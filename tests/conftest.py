from __future__ import annotations

from pathlib import Path

import pytest

from engine.db import init_db
from engine.ingest import ingest_directory


@pytest.fixture(scope="session", autouse=True)
def sample_db(tmp_path_factory):
    data_dir = Path("sample_data")
    init_db()
    ingest_directory(data_dir)
    yield
