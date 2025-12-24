"""
HTML parser for dynamic lease program tables.

Supports both static HTML content via BeautifulSoup and dynamic pages using
Playwright (when available). A lightweight fallback HTML parser is used when
BeautifulSoup is not installed so parsing can proceed in constrained
environments.
"""
from dataclasses import dataclass
from importlib import import_module, util
from typing import Iterable, List, Sequence
from xml.etree import ElementTree

from normalization.catalog import Catalog, NormalizedVehicle


def _require_bs4():
    if util.find_spec("bs4") is None:
        return None
    return import_module("bs4").BeautifulSoup


def _ensure_sequence(tags: Sequence[str] | str) -> Sequence[str]:
    if isinstance(tags, str):
        return [tags]
    return tags


class _ElementWrapper:
    def __init__(self, element: ElementTree.Element):
        self.element = element

    def find(self, tag: str):
        found = self.element.find(f".//{tag}")
        return _ElementWrapper(found) if found is not None else None

    def find_all(self, tags: Sequence[str] | str):
        matches = []
        for tag in _ensure_sequence(tags):
            matches.extend(self.element.findall(f".//{tag}"))
        return [_ElementWrapper(el) for el in matches]

    def get_text(self, strip: bool = False) -> str:
        text = "".join(self.element.itertext())
        return text.strip() if strip else text


class _FallbackSoup(_ElementWrapper):
    def __init__(self, html: str):
        root = ElementTree.fromstring(f"<root>{html}</root>")
        super().__init__(root)

    def find(self, tag: str):
        found = self.element.find(f".//{tag}")
        return _ElementWrapper(found) if found is not None else None

    def find_all(self, tags: Sequence[str] | str):
        matches = []
        for tag in _ensure_sequence(tags):
            matches.extend(self.element.findall(f".//{tag}"))
        return [_ElementWrapper(el) for el in matches]


@dataclass
class HtmlProgramRow:
    make: str
    model: str
    trim: str
    msrp: float
    residual_percent: float
    money_factor: float
    term_months: int
    normalized: NormalizedVehicle | None = None


def _parse_float(text: str) -> float:
    cleaned = text.strip().replace("%", "").replace(",", "")
    return float(cleaned)


def _parse_int(text: str) -> int:
    digits = "".join(ch for ch in text if ch.isdigit())
    return int(digits) if digits else 0


def _rows_from_soup(table) -> Iterable[List[str]]:
    for tr in table.find_all("tr"):
        cells = [cell.get_text(strip=True) for cell in tr.find_all(["td", "th"])]
        if cells and any(cells):
            yield cells


def parse_html_table(html: str, catalog: Catalog) -> List[HtmlProgramRow]:
    """Parse an HTML snippet containing a lease program table."""

    BeautifulSoup = _require_bs4()
    if BeautifulSoup:
        soup = BeautifulSoup(html, "html.parser")
    else:
        soup = _FallbackSoup(html)

    table = soup.find("table")
    if table is None:
        return []

    rows = list(_rows_from_soup(table))
    data_rows = rows[1:] if rows and rows[0][0].lower() in {"make", "model"} else rows

    programs: List[HtmlProgramRow] = []
    for row in data_rows:
        if len(row) < 7:
            continue
        program = HtmlProgramRow(
            make=row[0],
            model=row[1],
            trim=row[2],
            msrp=_parse_float(row[3]),
            residual_percent=_parse_float(row[4]),
            money_factor=_parse_float(row[5]),
            term_months=_parse_int(row[6]),
        )
        program.normalized = catalog.normalize(program.make, program.model, program.trim)
        programs.append(program)

    return programs


def fetch_dynamic_html(url: str, selector: str) -> str:
    """
    Fetch HTML from a dynamic page using Playwright.

    This helper keeps the dependency optional: Playwright is only imported
    when this function is invoked.
    """

    if util.find_spec("playwright") is None:
        raise ImportError("The Playwright dependency is required for dynamic HTML parsing.")

    playwright = import_module("playwright.sync_api")
    with playwright.sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(url)
        page.wait_for_selector(selector)
        html_content = page.inner_html(selector)
        browser.close()
        return html_content
