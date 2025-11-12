from collections import namedtuple
from tqdm import tqdm
import urllib.request
from typing import Union

GENOME_INITIAL_URL = "https://progenomes.embl.de/data"

UrlData = namedtuple(
    "UrlData", ["type", "server_prefix", "file_prefix", "filetype", "order"]
)

DatasetUrlData = namedtuple(
    "DatasetUrlData", ["file_prefix", "filename", "filetype", "headers"]
)

GENOME_URL_MAPPING = {
    "representative-genomes": UrlData(
        "representatives", "repGenomes", "progenomes3", "fasta.bz2", "target.type"
    ),
    "aquatic": UrlData(
        "aquatic", "habitats", "representatives", "fasta.gz", "type.target"
    ),
    "disease-associated": UrlData(
        "disease-associated",
        "habitats",
        "representatives",
        "fasta.gz",
        "type.target",
    ),
    "food-associated": UrlData(
        "food-associated", "habitats", "representatives", "fasta.gz", "type.target"
    ),
    "freshwater": UrlData(
        "freshwater", "habitats", "representatives", "fasta.gz", "type.target"
    ),
    "host-associated": UrlData(
        "host-associated", "habitats", "representatives", "fasta.gz", "type.target"
    ),
    "host-plant-associated": UrlData(
        "host-plant-associated",
        "habitats",
        "representatives",
        "fasta.gz",
        "type.target",
    ),
    "sediment-mud": UrlData(
        "sediment-mud", "habitats", "representatives", "fasta.gz", "type.target"
    ),
    "soil": UrlData("soil", "habitats", "representatives", "fasta.gz", "type.target"),
}


def _get_genome_url(target: str, component: str):
    mapping = GENOME_URL_MAPPING[target]
    if mapping.order == "type.target":
        return (
            f"{GENOME_INITIAL_URL}/{mapping.server_prefix}/{mapping.file_prefix}."
            f"{mapping.type.replace('-', '_')}.{component}.{mapping.filetype}"
        )
    else:
        return (
            f"{GENOME_INITIAL_URL}/{mapping.server_prefix}/{mapping.file_prefix}."
            f"{component}.{mapping.type.replace('-', '_')}.{mapping.filetype}"
        )


def download_genomes(target: str, components: list[str]):
    ''' Download genome files by their target name and components. '''
    pbar = tqdm(components)
    for t in pbar:
        pbar.set_description(f"Downloading {t}")
        url = _get_genome_url(target, t)
        urllib.request.urlretrieve(url, url.split("/")[-1])


DATASET_INITIAL_URL = "https://progenomes.embl.de/data"

DATASET_URL_MAPPING = {
    "habitats-per-isolate": DatasetUrlData(
        "proGenomes3", "habitat_isolates", "tab.bz2", True
    ),
    "habitats-per-speci-cluster": DatasetUrlData(
        "proGenomes3", "habitat_specI", "tab.bz2", True
    ),
    "representatives-per-speci-cluster": DatasetUrlData(
        "proGenomes3", "representatives_for_each_specI", "tsv.gz", False
    ),
    "marker-genes": DatasetUrlData("proGenomes3", "markerGenes", "tar.gz", None),
    "speci-clustering-data": DatasetUrlData(
        "proGenomes3", "specI_clustering", "tab.bz2", False
    ),
    "gtdb-taxonomy": DatasetUrlData(
        "proGenomes3", "specI_lineageGTDB", "tab.bz2", True
    ),
    "highly-important-strains": DatasetUrlData(
        None, "highly_important_strains", "tab.bz2", False
    ),
    "excluded-genomes": DatasetUrlData(
        "proGenomes3", "excluded_genomes", "txt.bz2", None
    ),
    "mge-orfs": DatasetUrlData("representatives", "mge_ORFS", "tsv.bz2", True),
    "mge-annotation": DatasetUrlData(
        "representatives", "mge_annotation", "tsv.bz2", True
    ),
    "gecco-gene-clusters": DatasetUrlData(
        "proGenomes3", "gecco_clusters", "gbk.gz", None
    ),
}


def _get_dataset_url(item: str):
    mapping = DATASET_URL_MAPPING[item]
    if mapping.file_prefix is None:
        return f"{DATASET_INITIAL_URL}/{mapping.filename}.{mapping.filetype}"
    else:
        return (
            f"{DATASET_INITIAL_URL}/{mapping.file_prefix}_{mapping.filename}."
            f"{mapping.filetype}"
        )


def download_dataset(target: str):
    ''' Download a dataset by its target name. '''
    url = _get_dataset_url(target)
    urllib.request.urlretrieve(url, url.split("/")[-1])
