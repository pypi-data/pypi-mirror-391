import pytest
import os
from pathlib import Path

@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "test_data"

@pytest.fixture
def sample_docx_path(test_data_dir):
    return test_data_dir / "sample_quality_standard.docx"
