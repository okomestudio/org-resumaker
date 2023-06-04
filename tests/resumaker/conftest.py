import pytest
from . import data
from pathlib import Path


@pytest.fixture
def org_resume():
    return Path(data.__file__).parent / "fake_resume.org"
