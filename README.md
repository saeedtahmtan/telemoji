<p align="center">
  <img src="./webp/animated/U+1F525_1.webp" alt="Telemoji" width="150px" height="150px"/>
</p>

# Telemoji

Animated Telegram emoji + country flag collection in TGS and WebP formats.

## Contents

| Category | TGS | WebP |
|---|---|---|
| Animated Emojis | 599 | 599 |
| Reactions | 121 | 121 |
| Dice | 78 | 78 |
| Generic Animations | 6 | 6 |
| Default Status | 11 | 11 |
| Channel Status | 11 | 11 |
| Topic Icons | 112 | 112 |
| Premium Gifts | 3 | 3 |
| Flags (251 countries) | 251 | 251 |
| **Total** | **1192** | **1192** |

## Repository Structure

```
tgs/          # TGS (Telegram Sticker) source files
  animated/
  reactions/
  dice/
  generic_anim/
  default_status/
  channel_status/
  topic_icons/
  premium_gifts/
  flags/
webp/         # Converted WebP files (same structure)
  animated/
  reactions/
  ...
  flags/
emojis.json   # Unified metadata for all items
index.html    # Browser to browse, preview, and copy embed code
flags.json    # Flag metadata (name, code, emoji)
scripts/
  download_animated_emojis.py  # Downloads TGS from Telegram
  convert_tgs_to_webp.py       # Batch TGS→WebP conversion using rlottie-python
```

## Usage

Serve the repository root as a static site. Open `index.html` to browse and search, or access files directly:

- `tgs/animated/U+1F600.tgs`
- `webp/reactions/U+2764.webp`
- `tgs/flags/US.tgs`
- `webp/flags/GB.webp`

## Requirements (scripts)

- Python 3.11+
- `pip install telethon python-dotenv tqdm rlottie-python Pillow`

## Credits

- Emoji animations sourced from [Telegram](https://telegram.org)
- Country flags by [Malith Rukshan / animated-country-flags](https://github.com/Malith-Rukshan/animated-country-flags)
