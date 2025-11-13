# generate_pheno_plink_fast.py
from __future__ import annotations
import os
import io
import math
from collections import defaultdict
from typing import Dict, Iterable, List, Tuple, Optional
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm  # <-- needed for rank-Z

from plinkformatter.plink_utils import generate_bed_bim_fam, calculate_kinship_matrix
from plinkformatter.generate_pheno_plink import extract_pheno_measure

# ----------------------------
# Helpers
# ----------------------------

def _sanitize_strain(s: str) -> str:
    if not isinstance(s, str):
        s = str(s)
    return s.replace("?", "").replace(" ", "").upper()


def _base_id(mid) -> str:
    s = str(mid)
    return s.split("_", 1)[0]


def _read_map_sanitized(map_file: str) -> pd.DataFrame:
    df = pd.read_csv(map_file, header=None, sep="\t")
    df[1] = np.where(df[1] == ".", df[0].astype(str) + "_" + df[3].astype(str), df[1].astype(str))
    return df


def _iter_ped_strain_offsets(ped_path: str) -> Dict[str, int]:
    offsets: Dict[str, int] = {}
    with open(ped_path, "rb") as f:
        while True:
            pos = f.tell()
            line = f.readline()
            if not line:
                break
            first_tab = line.find(b"\t")
            fid_bytes = (line.strip().split()[0] if first_tab <= 0 else line[:first_tab])
            name = _sanitize_strain(fid_bytes.decode(errors="replace"))
            if name and name not in offsets:
                offsets[name] = pos
    return offsets


def _read_ped_line_at_offset(ped_path: str, offset: int) -> str:
    with open(ped_path, "rb") as f:
        f.seek(offset)
        raw = f.readline()
    return raw.decode(errors="replace").rstrip("\n")


def _parse_tab_ped_line_to_parts(line: str) -> List[str]:
    parts = line.split("\t")
    if len(parts) <= 6:
        parts = line.split()
    return parts


def _flatten_pairs_to_space_stream(parts: List[str], sex_flag: str, phe_value: Optional[float]) -> str:
    if len(parts) < 7:
        raise ValueError("Malformed PED: expected >=7 columns (6 meta + genotypes)")
    meta = parts[:6]
    meta[4] = "2" if sex_flag == "f" else "1"
    if phe_value is not None:
        if isinstance(phe_value, float) and (not math.isfinite(phe_value)):
            phe_value = -9
        meta[5] = "-9" if (isinstance(phe_value, float) and math.isnan(phe_value)) else str(phe_value)
    out = io.StringIO()
    out.write(" ".join(meta))
    for gp in parts[6:]:
        a_b = gp.split(" ")
        if len(a_b) != 2:
            a_b = gp.split()
            if len(a_b) != 2:
                raise ValueError(f"Genotype pair not splitable into two alleles: {gp!r}")
        out.write(f" {a_b[0]} {a_b[1]}")
    return out.getvalue()


def write_keep_ids(pheno_path: str, fam_path: Optional[str], out_path: str) -> int:
    """
    Build a PLINK --keep file (FID IID) from a PHENO file.

    Args:
        pheno_path (str): Path to .pheno with columns [FID, IID, z].
        fam_path (Optional[str]): Optional .fam to intersect (preserves .fam order).
        out_path (str): Output path for two-column keep file (no header).

    Returns:
        int: Number of kept samples written.
    """
    ph = pd.read_csv(
        pheno_path, sep=r"\s+", header=None, usecols=[0, 1, 2],
        names=["FID", "IID", "z"], engine="python"
    )
    ph = ph[pd.to_numeric(ph["z"], errors="coerce").notna()][["FID", "IID"]]

    if fam_path:
        fam = pd.read_csv(
            fam_path, sep=r"\s+", header=None, usecols=[0, 1],
            names=["FID", "IID"], engine="python"
        )
        keep = fam.merge(ph, on=["FID", "IID"], how="inner")[["FID", "IID"]]
    else:
        keep = ph

    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    keep.to_csv(out_path, sep=" ", header=False, index=False)
    return len(keep)


# ---------- NEW: rank-Z transform like legacy/R ----------
def _rankz(series: pd.Series) -> pd.Series:
    """
    Rank-Z transform matching legacy/R rz.transform.

    Formula:
        z = qnorm(rank(y, ties='average') / (n_nonmissing + 1))

    Args:
        series (pd.Series): Numeric series with possible NaNs.

    Returns:
        pd.Series: Rank-Z transformed values aligned to input index (NaN preserved).
    """
    s = pd.to_numeric(series, errors="coerce")
    ranks = s.rank(method="average", na_option="keep")
    n = ranks.notna().sum()
    if n == 0:
        return pd.Series(np.nan, index=series.index)
    p = ranks / float(n + 1)
    return pd.Series(norm.ppf(p), index=series.index)

# ----------------------------
# Core: fast generator
# ----------------------------
def generate_pheno_plink_fast(
    ped_file: str,
    map_file: str,
    pheno: pd.DataFrame,
    outdir: str,
    ncore: int = 1,
) -> pd.DataFrame:
    """
    Streamed writer for PED/MAP/PHENO with rank-Z phenotype per strain.

    Behavior:
        - Within each (measnum, sex), compute strain mean of `value`, then global rank-Z across strains.
        - Write .pheno with ONE row per strain: "FID IID z", where IID is the first emitted IID for that strain.
        - Write .ped for ALL replicates; PED col6 (PHE) is the strain’s rank-Z value (keeps PED consistent).

    Args:
        ped_file (str): Reference PED (provides strain rows and genotypes).
        map_file (str): Corresponding MAP.
        pheno (pd.DataFrame): Must contain columns: 'strain', 'sex', 'measnum', 'value' (and optional 'animal_id').
        outdir (str): Output directory for {base}.{sex}.ped/.map/.pheno.
        ncore (int): Reserved for future parallelization (unused here).

    Returns:
        pd.DataFrame: Filtered phenotype rows actually used (post strain/PED filtering).

    Raises:
        ValueError: If required columns are missing or rank-Z has zero/invalid variance.
    """
    os.makedirs(outdir, exist_ok=True)
    if pheno is None or pheno.empty:
        return pd.DataFrame()

    for col in ("strain", "sex", "measnum"):
        if col not in pheno.columns:
            raise ValueError("pheno must have columns: 'strain', 'sex', 'measnum' (plus 'value').")

    ph = pheno.copy()
    ph["strain"] = ph["strain"].astype(str).str.replace(" ", "", regex=False).str.upper()
    ph = ph[ph["sex"].isin(["f", "m"])].copy()
    if ph.empty:
        return ph

    # Ensure we have raw values to average at the strain level.
    if "value" not in ph.columns:
        raise ValueError("Expected raw 'value' column for rank-Z on strain means.")

    # Index reference PED by strain to find genotype lines
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

    ped_strains = set(ped_offsets.keys())
    ph = ph[ph["strain"].isin(ped_strains)].sort_values(by="strain", kind="stable").reset_index(drop=True)
    if ph.empty:
        return ph

    # Read MAP once, sanitize rs IDs of "."
    map_df = pd.read_csv(map_file, header=None, sep="\t")
    map_df[1] = np.where(map_df[1] == ".", map_df[0].astype(str) + "_" + map_df[3].astype(str), map_df[1].astype(str))

    # (measnum, sex) groups
    groups: Dict[Tuple[int, str], pd.DataFrame] = {}
    for (measnum, sex), df in ph.groupby(["measnum", "sex"], sort=False):
        groups[(int(measnum), str(sex))] = df

    # Write outputs per group
    for (measnum, sex), df in groups.items():
        # 1) Strain mean of raw value, then global rank-Z across strains
        strain_mean = df.groupby("strain")["value"].mean()
        z_by_strain = _rankz(strain_mean).to_dict()

        # Guard: there must be between-strain signal after rank-Z
        finite = [v for v in z_by_strain.values() if isinstance(v, (int, float)) and math.isfinite(v)]
        if not finite or float(np.nanstd(finite)) == 0.0:
            raise ValueError(f"Zero/invalid across-strain variance after rank-Z for {measnum}.{sex}")

        # 2) Prepare per-strain IID queues (replicates retain unique IIDs)
        queues: Dict[str, List[str]] = defaultdict(list)
        for row in df.itertuples(index=False):
            strain = str(row.strain)
            aid = getattr(row, "animal_id", None)
            if aid is None or (isinstance(aid, float) and math.isnan(aid)):
                aid = f"rep{len(queues[strain]) + 1}"
            iid = f"{strain}__{str(aid).replace(' ', '_').replace('/', '-')}"
            queues[strain].append(iid)

        strains_in_order = list(dict.fromkeys(df["strain"].tolist()))  # preserve stable order

        # 3) Write MAP
        map_out = os.path.join(outdir, f"{measnum}.{sex}.map")
        map_df.to_csv(map_out, sep="\t", index=False, header=False)

        # 4) Write PED (all reps, PHE = strain rank-Z) and PHENO (one row/strain)
        ped_out = os.path.join(outdir, f"{measnum}.{sex}.ped")
        pheno_out = os.path.join(outdir, f"{measnum}.{sex}.pheno")

        with open(ped_out, "w", encoding="utf-8") as f_ped, open(pheno_out, "w", encoding="utf-8") as f_ph:
            for strain in strains_in_order:
                # Load the reference PED line for this strain
                with open(ped_file, "rb") as f:
                    f.seek(ped_offsets[strain])
                    raw = f.readline().decode(errors="replace").rstrip("\n")

                parts = raw.split("\t")
                if len(parts) <= 6:
                    parts = raw.split()
                if len(parts) < 7:
                    raise ValueError("Malformed PED: expected >=7 columns (6 meta + genotypes)")

                # Normalize meta fields
                parts[0] = parts[0].replace("?", "").replace(" ", "").upper()  # FID
                # parts[1] set below per replicate

                # Rank-Z for this strain
                z_val = float(z_by_strain.get(strain, np.nan))
                if not math.isfinite(z_val):
                    z_str = "-9"
                else:
                    z_str = f"{z_val:.6g}"

                # Emit PED rows (all replicates), with PHE=z_val and SEX set by group
                first_iid = None
                for iid in queues[strain]:
                    meta = parts[:6]
                    meta[1] = iid
                    meta[4] = "2" if sex == "f" else "1"        # SEX
                    meta[5] = z_str                              # PHE (strain-level)
                    # Reconstruct PED row: space-delimited, expand genotype pairs
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
                    if first_iid is None:
                        first_iid = iid

                # Emit ONE PHENO row per strain (FID, first IID, z)
                if first_iid:
                    f_ph.write(f"{strain} {first_iid} {z_str}\n")

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
    ped_pheno_field: str = "zscore",  # ignored in this implementation
) -> None:
    """
    End-to-end writer for PyLMM inputs using rank-Z strain phenotypes.

    Steps:
        1) Extract phenotype rows for `measure_ids`.
        2) Write {base}.{sex}.ped/.map/.pheno via `generate_pheno_plink_fast`.
        3) Build --keep from .pheno (one IID/strain), then make BED/BIM/FAM and KIN.

    Args:
        ped_file (str): Reference PED (for genotype rows).
        map_file (str): MAP matching the PED’s SNP grid.
        measure_id_directory (str): Folder holding CSV(s) for the requested measures.
        measure_ids (List): Set/list of measure IDs (e.g., {"40701_NON_DO"}).
        outdir (str): Output folder.
        ncore (int): Threads (reserved).
        plink2_path (str): Path to plink2 binary.
        ped_pheno_field (str): Kept for API parity; ignored (we always write rank-Z).

    Returns:
        None

    Raises:
        ValueError: If phenotype extraction fails or outputs are malformed.
    """
    os.makedirs(outdir, exist_ok=True)
    pheno = extract_pheno_measure(measure_id_directory, measure_ids)
    if pheno is None or pheno.empty:
        return

    generate_pheno_plink_fast(
        ped_file=ped_file,
        map_file=map_file,
        pheno=pheno,
        outdir=outdir,
        ncore=ncore,
    )

    for measure_id in measure_ids:
        base_id = str(measure_id).split("_", 1)[0]
        for sex in ("f", "m"):
            ped_path   = os.path.join(outdir, f"{base_id}.{sex}.ped")
            map_path   = os.path.join(outdir, f"{base_id}.{sex}.map")
            pheno_path = os.path.join(outdir, f"{base_id}.{sex}.pheno")
            out_prefix = os.path.join(outdir, f"{base_id}.{sex}")

            if not (os.path.exists(ped_path) and os.path.exists(pheno_path)):
                continue

            keep_path = f"{out_prefix}.keep.id"
            write_keep_ids(pheno_path, fam_path=None, out_path=keep_path)

            generate_bed_bim_fam(
                plink2_path=plink2_path,
                ped_file=ped_path,
                map_file=map_path,
                output_prefix=out_prefix,
                relax_mind_threshold=False,
                maf_threshold=0.05,
                sample_keep_path=keep_path,
                autosomes_only=True,
            )

            calculate_kinship_matrix(
                plink2_path=plink2_path,
                input_prefix=out_prefix,
                output_prefix=os.path.join(outdir, f"{base_id}.{sex}.kin"),
                sample_keep_path=keep_path,
            )
