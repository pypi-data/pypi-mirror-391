from collections import namedtuple

INITIAL_URL = "https://progenomes.embl.de/data"

URLMapping = namedtuple("URLMapping", ["file_prefix", "filename", "filetype", "headers"])

URL_MAPPING = {
    "habitats-per-isolate": URLMapping(
        file_prefix="proGenomes3",
        filename="habitat_isolates",
        filetype="tab.bz2",
        headers=True,
    ),
    "habitats-per-speci-cluster": URLMapping(
        file_prefix="proGenomes3",
        filename="habitat_specI",
        filetype="tab.bz2",
        headers=True,
    ),
    "representatives-per-speci-cluster": URLMapping(
        file_prefix="proGenomes3",
        filename="representatives_for_each_specI",
        filetype="tsv.gz",
        headers=False,
    ),
    "speci-clustering-data": URLMapping(
        file_prefix="proGenomes3",
        filename="specI_clustering",
        filetype="tab.bz2",
        headers=False,
    ),
    "gtdb-taxonomy": URLMapping(
        file_prefix="proGenomes3",
        filename="specI_lineageGTDB",
        filetype="tab.bz2",
        headers=True,
    ),
    "highly-important-strains": URLMapping(
        file_prefix=None,
        filename="highly_important_strains",
        filetype="tab.bz2",
        headers=False,
    ),
    "mge-orfs": URLMapping(
        file_prefix="representatives",
        filename="mge_ORFS",
        filetype="tsv.bz2",
        headers=True,
    ),
    "mge-annotation": URLMapping(
        file_prefix="representatives",
        filename="mge_annotation",
        filetype="tsv.bz2",
        headers=True,
    ),
}


def get_url(item: str):
    try:
        mapping = URL_MAPPING[item]
    except KeyError as exc:
        raise ValueError(f"Item '{item}' not found in URL mapping.") from exc
    if mapping.file_prefix is None:
        path = f"{mapping.filename}.{mapping.filetype}"
    else:
        path = f"{mapping.file_prefix}_{mapping.filename}.{mapping.filetype}"
    return (f"{INITIAL_URL}/{path}", mapping.filetype)


def view(target):
    import polars as pl
    import pandas as pd
    url, filetype = get_url(target)
    if "tab.bz2" in filetype:
        return pl.from_pandas(pd.read_table(url))
    elif "tsv.bz2" in filetype:
        return pl.from_pandas(pd.read_csv(url, sep="\t", index_col=None), include_index=False)
    else:
        return pl.read_csv(url, separator="\t")
