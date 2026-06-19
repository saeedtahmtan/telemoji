#!/usr/bin/env python3
"""
Download ALL Telegram animated emojis.
Outputs to ./emojis/ directory.

Usage:
    python3 download_animated_emojis.py
"""

import os
import sys
import json
import asyncio
from pathlib import Path

from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.tl.types import (
    InputStickerSetAnimatedEmoji,
    InputStickerSetAnimatedEmojiAnimations,
    InputStickerSetDice,
    InputStickerSetEmojiChannelDefaultStatuses,
    InputStickerSetEmojiDefaultStatuses,
    InputStickerSetEmojiDefaultTopicIcons,
    InputStickerSetEmojiGenericAnimations,
    InputStickerSetPremiumGifts,
    DocumentAttributeFilename,
)
from tqdm import tqdm

DICE_EMOJIS = ["\U0001F3B2", "\U0001F3AF", "\U0001F3C0", "\u26BD", "\U0001F3B0",
               "\U0001F3B3", "\U0001F3B1", "\U0001F3D3", "\U0001FA80", "\U0001F3CF"]

STICKER_SETS = [
    ("animated",       "Animated Emojis",              lambda: InputStickerSetAnimatedEmoji()),
    ("reactions",      "Reaction Animations",          lambda: InputStickerSetAnimatedEmojiAnimations()),
    ("generic_anim",   "Generic Animations",           lambda: InputStickerSetEmojiGenericAnimations()),
    ("default_status", "Default Status Emojis",        lambda: InputStickerSetEmojiDefaultStatuses()),
    ("channel_status", "Channel Default Status Emojis", lambda: InputStickerSetEmojiChannelDefaultStatuses()),
    ("topic_icons",    "Default Topic Icons",          lambda: InputStickerSetEmojiDefaultTopicIcons()),
    ("premium_gifts",  "Premium Gifts",                lambda: InputStickerSetPremiumGifts()),
]

DOWNLOAD_DELAY = 0.2
MAX_RETRIES = 3


def safe_encode(s: str) -> str:
    return "_".join(f"U+{ord(c):04X}" for c in s)


def get_ext(doc) -> str:
    for attr in doc.attributes:
        if isinstance(attr, DocumentAttributeFilename):
            _, ext = os.path.splitext(attr.file_name)
            if ext:
                return ext
    mime_map = {
        "application/x-tgsticker": ".tgs",
        "video/webm": ".webm",
        "image/webp": ".webp",
        "audio/ogg": ".ogg",
        "audio/mpeg": ".mp3",
    }
    return mime_map.get(doc.mime_type, ".bin")


async def download_doc(client, doc, fpath: Path) -> bool:
    if fpath.exists():
        actual = fpath.stat().st_size
        if doc.size > 0 and actual >= doc.size:
            return True
    for attempt in range(MAX_RETRIES):
        try:
            await client.download_media(doc, file=str(fpath))
            return True
        except Exception:
            if attempt < MAX_RETRIES - 1:
                await asyncio.sleep(1)
    return False


def find_emoji_for_doc(packs, doc_id):
    for pack in packs:
        if doc_id in pack.documents:
            idx = pack.documents.index(doc_id)
            return pack.emoticon, idx + 1
    return None, 0


async def fetch_set(client, dir_path, set_name, mk_input):
    out_dir = dir_path / set_name
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        ss = await client(GetStickerSetRequest(stickerset=mk_input(), hash=0))
    except Exception as e:
        print(f"  [{set_name}] SKIPPED: {e}")
        return [], 0, 0
    ok = 0
    fail = 0
    metas = []
    for doc in tqdm(ss.documents, desc=set_name, unit="doc", leave=False):
        emoji, variant = find_emoji_for_doc(ss.packs, doc.id)
        code = safe_encode(emoji) if emoji else str(doc.id)
        ext = get_ext(doc)
        if variant:
            fname = f"{code}_{variant}{ext}"
        else:
            fname = f"{code}{ext}"
        fpath = out_dir / fname
        if await download_doc(client, doc, fpath):
            ok += 1
        else:
            fail += 1
        metas.append({
            "emoji": emoji or "",
            "type": set_name,
            "file": f"{set_name}/{fname}",
            "document_id": doc.id,
            "access_hash": doc.access_hash,
            "emoji_code": code,
            "variant": variant,
        })
        await asyncio.sleep(DOWNLOAD_DELAY)
    return metas, ok, fail


async def main():
    load_dotenv()
    api_id = int(os.getenv("API_ID", "0"))
    api_hash = os.getenv("API_HASH", "")
    bot_token = os.getenv("BOT_TOKEN", "")

    if not api_id or not api_hash:
        print("Error: API_ID and API_HASH must be set in .env")
        sys.exit(1)

    base = Path("emojis")
    base.mkdir(exist_ok=True)

    client = TelegramClient("session_dl_emojis", api_id, api_hash)
    if bot_token:
        await client.start(bot_token=bot_token)
    else:
        await client.start()
    print("Connected to Telegram\n")

    all_meta = []
    grand_ok = 0
    grand_fail = 0

    # ── Phase 1: All sticker sets ──
    print(f"Downloading {len(STICKER_SETS)} sticker set categories...\n")
    for dir_name, label, mk_input in STICKER_SETS:
        print(f"  [{label}]")
        metas, ok, fail = await fetch_set(client, base, dir_name, mk_input)
        total = ok + fail
        print(f"    {ok}/{total} downloaded ({fail} failed)\n" if fail else f"    {ok}/{total} downloaded\n")
        all_meta.extend(metas)
        grand_ok += ok
        grand_fail += fail

    # ── Phase 2: Dice ──
    print("  [Dice Emojis]")
    dice_dir = base / "dice"
    dice_dir.mkdir(exist_ok=True)
    dice_ok = 0
    dice_fail = 0
    for de in tqdm(DICE_EMOJIS, desc="dice", unit="set", leave=False):
        try:
            ss = await client(GetStickerSetRequest(
                stickerset=InputStickerSetDice(emoticon=de), hash=0,
            ))
        except Exception:
            continue
        code = safe_encode(de)
        for face_idx, doc in enumerate(ss.documents):
            ext = get_ext(doc)
            fname = f"{code}_{face_idx + 1}{ext}"
            fpath = dice_dir / fname
            if await download_doc(client, doc, fpath):
                dice_ok += 1
            else:
                dice_fail += 1
            all_meta.append({
                "emoji": de,
                "type": "dice",
                "file": f"dice/{fname}",
                "document_id": doc.id,
                "access_hash": doc.access_hash,
                "emoji_code": code,
                "face": face_idx + 1,
            })
            await asyncio.sleep(DOWNLOAD_DELAY)
    total_dice = dice_ok + dice_fail
    print(f"    {dice_ok}/{total_dice} downloaded ({dice_fail} failed)\n" if dice_fail else f"    {dice_ok}/{total_dice} downloaded\n")
    grand_ok += dice_ok
    grand_fail += dice_fail

    # ── Write metadata ──
    meta_path = base / "metadata.json"
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(all_meta, f, ensure_ascii=False, indent=2)
    print(f"Metadata written to {meta_path}")

    counts = {}
    for e in all_meta:
        counts[e["type"]] = counts.get(e["type"], 0) + 1
    print("\nFinal summary:")
    for t, c in sorted(counts.items()):
        print(f"  {t}: {c}")
    print(f"  total: {sum(counts.values())} ({grand_ok} ok, {grand_fail} failed)")

    await client.disconnect()


if __name__ == "__main__":
    asyncio.run(main())
