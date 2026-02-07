from normalization.catalog import DEFAULT_CATALOG
from parsers.pdf_program import LeaseProgram
from validation.rules import validate_programs


def test_validation_rejects_outliers():
    program = LeaseProgram(
        make="Toyota",
        model="RAV4",
        trim="LE",
        msrp=32000,
        residual_percent=20,
        money_factor=0.02,
        term_months=36,
    )
    program.normalized = DEFAULT_CATALOG.normalize(program.make, program.model, program.trim)

    results = validate_programs([program])
    assert not results[0].is_valid
    assert len(results[0].issues) == 2


def test_validation_accepts_reasonable_values():
    program = LeaseProgram(
        make="Honda",
        model="Accord",
        trim="Touring",
        msrp=40000,
        residual_percent=60,
        money_factor=0.0009,
        term_months=36,
    )
    program.normalized = DEFAULT_CATALOG.normalize(program.make, program.model, program.trim)

    results = validate_programs([program])
    assert results[0].is_valid
    assert results[0].issues == []
