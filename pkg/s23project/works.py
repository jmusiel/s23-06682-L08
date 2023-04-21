"""Module containing Works class."""
import time
import base64
import requests
from IPython.display import display, HTML
import bibtexparser


class Works:
    """Describes a work queried from Open Alex."""

    def __init__(self, oaid):
        """Construct Works class."""
        self.oaid = oaid
        self.req = requests.get(f"https://api.openalex.org/works/{oaid}", timeout=10)
        self.data = self.req.json()

    def __str__(self):
        """Replace string method with repr method."""
        return self.__repr__()

    def __repr__(self):
        """Replace repr method to display all information about work."""
        _authors = [au["author"]["display_name"] for au in self.data["authorships"]]
        if len(_authors) == 1:
            authors = _authors[0]
        elif len(_authors) == 0:
            authors = "(No authors)"
        else:
            authors = ", ".join(_authors[0:-1]) + " and " + _authors[-1]

        title = self.data["title"]
        # journal = self.data["host_venue"]["display_name"]
        volume = self.data["biblio"]["volume"]

        issue = self.data["biblio"]["issue"]
        if issue is None:
            issue = ", "
        else:
            issue = ", " + issue

        pages = "-".join(
            [
                self.data["biblio"].get("first_page", "") or "",
                self.data["biblio"].get("last_page", "") or "",
            ]
        )
        year = self.data["publication_year"]
        citedby = self.data["cited_by_count"]

        open_alex_id = self.data["id"]
        return_string = f"\n{authors}, {title}, {volume}{issue}{pages}, ({year}), "
        return_string += f'{self.data["doi"]}. cited by: {citedby}. {open_alex_id}'
        return return_string

    @property
    def ris(self):
        """Return RIS citation data."""
        fields = []
        if self.data["type"] == "journal-article":
            fields += ["TY  - JOUR"]
        else:
            raise ValueError("Unsupported type {self.data['type']}")

        for author in self.data["authorships"]:
            fields += [f'AU  - {author["author"]["display_name"]}']

        fields += [f'PY  - {self.data["publication_year"]}']
        fields += [f'TI  - {self.data["title"]}']
        fields += [f'JO  - {self.data["host_venue"]["display_name"]}']
        fields += [f'VL  - {self.data["biblio"]["volume"]}']

        if self.data["biblio"]["issue"]:
            fields += [f'IS  - {self.data["biblio"]["issue"]}']

        fields += [f'SP  - {self.data["biblio"]["first_page"]}']
        fields += [f'EP  - {self.data["biblio"]["last_page"]}']
        fields += [f'DO  - {self.data["doi"]}']
        fields += ["ER  -"]

        ris = "\n".join(fields)
        ris64 = base64.b64encode(ris.encode("utf-8")).decode("utf8")
        uri = f'<pre>{ris}<pre><br><a href="data:text/plain;base64,'
        uri += f'{ris64}" download="ris">Download RIS</a>'

        display(HTML(uri))
        return ris

    def related_works(self):
        """Get list of related works."""
        rworks = []
        for rw_url in self.data["related_works"]:
            rwork = Works(rw_url)
            rworks += [rwork]
            time.sleep(0.101)
        return rworks

    def citing_works(self):
        """Get list of citing works."""
        cworks = []
        cw_json = requests.get(self.data["cited_by_api_url"], timeout=10).json()
        for result in cw_json["results"]:
            citing_work = Works(result["id"])
            cworks.append(citing_work)
            time.sleep(0.2)
        return cworks

    def references(self):
        """Get list of references."""
        refs = []
        for refurl in self.data["referenced_works"]:
            refwork = Works(refurl)
            refs.append(refwork)
            time.sleep(0.2)
        return refs

    @property
    def bibtex(
        self,
        abstract=False,
        author=True,
        title=True,
        journal=True,
        volume=True,
        number=True,
        pages=True,
        year=True,
        doi=True,
        url=True,
        eprint=True,
    ):
        """Return parsed bibtex string."""
        bib = bibtexparser.bibdatabase.BibDatabase()

        # Get abstract from inverted index
        inverted_index = self.data["abstract_inverted_index"]
        postings = [
            (doc_id, term)
            for term, doc_ids in inverted_index.items()
            for doc_id in doc_ids
        ]
        postings.sort()
        abstract_string = ""
        prev_doc_id = -1
        for doc_id, term in postings:
            if doc_id != prev_doc_id:
                abstract_string += " " * (doc_id - prev_doc_id) + term
                prev_doc_id = doc_id
            else:
                abstract_string += " " + term
        abstract_string = abstract_string.strip()

        # create bib dictionary to feed into parser to dump to string
        bib_dict = {}
        bib_dict["ID"] = [
            a["author"]["display_name"] for a in self.data["authorships"]
        ][0].split(" ")[-1] + str(self.data["publication_year"])
        bib_dict["ENTRYTYPE"] = self.data["type"]

        if abstract:
            bib_dict["abstract"] = abstract_string
        if author:
            bib_dict["author"] = ", ".join(
                [a["author"]["display_name"] for a in self.data["authorships"]]
            )
        if title:
            bib_dict["title"] = self.data["title"]
        if journal:
            bib_dict["journal"] = self.data["host_venue"]["display_name"]
        if volume:
            bib_dict["volume"] = self.data["biblio"]["volume"]
        if number:
            bib_dict["number"] = self.data["biblio"]["issue"]
        if pages:
            bib_dict["pages"] = (
                self.data["biblio"]["first_page"]
                + "-"
                + self.data["biblio"]["last_page"]
            )
        if year:
            bib_dict["year"] = str(self.data["publication_year"])
        if doi:
            bib_dict["doi"] = self.data["doi"].replace("https://doi.org/", "")
        if url:
            bib_dict["URL"] = self.data["primary_location"]["landing_page_url"]
        if eprint:
            bib_dict["eprint"] = self.data["primary_location"]["landing_page_url"]
        bib.entries = [bib_dict]
        return bibtexparser.dumps(bib)
