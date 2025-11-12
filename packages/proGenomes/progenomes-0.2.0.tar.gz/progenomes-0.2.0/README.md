# proGenomes-cli

proGenomes-cli is a command-line tool for exploring the [proGenomes](https://progenomes.embl.de) dataset of bacterial and archaeal genomes.

If you use this software in a publication please cite:

> Fullam, Anthony; Letunic, Ivica,; Maistrenko, Oleksandr; Castro, Alexandre A; Coelho, Luis Pedro; Grekova, Anastasia ; Schudoma, Christian; Khedkar, Supriya; Robbani, Shahriyar Mahdi; Kuhn, Michael; Schmidt, Thomas S. B; Bork, Peer; Mende, Daniel R. **proGenomes4: providing two million accurately and consistently annotated high-quality prokaryotic genomes.** in *Nucleic Acids Research*. (accepted)

## Installation

Clone this repository and install using `pip`:

```bash
pip install .
```

## Usage

After installation, the `progenomes` command provides access to several subcommands:

```bash
progenomes download <options>   # Download genome data
progenomes view <options>       # Inspect downloaded data
```

Refer to the built-in help for full details on available commands.

```bash
progenomes --help
```

## License

This project is licensed under the [MIT License](LICENSE).

