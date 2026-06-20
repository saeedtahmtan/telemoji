#!/usr/bin/env python3
import os, sys, shutil, argparse
from pathlib import Path

TGS_EXT = ".tgs"
LOTTIE_EXT = ".json"

def main():
    parser = argparse.ArgumentParser(description="Copy TGS files to lottie/ as .json")
    parser.add_argument("--input", default="tgs")
    parser.add_argument("--output", default="lottie")
    parser.add_argument("--files", nargs="*", help="Only copy these TGS files (relative to --input)")
    args = parser.parse_args()

    input_root = Path(args.input)
    output_root = Path(args.output)

    if args.files:
        tgs_files = sorted(input_root / f for f in args.files)
    else:
        tgs_files = sorted(input_root.rglob(f"*{TGS_EXT}"))

    if not tgs_files:
        print(f"No .tgs files found")
        sys.exit(1)

    copied = skipped = 0
    for tgs_path in tgs_files:
        if not tgs_path.exists():
            print(f"  SKIP (not found): {tgs_path}")
            skipped += 1
            continue
        rel = tgs_path.relative_to(input_root)
        lottie_path = output_root / rel.with_suffix(LOTTIE_EXT)
        if lottie_path.exists():
            skipped += 1
            continue
        lottie_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(tgs_path, lottie_path)
        print(f"  COPY: {rel} -> {lottie_path.relative_to(output_root.parent)}")
        copied += 1

    print(f"\nDone: {copied} copied, {skipped} skipped")
    if copied == 0:
        sys.exit(0)

if __name__ == "__main__":
    main()
