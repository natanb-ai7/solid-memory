"""
PDF parser for lease program tables.

This module extracts tabular lease program data from PDFs using `pdfplumber`.
It converts rows into `LeaseProgram` instances that downstream normalization
and validation layers can consume.
"""
from dataclasses import dataclass, field
from importlib import import_module, util
from typing import Iterable, List, Sequence

from normalization.catalog import Catalog, NormalizedVehicle


def _require_dependency(module_name: str) -> None:
    if util.find_spec(module_name) is None:
        raise ImportError(
            f"The parser requires the optional dependency '{module_name}'. "
            "Install it to enable PDF extraction."
        )


@dataclass
class LeaseProgram:
    """Structured representation of a single lease program row."""

    make: str
    model: str
    trim: str
    msrp: float
    residual_percent: float
    money_factor: float
    term_months: int
    raw_row: Sequence[str] = field(default_factory=list)
    normalized: NormalizedVehicle | None = None


def _parse_numeric(value: str) -> float:
    cleaned = value.strip().replace("%", "").replace(",", "")
    if cleaned.endswith("mf"):
        cleaned = cleaned[:-2]
    return float(cleaned)


def _coerce_term(value: str) -> int:
    digits = "".join(ch for ch in value if ch.isdigit())
    return int(digits) if digits else 0


def _to_program(row: Sequence[str], catalog: Catalog) -> LeaseProgram:
    keys = ["make", "model", "trim", "msrp", "residual_percent", "money_factor", "term"]
    mapped = {key: row[idx] if idx < len(row) else "" for idx, key in enumerate(keys)}

    program = LeaseProgram(
        make=mapped["make"].strip(),
        model=mapped["model"].strip(),
        trim=mapped["trim"].strip(),
        msrp=_parse_numeric(mapped["msrp"] or "0"),
        residual_percent=_parse_numeric(mapped["residual_percent"] or "0"),
        money_factor=_parse_numeric(mapped["money_factor"] or "0"),
        term_months=_coerce_term(mapped["term"]),
        raw_row=row,
    )
    program.normalized = catalog.normalize(program.make, program.model, program.trim)
    return program


def parse_pdf_program(file_path: str, catalog: Catalog) -> List[LeaseProgram]:
    """
    Parse tabular lease program data from a PDF file.

    Parameters
    ----------
    file_path: str
        Path to the PDF containing program tables.
    catalog: Catalog
        Reference catalog used for normalization of make/model/trim.

    Returns
    -------
    List[LeaseProgram]
        A list of parsed lease program rows.
    """

    _require_dependency("pdfplumber")
    pdfplumber = import_module("pdfplumber")

    programs: List[LeaseProgram] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            for table in page.extract_tables():
                # assume the first row is a header row we can ignore
                body: Iterable[Sequence[str]] = table[1:] if table else []
                for row in body:
                    if not any(cell.strip() for cell in row):
                        continue
                    programs.append(_to_program(row, catalog))

    return programs
