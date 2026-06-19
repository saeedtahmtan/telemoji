#!/usr/bin/env python3
import os, sys, argparse
from pathlib import Path
from multiprocessing import Pool, cpu_count
from PIL import Image
from tqdm import tqdm

TGS_EXT = ".tgs"
WEBP_EXT = ".webp"


def convert_one(args):
    tgs_path, webp_path = args
    try:
        from rlottie_python import LottieAnimation
        anim = LottieAnimation.from_tgs(str(tgs_path))
        total = anim.lottie_animation_get_totalframe()
        fps = anim.lottie_animation_get_framerate()
        duration_ms = int(1000 / fps) if fps > 0 else 33
        frames = [anim.render_pillow_frame(i) for i in range(total)]
        webp_path.parent.mkdir(parents=True, exist_ok=True)
        frames[0].save(
            str(webp_path), save_all=True, append_images=frames[1:],
            loop=0, duration=duration_ms, format="WEBP",
        )
        return (tgs_path, webp_path, None)
    except Exception as e:
        return (tgs_path, webp_path, str(e))


def main():
    parser = argparse.ArgumentParser(description="Batch convert TGS to animated WebP")
    parser.add_argument("--input", default="tgs")
    parser.add_argument("--output", default="webp")
    parser.add_argument("--skip-existing", action="store_true", default=True)
    parser.add_argument("--files", nargs="*", help="Only convert these TGS files (relative to --input)")
    parser.add_argument("--jobs", type=int, default=cpu_count(), help="Parallel workers")
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

    batch = []
    for tgs_path in tgs_files:
        if not tgs_path.exists():
            print(f"  SKIP (not found): {tgs_path}")
            continue
        rel = tgs_path.relative_to(input_root)
        webp_path = output_root / rel.with_suffix(WEBP_EXT)
        if args.skip_existing and webp_path.exists():
            continue
        batch.append((tgs_path, webp_path))

    if not batch:
        print("All WebP files already exist — nothing to do")
        return

    print(f"Converting {len(batch)} files with {args.jobs} workers...")
    ok = fail = 0
    with Pool(args.jobs) as pool:
        results = list(tqdm(pool.imap_unordered(convert_one, batch), total=len(batch), unit="file"))
    for tgs_path, webp_path, err in results:
        if err:
            print(f"  FAILED: {tgs_path.relative_to(input_root)} — {err}")
            fail += 1
        else:
            ok += 1

    print(f"\nDone: {ok} converted, {fail} failed")


if __name__ == "__main__":
    main()
