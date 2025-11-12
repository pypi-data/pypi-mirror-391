from progenomes.download import download_dataset, download_genomes
from progenomes.view import view
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="""
    Interact with the proGenomes[1] database.

    Anthony Fullam, Ivica Letunic, Thomas S B Schmidt, Quinten R Ducarmon,
    Nicolai Karcher, Supriya Khedkar, Michael Kuhn, Martin Larralde, Oleksandr
    M Maistrenko, Lukas Malfertheiner, Alessio Milanese, Joao Frederico Matias
    Rodrigues, Claudia Sanchis-López, Christian Schudoma, Damian Szklarczyk,
    Shinichi Sunagawa, Georg Zeller, Jaime Huerta-Cepas, Christian von Mering,
    Peer Bork, Daniel R Mende, proGenomes3: approaching one million accurately
    and consistently annotated high-quality prokaryotic genomes, Nucleic
    Acids Research, Volume 51, Issue D1, 6 January 2023, Pages D760–D766,
    https://doi.org/10.1093/nar/gkac1078
    """,
        formatter_class=argparse.RawTextHelpFormatter,
    )
    subparsers = parser.add_subparsers(help="subcommand help", dest="action")
    parser_download = subparsers.add_parser(
        "download", help="download data from an item"
    )
    subparser_download = parser_download.add_subparsers(help="subsubcommand help", dest="download_target")
    parser_download_genome = subparser_download.add_parser("genomes", help="download genome set")
    parser_download_genome.add_argument(
        dest="target",
        choices=[
            "representative-genomes",
            "aquatic",
            "disease-associated",
            "food-associated",
            "host-associated",
            "host-plant-associated",
            "freshwater",
            "sediment-mud",
            "soil",
        ],
        action="store",
        help="""Representative genome set to download. Available options:
        Representative genomes, Aquatic, Disease associated, Food associated,
        Freshwater, Host associated, Host plant associated, Sediment mud, Soil.""",
    )
    parser_download_genome.add_argument(
        "-c", "--contigs", dest="contigs", help="Contigs", action="store_true"
    )
    parser_download_genome.add_argument(
        "-g", "--genes", dest="genes", help="Genes", action="store_true"
    )
    parser_download_genome.add_argument(
        "-p", "--proteins", dest="proteins", help="Proteins", action="store_true"
    )
    parser_download_genome.add_argument(
        "-a", "--all", dest="all", help="All", action="store_true"
    )
    parser_download_dataset = subparser_download.add_parser("datasets", help="download genome set")
    parser_download_dataset.add_argument(
        dest="target",
        choices=[
            "habitats-per-isolate",
            "habitats-per-speci-cluster",
            "representatives-per-speci-cluster",
            "marker-genes",
            "speci-clustering-data",
            "gtdb-taxonomy",
            "highly-important-strains",
            "excluded-genomes",
            "mge-orfs",
            "mge-annotation",
            "gecco-gene-clusters",
        ],
        action="store",
        help="""Dataset to download. Available options:
        Habitats per isolate, Habitats per specI cluster, Representatives per specI cluster,
        Marker genes, SpecI clustering data, GTDB taxonomy, Highly important strains,
        Excluded genomes, MGE ORFs, MGE annotation, GECCO biosynthetic gene clusters (GenBank records)""",
    )
    parser_view = subparsers.add_parser("view", help="view an item")
    parser_view.add_argument(
        dest="target",
        choices=[
            "habitats-per-isolate",
            "habitats-per-speci-cluster",
            "representatives-per-speci-cluster",
            "speci-clustering-data",
            "gtdb-taxonomy",
            "highly-important-strains",
            "mge-orfs",
            "mge-annotation",
        ],
        action="store",
        help="""Dataset to view. Available options:
        Habitats per isolate, Habitats per specI cluster, Representatives per specI cluster,
        SpecI clustering data, GTDB taxonomy, Highly important strains,
        MGE ORFs, MGE annotation""",
    )

    args = parser.parse_args()
    if args.action == "download":
        items_to_download = []
        if args.download_target == "genomes":
            if not args.contigs and not args.genes and not args.proteins:
                args.all = True
            if args.contigs:
                items_to_download.append("contigs")
            if args.genes:
                items_to_download.append("genes")
            if args.proteins:
                items_to_download.append("proteins")
            if args.all:
                items_to_download = ["genes", "contigs", "proteins"]
            download_genomes(args.target, items_to_download)
        else:
            items_to_download = None
            download_dataset(args.target)
    elif args.action == "view":
        item_to_view = args.target
        print(view(item_to_view))


if __name__ == "__main__":
    main()
