from pathlib import Path
from app.parsing import text_from_html, detect_loaner, extract_miles, extract_prices, extract_vin

FIXTURES = [
    "dealer1.html",
    "dealer2.html",
    "dealer3.html",
    "dealer4.html",
    "dealer5.html",
]


def test_parsing_fixtures():
    base = Path(__file__).parent / "fixtures"
    for fixture in FIXTURES:
        html = (base / fixture).read_text()
        text = text_from_html(html)
        is_loaner, _ = detect_loaner(text)
        miles = extract_miles(text)
        prices = extract_prices(text)
        vin = extract_vin(text)

        assert is_loaner is True
        assert miles is not None
        assert len(prices) >= 2
        if "dealer3" in fixture:
            assert vin is None
        else:
            assert vin is None or len(vin) == 17
