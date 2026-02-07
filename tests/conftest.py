import os
import sys
import tempfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from db.program_repository import ProgramRepository


@pytest.fixture()
def repo():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "programs.db")
        repository = ProgramRepository(db_path)
        repository.apply_migrations()
        yield repository
        repository.close()
