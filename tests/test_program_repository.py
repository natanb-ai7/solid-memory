from db.program_repository import Program, ProgramRepository


def test_upsert_inserts_new_program(repo: ProgramRepository):
    program = Program(
        make="Acme",
        model="RoadRunner",
        model_year=2024,
        term_months=36,
        mileage=12000,
        region="Southwest",
        effective_from="2024-01-01",
        effective_to="2024-03-31",
        program_name="Winter Promo",
        apr=1.9,
        residual_value=55.0,
        notes="Initial release",
    )

    saved = repo.upsert_program(program)
    fetched = repo.get_program(id=saved.id)

    assert saved.id is not None
    assert fetched is not None
    assert fetched.make == "Acme"
    assert fetched.apr == 1.9
    assert fetched.notes == "Initial release"


def test_upsert_updates_existing_program(repo: ProgramRepository):
    base_program = Program(
        make="Acme",
        model="RoadRunner",
        model_year=2024,
        term_months=36,
        mileage=12000,
        region="Southwest",
        effective_from="2024-01-01",
        effective_to="2024-03-31",
        program_name="Winter Promo",
        apr=1.9,
        residual_value=55.0,
        notes="Initial release",
    )
    repo.upsert_program(base_program)

    updated = Program(
        make="Acme",
        model="RoadRunner",
        model_year=2024,
        term_months=36,
        mileage=12000,
        region="Southwest",
        effective_from="2024-01-01",
        effective_to="2024-03-31",
        program_name="Spring Refresh",
        apr=1.5,
        residual_value=58.0,
        notes="Updated terms",
    )
    saved = repo.upsert_program(updated)

    assert saved.program_name == "Spring Refresh"
    assert saved.apr == 1.5
    assert saved.residual_value == 58.0
    assert saved.notes == "Updated terms"

    retrieved = repo.get_program(
        make="Acme",
        model="RoadRunner",
        model_year=2024,
        term_months=36,
        mileage=12000,
        region="Southwest",
        effective_from="2024-01-01",
        effective_to="2024-03-31",
    )
    assert retrieved is not None
    assert retrieved.program_name == "Spring Refresh"
    assert retrieved.apr == 1.5


def test_list_programs_returns_all(repo: ProgramRepository):
    programs = [
        Program(
            make="Acme",
            model="RoadRunner",
            model_year=2024,
            term_months=36,
            mileage=12000,
            region="Southwest",
            effective_from="2024-01-01",
            effective_to="2024-03-31",
            program_name="Winter Promo",
        ),
        Program(
            make="Acme",
            model="RoadRunner",
            model_year=2024,
            term_months=24,
            mileage=10000,
            region="Northwest",
            effective_from="2024-02-01",
            effective_to="2024-04-30",
            program_name="Lease Special",
        ),
    ]

    for program in programs:
        repo.upsert_program(program)

    retrieved = repo.list_programs()
    assert len(retrieved) == 2
    models = {(p.term_months, p.region) for p in retrieved}
    assert models == {(36, "Southwest"), (24, "Northwest")}
