# generate_pheno_plink_fast.py
from __future__ import annotations
import os
import io
import math
import logging
from typing import Dict, List

import numpy as np
import pandas as pd

from plinkformatter.plink_utils import generate_bed_bim_fam, calculate_kinship_matrix
from plinkformatter.generate_pheno_plink import extract_pheno_measure


def generate_pheno_plink_fast(
    ped_file: str,
    map_file: str,
    pheno: pd.DataFrame,
    outdir: str,
    ncore: int = 1,
) -> pd.DataFrame:
    """
    Write per-(measnum, sex) PLINK inputs (PED/MAP/PHENO) with **replicate-level** samples
    and Hao-style IDs: FID = STRAIN, IID = STRAIN (duplicated per replicate).

    PED col semantics per row:
      - FID = STRAIN
      - IID = STRAIN
      - PID = 0, MID = 0
      - SEX = 2 for 'f', 1 for 'm'
      - PHE = replicate zscore if present, else -9   (Hao uses zscore in V6)

    PHENO file per replicate row:
      - "FID IID zscore value"    (four columns, space-delimited)
        pylmm can use column index 0 (zscore) like Hao's "-p 0".

    MAP is written once per group, with '.' rsIDs replaced by 'chr_bp'.
    """
    os.makedirs(outdir, exist_ok=True)
    if pheno is None or pheno.empty:
        return pd.DataFrame()

    for col in ("strain", "sex", "measnum", "value"):
        if col not in pheno.columns:
            raise ValueError(
                "pheno must have columns: 'strain', 'sex', 'measnum', 'value' (+ optional 'zscore')."
            )

    ph = pheno.copy()
    ph["strain"] = ph["strain"].astype(str).str.replace(" ", "", regex=False).str.upper()
    ph = ph[ph["sex"].isin(["f", "m"])].copy()
    if ph.empty:
        return ph

    # Index reference PED by strain (first occurrence per strain).
    ped_offsets: Dict[str, int] = {}
    with open(ped_file, "rb") as f:
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            first_tab = line.find(b"\t")
            fid_bytes = (line.strip().split()[0] if first_tab <= 0 else line[:first_tab])
            name = fid_bytes.decode(errors="replace").replace("?", "").replace(" ", "").upper()
            if name and name not in ped_offsets:
                ped_offsets[name] = pos

    # keep only strains present in the reference PED
    ped_strains = set(ped_offsets.keys())
    ph = ph[ph["strain"].isin(ped_strains)].reset_index(drop=True)
    if ph.empty:
        return ph

    # Read MAP once, sanitize rs IDs of "."
    map_df = pd.read_csv(map_file, header=None, sep=r"\s+")
    map_df[1] = np.where(
        map_df[1] == ".",
        map_df[0].astype(str) + "_" + map_df[3].astype(str),
        map_df[1].astype(str),
    )

    # Ensure we have a zscore column (Hao uses zscore in PED V6 and in PHENO)
    if "zscore" not in ph.columns:
        ph["zscore"] = np.nan

    # Group by (measnum, sex) and write outputs
    for (measnum, sex), df in ph.groupby(["measnum", "sex"], sort=False):
        measnum = int(measnum)
        sex = str(sex)

        # Write MAP
        map_out = os.path.join(outdir, f"{measnum}.{sex}.map")
        map_df.to_csv(map_out, sep="\t", index=False, header=False)

        # Write PED (one row *per replicate*, FID=IID=strain) and PHENO ("FID IID zscore value")
        ped_out = os.path.join(outdir, f"{measnum}.{sex}.ped")
        phe_out = os.path.join(outdir, f"{measnum}.{sex}.pheno")

        # keep stable strain order and stable replicate order within strain
        df = df.sort_values(["strain"]).reset_index(drop=True)

        with open(ped_out, "w", encoding="utf-8") as f_ped, open(phe_out, "w", encoding="utf-8") as f_ph:
            for strain, sdf in df.groupby("strain", sort=False):
                # load the template line for this strain from reference PED
                with open(ped_file, "rb") as f:
                    f.seek(ped_offsets[strain])
                    raw = f.readline().decode(errors="replace").rstrip("\n")

                parts = raw.split("\t")
                if len(parts) <= 6:
                    parts = raw.split()
                if len(parts) < 7:
                    raise ValueError("Malformed PED: expected >=7 columns (6 meta + genotypes)")

                # normalize FID in template
                parts[0] = parts[0].replace("?", "").replace(" ", "").upper()

                # write one PED row per replicate (duplicate genotype row; FID=IID=strain)
                for _, r in sdf.iterrows():
                    z = r.get("zscore", np.nan)
                    val = r.get("value", np.nan)
                    try:
                        z = float(z)
                    except Exception:
                        z = np.nan
                    try:
                        val = float(val)
                    except Exception:
                        val = np.nan

                    meta = parts[:6]
                    meta[0] = strain              # FID
                    meta[1] = strain              # IID (same as FID, per Hao)
                    meta[2] = "0"                 # PID
                    meta[3] = "0"                 # MID
                    meta[4] = "2" if sex == "f" else "1"   # SEX
                    meta[5] = f"{z}" if math.isfinite(z) else "-9"  # PHE = zscore

                    # reconstruct PED row
                    out = io.StringIO()
                    out.write(" ".join(meta))
                    for gp in parts[6:]:
                        a_b = gp.split(" ")
                        if len(a_b) != 2:
                            a_b = gp.split()
                            if len(a_b) != 2:
                                raise ValueError(f"Genotype pair not splitable into two alleles: {gp!r}")
                        out.write(f" {a_b[0]} {a_b[1]}")
                    f_ped.write(out.getvalue() + "\n")

                    # PHENO: FID IID zscore value (four columns)
                    f_ph.write(
                        f"{strain} {strain} "
                        f"{(z if math.isfinite(z) else -9)} "
                        f"{(val if math.isfinite(val) else -9)}\n"
                    )

        logging.info(f"[generate_pheno_plink_fast] wrote {ped_out}, {map_out}, {phe_out}")

    return ph


def fast_prepare_pylmm_inputs(
    ped_file: str,
    map_file: str,
    measure_id_directory: str,
    measure_ids: List,
    outdir: str,
    ncore: int,
    plink2_path: str,
    *,
    ped_pheno_field: str = "zscore",
) -> None:
    """
    Orchestrate extraction and PLINK file generation **like Hao**:

      1) Extract phenotype rows for requested measure_ids.
      2) Generate per-(measnum, sex):
           - {base}.{sex}.map
           - {base}.{sex}.ped   (replicate-level rows; FID=IID=STRAIN; PED V6=zscore)
           - {base}.{sex}.pheno (FID IID zscore value)
      3) Convert PED/MAP -> BED/BIM/FAM with: --geno 0.1 --mind 0.1
         (NO --maf; NO --keep).
      4) Compute kinship with: --make-rel square.
    """
    os.makedirs(outdir, exist_ok=True)

    pheno = extract_pheno_measure(measure_id_directory, measure_ids)
    if pheno is None or pheno.empty:
        logging.info("[fast_prepare_pylmm_inputs] no phenotype rows extracted; nothing to do.")
        return

    used = generate_pheno_plink_fast(
        ped_file=ped_file,
        map_file=map_file,
        pheno=pheno,
        outdir=outdir,
        ncore=ncore,
    )
    if used is None or used.empty:
        logging.info("[fast_prepare_pylmm_inputs] no usable phenotypes after PED intersection; nothing to do.")
        return

    for measure_id in measure_ids:
        base_id = str(measure_id).split("_", 1)[0]
        for sex in ("f", "m"):
            ped_path   = os.path.join(outdir, f"{base_id}.{sex}.ped")
            map_path   = os.path.join(outdir, f"{base_id}.{sex}.map")
            out_prefix = os.path.join(outdir, f"{base_id}.{sex}")

            if not (os.path.exists(ped_path) and os.path.exists(map_path)):
                continue

            logging.info(f"[fast_prepare_pylmm_inputs] make BED/BIM/FAM for {base_id}.{sex}")
            generate_bed_bim_fam(
                plink2_path=plink2_path,
                ped_file=ped_path,
                map_file=map_path,
                output_prefix=out_prefix,
                relax_mind_threshold=False,
                maf_threshold=None,     # match Hao: no --maf
                sample_keep_path=None,  # no --keep
                autosomes_only=False,   # match Hao: no --chr constraint
            )

            logging.info(f"[fast_prepare_pylmm_inputs] compute kinship for {base_id}.{sex}")
            calculate_kinship_matrix(
                plink2_path=plink2_path,
                input_prefix=out_prefix,
                output_prefix=os.path.join(outdir, f"{base_id}.{sex}.kin"),
                sample_keep_path=None,
            )
