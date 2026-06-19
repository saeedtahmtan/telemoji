#!/usr/bin/env python3
"""
Convert all TGS files in a directory tree to animated WebP using rlottie.
Output mirrors the input directory structure under a 'webp/' root.
"""

import os
import sys
import argparse
from pathlib import Path

from PIL import Image
from tqdm import tqdm

TGS_EXT = ".tgs"
WEBP_EXT = ".webp"


def convert_tgs_to_webp(tgs_path: Path, webp_path: Path):
    from rlottie_python import LottieAnimation
    anim = LottieAnimation.from_tgs(str(tgs_path))
    total = anim.lottie_animation_get_totalframe()
    fps = anim.lottie_animation_get_framerate()
    duration_ms = int(1000 / fps) if fps > 0 else 33

    frames = []
    for i in range(total):
        frame = anim.render_pillow_frame(i)
        frames.append(frame)

    webp_path.parent.mkdir(parents=True, exist_ok=True)
    frames[0].save(
        str(webp_path),
        save_all=True,
        append_images=frames[1:],
        loop=0,
        duration=duration_ms,
        format="WEBP",
    )


def main():
    parser = argparse.ArgumentParser(description="Batch convert TGS to animated WebP")
    parser.add_argument("--input", default="emojis", help="Input directory containing TGS files")
    parser.add_argument("--output", default="webp", help="Output directory for WebP files")
    parser.add_argument("--skip-existing", action="store_true", default=True, help="Skip if WebP already exists")
    args = parser.parse_args()

    input_root = Path(args.input)
    output_root = Path(args.output)

    tgs_files = sorted(input_root.rglob(f"*{TGS_EXT}"))
    if not tgs_files:
        print(f"No .tgs files found under {input_root}")
        sys.exit(1)

    ok = 0
    skip = 0
    fail = 0
    for tgs_path in tqdm(tgs_files, desc="Converting", unit="file"):
        rel = tgs_path.relative_to(input_root)
        webp_path = output_root / rel.with_suffix(WEBP_EXT)

        if args.skip_existing and webp_path.exists():
            skip += 1
            continue

        try:
            convert_tgs_to_webp(tgs_path, webp_path)
            ok += 1
        except Exception as e:
            print(f"\n  FAILED: {rel} — {e}")
            fail += 1

    print(f"\nDone: {ok} converted, {skip} skipped, {fail} failed")


if __name__ == "__main__":
    main()
