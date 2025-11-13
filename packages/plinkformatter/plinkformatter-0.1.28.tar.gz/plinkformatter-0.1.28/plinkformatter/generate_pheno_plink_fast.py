# generate_pheno_plink_fast.py
from __future__ import annotations
import os
import io
import math
import logging
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




def write_keep_ids_from_pheno(pheno_path: str, out_path: str) -> int:
    """
    Emit a PLINK --keep (FID IID) line for every PHENO row with a numeric value.
    Args:
        pheno_path: Path to 'FID IID <phenovalue>' file (3 columns, space-delimited).
        out_path: Output path for the two-column --keep file (no header).
    Returns:
        int: number of lines written.
    """
    n = 0
    with open(pheno_path) as r, open(out_path, "w") as w:
        for ln in r:
            parts = ln.split()
            if len(parts) < 3:
                continue
            fid, iid, val = parts[:3]
            # accept any numeric (including negatives/decimals)
            try:
                float(val)
            except ValueError:
                continue
            w.write(f"{fid} {iid}\n")
            n += 1
    return n




def write_keep_ids_intersect_fam(pheno_path: str, fam_path: str, out_path: str) -> int:
    """
    Build a PLINK --keep (FID IID) by intersecting PHENO and FAM.




    Args:
        pheno_path: space-delimited 'FID IID value' file (no header).
        fam_path:   space-delimited PLINK .fam (only FID/IID are read).
        out_path:   destination for two-column keep file (no header).




    Returns:
        int: number of rows written.
    """
    ph = pd.read_csv(
        pheno_path, sep=r"\s+", header=None, usecols=[0, 1, 2],
        names=["FID", "IID", "val"], engine="python"
    )
    # keep numeric-only phenos
    ph = ph[pd.to_numeric(ph["val"], errors="coerce").notna()][["FID", "IID"]]


    fam = pd.read_csv(
        fam_path, sep=r"\s+", header=None, usecols=[0, 1],
        names=["FID", "IID"], engine="python"
    )


    keep = fam.merge(ph, on=["FID", "IID"], how="inner")[["FID", "IID"]]
    Path(out_path).parent.mkdir(parents=True, exist_ok=True)
    keep.to_csv(out_path, sep=" ", header=False, index=False)
    return int(keep.shape[0])




def generate_pheno_plink_fast(
    ped_file: str,
    map_file: str,
    pheno: pd.DataFrame,
    outdir: str,
    ncore: int = 1,
) -> pd.DataFrame:
    """
    Streamed writer for PED/MAP/PHENO with RAW per-animal phenotypes.


    Behavior:
        - Within each (measnum, sex), emit one PED row per replicate (animal).
          * FID = sanitized strain
          * IID = animal_id (no custom suffixes)
          * SEX (col 5) set from group ('f'->2, 'm'->1)
          * PHE (col 6) = raw 'value' for that animal (or -9 if missing)
        - PHENO is THREE columns with ONE ROW PER REPLICATE: 'FID IID value'
          (value is the same raw 'value' used in PED col6).
        - MAP is copied/sanitized once per group (rsid '.' -> 'chr_bp').


    Args:
        ped_file (str): Reference PED (provides genotype line template per strain).
        map_file (str): Corresponding MAP.
        pheno (pd.DataFrame): Must contain columns: 'strain', 'sex', 'measnum', 'value', 'animal_id'.
        outdir (str): Output directory for {base}.{sex}.ped/.map/.pheno.
        ncore (int): Reserved for future parallelization (unused here).


    Returns:
        pd.DataFrame: Filtered phenotype rows actually used (post PED/strain filtering).


    Raises:
        ValueError: If required columns are missing or malformed.
    """
    os.makedirs(outdir, exist_ok=True)
    if pheno is None or pheno.empty:
        return pd.DataFrame()


    # required columns
    for col in ("strain", "sex", "measnum", "value"):
        if col not in pheno.columns:
            raise ValueError("pheno must have columns: 'strain', 'sex', 'measnum', 'value' (+ 'animal_id').")


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


    ped_strains = set(ped_offsets.keys())
    ph = ph[ph["strain"].isin(ped_strains)].sort_values(by="strain", kind="stable").reset_index(drop=True)
    if ph.empty:
        return ph


    # Read MAP once, sanitize rs IDs of "."
    map_df = pd.read_csv(map_file, header=None, sep="\t")
    map_df[1] = np.where(map_df[1] == ".", map_df[0].astype(str) + "_" + map_df[3].astype(str), map_df[1].astype(str))


    # Group by (measnum, sex)
    groups: Dict[Tuple[int, str], pd.DataFrame] = {}
    for (measnum, sex), df in ph.groupby(["measnum", "sex"], sort=False):
        groups[(int(measnum), str(sex))] = df


    # Write outputs per group
    for (measnum, sex), df in groups.items():
        # Build per-strain queues of (iid, value) for ALL replicates
        # IID policy: use animal_id (string); NO custom "__" suffix.
        queues: Dict[str, List[Tuple[str, Optional[float]]]] = defaultdict(list)
        for row in df.itertuples(index=False):
            strain = str(row.strain)
            # per-animal raw value
            val = getattr(row, "value", None)
            try:
                val = float(val)
            except Exception:
                val = None
            # iid from animal_id; fall back to incremental tag if absent
            aid = getattr(row, "animal_id", None)
            if aid is None or (isinstance(aid, float) and math.isnan(aid)):
                aid = f"rep{len(queues[strain]) + 1}"
            iid = str(aid)
            queues[strain].append((iid, val))


        strains_in_order = list(dict.fromkeys(df["strain"].tolist()))  # preserve stable order


        # Write MAP
        map_out = os.path.join(outdir, f"{measnum}.{sex}.map")
        map_df.to_csv(map_out, sep="\t", index=False, header=False)


        # Write PED (all replicates with raw 'value' as PHE) and PHENO (one per replicate)
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


                # Normalize FID
                parts[0] = parts[0].replace("?", "").replace(" ", "").upper()


                # Emit all replicates for this strain
                for iid, val in queues[strain]:
                    meta = parts[:6]
                    meta[1] = iid                               # IID = animal_id (string)
                    meta[4] = "2" if sex == "f" else "1"        # SEX
                    if val is None or (isinstance(val, float) and not math.isfinite(val)):
                        meta[5] = "-9"                          # missing phenotype
                    else:
                        meta[5] = f"{val}"                      # RAW value


                    # Reconstruct PED row (space-delimited; expand genotype pairs)
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


                    # PHENO row: FID IID value (one per replicate)
                    if val is None or (isinstance(val, float) and not math.isfinite(val)):
                        f_ph.write(f"{strain} {iid} -9\n")
                    else:
                        f_ph.write(f"{strain} {iid} {val}\n")


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
            fam_path  = f"{out_prefix}.fam"  # written by PLINK in the BED/BIM/FAM step above
            # but fam doesn't exist yet here; move keep creation AFTER BED/BIM/FAM creation


            logging.info(f"[fast_prepare_pylmm_inputs] generate_bed_bim_fam for {base_id}.{sex}")


            # 1) Make BED/BIM/FAM from the PED/MAP (this writes {out_prefix}.fam)
            generate_bed_bim_fam(
                plink2_path=plink2_path,
                ped_file=ped_path,
                map_file=map_path,
                output_prefix=out_prefix,
                relax_mind_threshold=False,
                maf_threshold=0.05,
                sample_keep_path=None,          # <-- no keep yet
                autosomes_only=True,
            )


            # 2) Now build KEEP by intersecting PHENO with the actual FAM we just produced
            keep_path = f"{out_prefix}.keep.id"
            fam_path  = f"{out_prefix}.fam"
            n_kept = write_keep_ids_intersect_fam(pheno_path, fam_path, keep_path)
            logging.info(f"[fast_prepare_pylmm_inputs] {base_id}.{sex}: wrote {n_kept} rows (PHENO ∩ FAM)")


            # 3) Re-run PLINK on the PFILE->BED step with --keep to filter down the dataset (optional but clean)
            #    If you prefer not to re-run, you can skip this; PLINK will accept --keep in kinship too.
            #    For clarity + reproducibility, we re-materialize a kept-only BED set into {out_prefix}.kept.*
            from plinkformatter.plink_utils import create_sorted_pgen, run_plink2
            create_sorted_pgen(plink2_path, ped_path, map_path, out_prefix + ".kept")
            run_plink2(
                f"{plink2_path} --pfile {out_prefix}.kept_temp --make-bed "
                f"--geno 0.1 --mind 0.1 --maf 0.05 --keep {keep_path} --chr 1-19 --out {out_prefix}"
            )


            # 4) Kinship on the final kept set
            logging.info(f"[fast_prepare_pylmm_inputs] Trying to compute kinship matrix")
            calculate_kinship_matrix(
                plink2_path=plink2_path,
                input_prefix=out_prefix,
                output_prefix=os.path.join(outdir, f"{base_id}.{sex}.kin"),
                sample_keep_path=keep_path,
            )
