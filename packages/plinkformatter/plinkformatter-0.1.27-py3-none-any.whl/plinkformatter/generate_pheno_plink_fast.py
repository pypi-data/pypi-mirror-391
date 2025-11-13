#!/usr/bin/env python3
"""
Streaming generator of per-animal, sex-split PLINK files (NON_DO), mirroring Hao's pipeline.

Writes, for each measure×sex:
  <outdir>/<measnum>.<sex>.ped
  <outdir>/<measnum>.<sex>.map
  <outdir>/<measnum>.<sex>.pheno  (columns: FID IID zscore value)
Then runs plink2 to produce:
  <outdir>/<measnum>.<sex>.bed/.bim/.fam
  <outdir>/<measnum>.<sex>.kin.rel (.rel.id is auto, no header)

Behavior:
- Never loads the source PED into memory. Streams and replicates rows per animal.
- Uses zscore as phenotype, exactly like Hao.
- No --keep anywhere; BED/FAM/KIN derive from the same prefix -> order matches PHENO.
"""

from __future__ import annotations
import argparse
import logging
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd

LOG = logging.getLogger("gen_pheno_fast")
logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")


# --------------------------- PLINK helpers ---------------------------

def run_plink2(argv: List[str]) -> None:
    """
    Run plink2 and raise on error.

    Args:
        argv: Full argument vector including the 'plink2' binary.

    Returns:
        None. Raises on non-zero exit.

    Raises:
        subprocess.CalledProcessError: if plink2 exits non-zero.
    """
    LOG.debug("plink2 argv: %s", " ".join(argv))
    cp = subprocess.run(argv, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    LOG.debug("plink2 output:\n%s", cp.stdout)
    cp.check_returncode()


def copy_map(src: Path, dst: Path) -> None:
    """
    Copy a MAP file verbatim.

    Args:
        src: Path to source .map.
        dst: Path to destination .map.

    Returns:
        None.
    """
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dst)


# --------------------------- Core streaming logic ---------------------------

def build_strain_to_animals(
    pheno_df: pd.DataFrame,
    sex_label: str,
) -> Dict[str, List[Tuple[str, float, float]]]:
    """
    Construct mapping strain -> [(animal_id, zscore, value)] for a given sex.

    Args:
        pheno_df: DataFrame for one measure; must include columns:
                  'strain','sex','animal_id','zscore','value'.
                  'strain' should be raw (spaces allowed; we normalize here).
        sex_label: 'm' or 'f'.

    Returns:
        Dict[str, List[(animal_id, zscore, value)]], with strain keys normalized
        by removing spaces to match PED FID naming in Hao's pipeline.
    """
    if sex_label not in ("m", "f"):
        raise ValueError("sex_label must be 'm' or 'f'.")

    df = pheno_df.loc[pheno_df["sex"] == sex_label].copy()
    if df.empty:
        return {}

    # Normalize to match Hao: remove spaces from strain names
    df["strain"] = df["strain"].astype(str).str.replace(" ", "", regex=False)

    # Ensure required types
    df["animal_id"] = df["animal_id"].astype(str)
    df["zscore"] = pd.to_numeric(df["zscore"], errors="coerce")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Drop rows without a usable zscore/value
    df = df.dropna(subset=["zscore", "value"])

    m: Dict[str, List[Tuple[str, float, float]]] = {}
    for strain, g in df.groupby("strain", sort=False):
        m[strain] = list(zip(g["animal_id"].tolist(),
                             g["zscore"].astype(float).tolist(),
                             g["value"].astype(float).tolist()))
    return m


def stream_write_ped_and_pheno(
    src_ped: Path,
    out_ped: Path,
    out_pheno: Path,
    sex_label: str,
    strain_to_animals: Dict[str, List[Tuple[str, float, float]]],
) -> int:
    """
    Stream the source PED and write per-animal PED + PHENO aligned, for one sex.

    Args:
        src_ped: Path to the combined grid .ped (strain-level genotypes).
        out_ped: Destination per-animal .ped for this measure×sex.
        out_pheno: Destination .pheno (FID IID zscore value), aligned to out_ped.
        sex_label: 'm' or 'f'.
        strain_to_animals: mapping strain -> list of (animal_id, zscore, value).

    Returns:
        int: number of per-animal rows written.

    Raises:
        ValueError: on malformed PED rows (<7 columns).
    """
    sex_code = "1" if sex_label == "m" else "2"
    out_ped.parent.mkdir(parents=True, exist_ok=True)
    out_pheno.parent.mkdir(parents=True, exist_ok=True)

    n_written = 0
    with src_ped.open("r") as fin, out_ped.open("w") as ped_out, out_pheno.open("w") as phe_out:
        for line in fin:
            if not line.strip():
                continue
            parts = line.rstrip("\n").split()
            if len(parts) < 7:
                raise ValueError(f"Malformed PED row with <7 fields: {parts[:7]}")

            # PED head: FID IID PID MID SEX PHE GENOS...
            fid = parts[0].replace("?", "")
            pid, mid = parts[2], parts[3]
            genos = parts[6:]

            animals = strain_to_animals.get(fid)
            if not animals:
                continue

            for animal_id, zscore, raw_value in animals:
                iid = f"{fid}__{animal_id}"
                head = [fid, iid, pid, mid, sex_code, f"{zscore:g}"]
                ped_out.write(" ".join(head + genos) + "\n")
                phe_out.write(f"{fid} {iid} {zscore:g} {raw_value:g}\n")
                n_written += 1

    return n_written


def build_measure_sex(
    src_ped: Path,
    src_map: Path,
    pheno_df: pd.DataFrame,
    measure: int,
    sex_label: str,
    outdir: Path,
    plink2_bin: str,
) -> None:
    """
    Produce PED/MAP/PHENO for measure×sex, then run plink2 to make BED/BIM/FAM and KIN.

    Args:
        src_ped: Path to combined grid .ped (strain-level).
        src_map: Path to combined grid .map.
        pheno_df: DataFrame filtered to this measure (columns: 'strain','sex','animal_id','zscore','value').
        measure: Measure number (int).
        sex_label: 'm' or 'f'.
        outdir: Output directory (created if missing).
        plink2_bin: plink2 executable.

    Returns:
        None. Writes files to disk.

    Raises:
        RuntimeError: if BED/BIM/FAM creation or kinship fails.
    """
    s2a = build_strain_to_animals(pheno_df, sex_label)
    if not s2a:
        LOG.info("measure %s sex %s: no usable samples; skipping", measure, sex_label)
        return

    prefix = outdir / f"{int(measure)}.{sex_label}"
    ped_out = prefix.with_suffix(".ped")
    map_out = prefix.with_suffix(".map")
    phe_out = prefix.with_suffix(".pheno")

    LOG.info("Streaming PED -> %s and %s", ped_out.name, phe_out.name)
    n = stream_write_ped_and_pheno(src_ped, ped_out, phe_out, sex_label, s2a)
    LOG.info("Samples written: %d", n)

    LOG.info("Copying MAP -> %s", map_out.name)
    copy_map(src_map, map_out)

    # Hao's flags: --geno 0.1 --mind 0.1 (no --maf, no --chr)
    LOG.info("plink2 --make-bed on %s", prefix.name)
    run_plink2([
        plink2_bin, "--pedmap", str(prefix),
        "--make-bed",
        "--geno", "0.1",
        "--mind", "0.1",
        "--out", str(prefix),
    ])

    LOG.info("plink2 --make-rel square on %s", prefix.name)
    run_plink2([
        plink2_bin, "--bfile", str(prefix),
        "--make-rel", "square",
        "--out", str(prefix) + ".kin",
    ])

    LOG.info("Done: %s (N=%d)", prefix.name, n)

# --------------------------- Entrypoint ---------------------------
def fast_prepare_pylmm_inputs(
    ped_file: str,
    map_file: str,
    measure_ids_directory: str,
    measure_id_tokens: list[str],
    output_folder: str,
    ncore: int = 4,
    plink2_path: str = "plink2",
) -> None:
    """
    Temporal-compatible entrypoint. Mirrors Hao:
      - Uses CSV zscore as phenotype (no extra transforms).
      - Streams the grid .ped, replicates per-animal rows, sex-split.
      - Builds BED/BIM/FAM and kin (.rel) from the same prefix (no --keep).
      - Writes files named <measure>.<sex>.* in output_folder.

    Args:
        ped_file: path to the combined grid PED (strain-level)
        map_file: path to the combined grid MAP
        measure_ids_directory: directory containing <measure>_<panel>.csv
        measure_id_tokens: e.g. ["40701_NON_DO"], we parse measure as int before the '_'
        output_folder: where to write outputs
        ncore: unused here (kept for API parity)
        plink2_path: plink2 binary

    Returns:
        None. Raises on IO/plink errors.
    """
    from pathlib import Path
    import os
    import pandas as pd

    outdir = Path(output_folder)
    outdir.mkdir(parents=True, exist_ok=True)

    for token in measure_id_tokens:
        csv_path = Path(measure_ids_directory) / f"{token}.csv"
        if not csv_path.exists():
            raise FileNotFoundError(f"phenotype CSV not found: {csv_path}")

        # Measure number is the integer before the first underscore in the token
        try:
            measure_num = int(str(token).split("_", 1)[0])
        except Exception:
            raise ValueError(f"Cannot parse measure number from token: {token}")

        # Small CSV -> pandas is fine
        ph = pd.read_csv(csv_path, dtype={"measnum": int, "animal_id": str})

        # Minimal column check
        need = {"measnum", "strain", "sex", "animal_id", "zscore", "value"}
        miss = need - set(ph.columns)
        if miss:
            raise ValueError(f"{csv_path} missing columns: {sorted(miss)}")

        # If the CSV contains more than one measure, filter it; otherwise this is a no-op
        ph = ph.loc[ph["measnum"] == measure_num].copy()

        # Build per-sex outputs exactly like Hao: <measure>.<sex>.*
        for sex in ("f", "m"):
            # streaming path; these helpers were defined in this module
            build_measure_sex(
                src_ped=Path(ped_file),
                src_map=Path(map_file),
                pheno_df=ph,
                measure=measure_num,
                sex_label=sex,
                outdir=outdir,
                plink2_bin=plink2_path,
            )

