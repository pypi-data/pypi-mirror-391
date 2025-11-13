import logging
import subprocess
from pathlib import Path

LOG = logging.getLogger(__name__)

def _run(argv):
    LOG.debug("plink2 argv: %s", " ".join(argv))
    cp = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    LOG.debug("plink2 out:\n%s", cp.stdout)
    cp.check_returncode()


def make_bed(prefix: Path, plink2: str = "plink2"):
    """
    Create BED/BIM/FAM from <prefix>.ped/.map using Hao's filters.

    Args:
        prefix: Path prefix (without extension) for .ped/.map and .bed/.bim/.fam.
        plink2: plink2 executable.

    Returns:
        None.
    """
    _run([plink2, "--pedmap", str(prefix),
          "--make-bed",
          "--geno", "0.1",
          "--mind", "0.1",
          "--out", str(prefix)])


def make_rel_square(prefix: Path, plink2: str = "plink2", out_prefix: Path | None = None):
    """
    Build a square kinship (.rel) from the same sample set as BED/BIM/FAM.

    Args:
        prefix: Path prefix used by make_bed (bfile prefix).
        plink2: plink2 executable.
        out_prefix: Optional output prefix; defaults to f"{prefix}.kin".

    Returns:
        None.
    """
    outp = str(out_prefix) if out_prefix else f"{prefix}.kin"
    _run([plink2, "--bfile", str(prefix), "--make-rel", "square", "--out", outp])


def generate_bed_bim_fam(*a, **k):
    """placeholder for old versions
    """

def calculate_kinship_matrix(*a, **k):
    """placeholder for old versions
    """