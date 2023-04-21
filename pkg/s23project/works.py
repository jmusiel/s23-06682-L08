"""Module containing Works class."""
import time
import base64
import requests
import matplotlib.pyplot as plt
from IPython.core.pylabtools import print_figure
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

    def _repr_markdown_(self):
        _authors = [
            f'[{au["author"]["display_name"]}]({au["author"]["id"]})'
            for au in self.data["authorships"]
        ]
        if len(_authors) == 1:
            authors = _authors[0]
        else:
            authors = ", ".join(_authors[0:-1]) + " and " + _authors[-1]

        title = self.data["title"]

        journal = f"[{self.data['host_venue']['display_name']}]({self.data['host_venue']['id']})"
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

        # Citation counts by year
        years = [e["year"] for e in self.data["counts_by_year"]]
        counts = [e["cited_by_count"] for e in self.data["counts_by_year"]]

        fig, ax_0 = plt.subplots()
        ax_0.bar(years, counts)
        ax_0.set_xlabel("year")
        ax_0.set_ylabel("citation count")
        data = print_figure(fig, "png")  # save figure in string
        plt.close(fig)

        b64 = base64.b64encode(data).decode("utf8")
        citefig = f"![img](data:image/png;base64,{b64})"

        return_string = (
            f"{authors}, *{title}*, **{journal}**, {volume}{issue}{pages}, ({year}), "
        )
        return_string += (
            f'{self.data["doi"]}. cited by: {citedby}. [Open Alex]({open_alex_id})'
        )
        return_string += "<br>" + citefig
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
    def bibtex(self):
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
        bib_dict = {
            "journal": self.data["host_venue"]["display_name"],
            # 'comments': '',
            "pages": self.data["biblio"]["first_page"]
            + "-"
            + self.data["biblio"]["last_page"],
            "abstract": abstract_string,
            "title": self.data["title"],
            "year": str(self.data["publication_year"]),
            "volume": self.data["biblio"]["volume"],
            "ID": [a["author"]["display_name"] for a in self.data["authorships"]][
                0
            ].split(" ")[-1]
            + str(self.data["publication_year"]),
            "author": ", ".join(
                [a["author"]["display_name"] for a in self.data["authorships"]]
            ),
            # 'keyword': '',
            "ENTRYTYPE": self.data["type"],
        }
        bib.entries = [bib_dict]
        return bibtexparser.dumps(bib)
