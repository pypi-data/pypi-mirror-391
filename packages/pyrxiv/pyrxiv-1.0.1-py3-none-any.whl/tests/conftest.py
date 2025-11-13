import datetime
import os
from pathlib import Path

import pytest

from pyrxiv.datamodel import ArxivPaper, Author
from pyrxiv.logger import log_storage

if os.getenv("_PYTEST_RAISE", "0") != "0":

    @pytest.hookimpl(tryfirst=True)
    def pytest_exception_interact(call):
        raise call.excinfo.value

    @pytest.hookimpl(tryfirst=True)
    def pytest_internalerror(excinfo):
        raise excinfo.value


@pytest.fixture(autouse=True)
def cleared_log_storage():
    """Fixture to clear the log storage before each test."""
    log_storage.clear()
    yield log_storage


def generate_arxiv_paper(id: str = "1234.5678v1"):
    return ArxivPaper(
        id=id,
        url=f"http://arxiv.org/abs/{id}",
        pdf_url=f"http://arxiv.org/pdf/{id}",
        updated=datetime.datetime(2025, 2, 21, 10, 0, 0),
        published=datetime.datetime(2025, 2, 20, 12, 0, 0),
        title="A test paper",
        summary="This is a test summary",
        authors=[Author(name="Alice"), Author(name="Bob")],
        comment="Some comment",
        n_pages=12,
        n_figures=3,
        categories=["cond-mat.str-el", "cond-mat.mtrl-sci"],
        pdf_loader="pypdf",
        text="This is the body of the paper.",
    )
