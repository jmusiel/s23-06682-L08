"""Pytest bibtex formatting from works class."""
from s23project import Works


REF_BIBTEX = """@journal-article{Kitchin2015,
 URL = {https://doi.org/10.1021/acscatal.5b00538},
 author = {John R. Kitchin},
 doi = {10.1021/acscatal.5b00538},
 eprint = {https://doi.org/10.1021/acscatal.5b00538},
 journal = {ACS Catalysis},
 number = {6},
 pages = {3894-3899},
 title = {Examples of Effective Data Sharing in Scientific Publishing},
 volume = {5},
 year = {2015}
}
"""


def test_bibtex():
    """Test bibtex formatting from Works class."""
    work = Works("https://doi.org/10.1021/acscatal.5b00538")
    assert REF_BIBTEX == work.bibtex
