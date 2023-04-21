"""Pytest other methods for retrieving other works from works class."""
from s23project import Works


CITING_LEN = 18
REFS_LEN = 18
RELATED_LEN = 10


def test_citing():
    """Test retrieving citing works."""
    work = Works("https://doi.org/10.1021/acscatal.5b00538")
    assert CITING_LEN == len(work.citing_works())


def test_refs():
    """Test retrieving referenced works."""
    work = Works("https://doi.org/10.1021/acscatal.5b00538")
    assert REFS_LEN == len(work.references())


def test_related():
    """Test retrieving related works."""
    work = Works("https://doi.org/10.1021/acscatal.5b00538")
    assert RELATED_LEN == len(work.related_works())
