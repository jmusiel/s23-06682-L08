#!/usr/bin/env python
"""Main method to print bibtex or ris for a given Open Alex url."""
import argparse
from s23project.works import Works


def main(args):
    """Print the bibtex or ris entry for the given url."""
    url = args.url
    entry_type = args.entrytype

    work = Works(url)

    if entry_type == "bibtex":
        print(work.bibtex)
    elif entry_type == "ris":
        print(work.ris)
    else:
        raise ValueError(
            "Inappropraite entry type provided, please provide either 'bibtex' or 'ris'."
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="a command line utility to print out the RIS"
        + " or the bibtex entry for a particular paper"
    )
    parser.add_argument(
        "-u",
        "--url",
        type=str,
        required=True,
        help="url linking to openalex api for the paper you want to print the entry",
    )
    parser.add_argument(
        "-e",
        "--entrytype",
        type=str,
        required=True,
        help="type of entry (bibtex or ris) you wish to print",
    )
    parsed_args = parser.parse_args()
    main(parsed_args)
