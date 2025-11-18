#! /usr/bin/env python

from __future__ import annotations

from importlib.metadata import version
from pathlib import Path

from cyclopts import App

app = App(
    help_on_error=True,
    version=f"[magenta]genoray[/magenta] {version('genoray')}\n[cyan]genoray-cli[/cyan] {version('genoray-cli')}",
    version_format="rich",
    help="Tools for genoray, including SVAR files.",
)


@app.command
def index(source: Path):
    """Create a genoray index for a VCF or PGEN file."""
    from genoray import PGEN, VCF
    from genoray._utils import variant_file_type

    file_type = variant_file_type(source)
    if file_type == "vcf":
        vcf = VCF(source)
        vcf._write_gvi_index()
    elif file_type == "pgen":
        _ = PGEN(source)
    else:
        raise ValueError(f"Unsupported file type: {source}")


@app.command
def write(
    source: Path,
    out: Path,
    max_mem: str = "1g",
    overwrite: bool = False,
    dosages: bool | str | None = None,
) -> None:
    """
    Convert a VCF or PGEN file to a SVAR file.

    Parameters
    ----------
    source
        Path to the input VCF or PGEN file.
    out
        Path to the output SVAR file.
    max_mem
        Maximum memory to use for conversion e.g. 1g, 250 MB, etc.
    overwrite
        Whether to overwrite the output file if it exists.
    dosages
        Whether to write dosages. If :code:`source` is a PGEN, this must be a path to a PGEN of dosages.
        If :code:`source` is a VCF, this must be the name of the FORMAT field to use for dosages.
    """
    from genoray import PGEN, VCF, SparseVar
    from genoray._utils import variant_file_type

    file_type = variant_file_type(source)

    if dosages is None:
        with_dosages = False
    else:
        with_dosages = True

    if file_type == "vcf":
        if isinstance(dosages, bool):
            raise ValueError(
                "Dosages must be provided as a string for a VCF FORMAT field if the source is a VCF."
            )

        if dosages is not None and Path(dosages).exists():
            raise ValueError(
                "The `dosages` argument appears to be a path to an existing file, but VCF requires a FORMAT field name."
            )

        vcf = VCF(source, dosage_field=dosages)
        SparseVar.from_vcf(out, vcf, max_mem, overwrite, with_dosages=with_dosages)
    elif file_type == "pgen":
        if dosages is False:
            dosages = None
        elif dosages is True:
            raise ValueError(
                "Dosages must be provided as a path to a PGEN if source is a PGEN."
            )

        pgen = PGEN(source, dosage_path=dosages)
        SparseVar.from_pgen(out, pgen, max_mem, overwrite, with_dosages=with_dosages)
    else:
        raise ValueError(f"Unsupported file type: {source}")


if __name__ == "__main__":
    app()
