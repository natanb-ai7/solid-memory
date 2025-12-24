from normalization.catalog import DEFAULT_CATALOG
from parsers.html_table import parse_html_table


def test_parse_static_html_table():
    html = """
    <table>
        <tr><th>Make</th><th>Model</th><th>Trim</th><th>MSRP</th><th>Residual</th><th>MF</th><th>Term</th></tr>
        <tr><td>Toyota</td><td>Camry</td><td>XSE</td><td>30000</td><td>60%</td><td>0.0008</td><td>36</td></tr>
    </table>
    """
    results = parse_html_table(html, DEFAULT_CATALOG)
    assert len(results) == 1
    assert results[0].normalized is not None
    assert results[0].normalized.model == "camry"
