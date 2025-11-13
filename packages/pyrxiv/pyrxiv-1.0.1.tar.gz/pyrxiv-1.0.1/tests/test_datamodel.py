import datetime
import io

import h5py
import pytest

from pyrxiv.datamodel import ArxivPaper
from tests.conftest import generate_arxiv_paper


def test_to_from_hdf5_roundtrip(tmp_path):
    sample_paper = generate_arxiv_paper()
    # create an in-memory buffer to avoid disk writes
    buffer = io.BytesIO()

    # write to HDF5
    with h5py.File(buffer, "w") as h5f:
        sample_paper.to_hdf5(h5f)

    # important: reset buffer cursor for reading
    buffer.seek(0)

    # write buffer to tmp_path just to satisfy Path input of from_hdf5
    # -> you can patch from_hdf5 later to also accept file-like objects
    hdf5_path = tmp_path / f"{sample_paper.id}.h5"
    with open(hdf5_path, "wb") as f:
        f.write(buffer.getvalue())

    # now load back
    paper2 = ArxivPaper.from_hdf5(hdf5_path)

    # compare
    assert paper2.id == sample_paper.id
    assert paper2.title == sample_paper.title
    assert paper2.summary == sample_paper.summary
    assert [a.name for a in paper2.authors] == [a.name for a in sample_paper.authors]
    assert paper2.text == sample_paper.text
    assert paper2.categories == sample_paper.categories
    assert paper2.n_pages == sample_paper.n_pages
    assert isinstance(paper2.updated, datetime.datetime)
