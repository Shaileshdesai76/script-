#!/usr/bin/env python3

import argparse
import subprocess
import sys
import tempfile
import shutil
import os

""" This pipeline helps in converting plink (bed,fam,bim) into eigenstrat, generally eigenstrat does not allow to convert the if Family ID and IND ID is more than 
39 character, which is very common in aDNA, hence this script will allow you convert directly into usualble ind, geno and snp file for your downstream analysis such f3, D, f4 and Admixtools bases. 
basically, it read fam file, convert familly id into number from 1 to sample number; convert into eigen format, then reconstrcut the ind file, and finally it map ind file indivudal ids to orignal fam individual IDS, then insert the family ID from orignnal fam file, so you dont have short the name each time, which i have done 10 time, before i made this scirpt with using AI helps. """
""" run like this;  python3 Eigenstrat_aDNA_run.py par.PED.EIGENSTRAT      """
# ------------------------------------------------------------
# Read parameter file
# ------------------------------------------------------------
def read_parfile(parfile):
    params = {}

    with open(parfile) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            if ":" not in line:
                continue

            key, value = line.split(":", 1)
            params[key.strip()] = value.strip()

    required = [
        "genotypename",
        "snpname",
        "indivname",
        "genotypeoutname",
        "snpoutname",
        "indivoutname",
    ]

    for r in required:
        if r not in params:
            sys.exit(f"ERROR: Missing '{r}' in parameter file.")

    return params


# ------------------------------------------------------------
# Validate original FAM
# ------------------------------------------------------------
def validate_fam(famfile):
    iid_to_fid = {}
    long_ids = []
    duplicate_iid = []

    with open(famfile) as f:
        for lineno, line in enumerate(f, 1):

            cols = line.rstrip().split()

            if len(cols) != 6:
                sys.exit(
                    f"ERROR: {famfile} line {lineno} does not contain 6 columns."
                )

            fid = cols[0]
            iid = cols[1]

            if len(fid) > 39:
                long_ids.append((lineno, "FID", fid, len(fid)))

            if len(iid) > 39:
                long_ids.append((lineno, "IID", iid, len(iid)))

            if iid in iid_to_fid:
                duplicate_iid.append(iid)
            else:
                iid_to_fid[iid] = fid

    if long_ids:
        print("\nERROR: IDs longer than 39 characters found:\n")

        for x in long_ids:
            print(
                f"Line {x[0]:5d}   {x[1]}   Length={x[3]}   {x[2]}"
            )

        sys.exit("\nPlease shorten these IDs before running convertf.")

    if duplicate_iid:
        print("\nERROR: Duplicate IID(s) detected:\n")
        for x in sorted(set(duplicate_iid)):
            print(x)
        sys.exit("\nEach IID must be unique.")

    return iid_to_fid


# ------------------------------------------------------------
# Create temporary fam
# ------------------------------------------------------------
def make_temp_fam(original, newfam):

    with open(original) as fin, open(newfam, "w") as fout:

        for i, line in enumerate(fin, 1):

            cols = line.rstrip().split()

            cols[0] = str(i)

            fout.write("\t".join(cols) + "\n")


# ------------------------------------------------------------
# Create temporary parameter file
# ------------------------------------------------------------
def make_temp_par(parfile, tempfam, newpar):

    with open(parfile) as fin, open(newpar, "w") as fout:

        for line in fin:

            if line.strip().startswith("indivname:"):
                fout.write(f"indivname: {tempfam}\n")
            else:
                fout.write(line)


# ------------------------------------------------------------
# Reconstruct ind
# ------------------------------------------------------------
def rebuild_ind(indfile, iid_to_fid):

    tmp = indfile + ".tmp"

    with open(indfile) as fin, open(tmp, "w") as fout:

        for lineno, line in enumerate(fin, 1):

            cols = line.rstrip().split()

            if len(cols) < 2:
                sys.exit(
                    f"ERROR: Invalid line {lineno} in {indfile}"
                )

            combined = cols[0]
            sex = cols[1]

            if combined.count(":") != 1:
                sys.exit(
                    f"\nERROR: Invalid sample name on line {lineno}\n"
                    f"Expected format: FID:IID\n"
                    f"Found: {combined}"
                )

            pop_from_convertf, iid = combined.split(":", 1)

            if iid not in iid_to_fid:
                sys.exit(
                    f"\nERROR: IID '{iid}' not found in original FAM."
                )

            original_pop = iid_to_fid[iid]

            fout.write(f"{iid}\t{sex}\t{original_pop}\n")

    shutil.move(tmp, indfile)


# ------------------------------------------------------------
# Main
# ------------------------------------------------------------
def main():

    parser = argparse.ArgumentParser(
        description="Wrapper around convertf that avoids 39-character FID limit."
    )

    parser.add_argument("parfile")

    args = parser.parse_args()

    params = read_parfile(args.parfile)

    fam = params["indivname"]

    print("Checking original FAM...")

    iid_to_fid = validate_fam(fam)

    tmpdir = tempfile.mkdtemp(prefix="convertf_")

    tempfam = os.path.join(tmpdir, "temp.fam")
    temppar = os.path.join(tmpdir, "temp.par")

    make_temp_fam(fam, tempfam)

    make_temp_par(args.parfile, tempfam, temppar)

    print("Running convertf...")

    subprocess.run(
        ["convertf", "-p", temppar],
        check=True,
    )

    print("Reconstructing IND file...")

    rebuild_ind(
        params["indivoutname"],
        iid_to_fid,
    )

    shutil.rmtree(tmpdir)

    print("\nSUCCESS")
    print("Finished conversion.")
    print(f"Output IND : {params['indivoutname']}")
    print(f"Output SNP : {params['snpoutname']}")
    print(f"Output GENO: {params['genotypeoutname']}")


if __name__ == "__main__":
    main()
