"""Render docs/banner.png from banner-base.png (the whiteboard without the tagline).

Usage: python3 docs/src/banner.py
Needs Pillow and fontconfig (fc-match) with Noto Sans.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "banner.png"
NAVY = "#1E3F66"


def fc(pattern):
    return subprocess.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True, check=True).stdout


img = Image.open(HERE / "banner-base.png").convert("RGB")
d = ImageDraw.Draw(img)
tagline = ImageFont.truetype(fc("Noto Sans"), 40)
d.text((220, 290), "One person’s trial and error,", font=tagline, fill=NAVY, anchor="ls")
d.text((220, 350), "shared with the team", font=tagline, fill=NAVY, anchor="ls")
d.text(
    (220, 410),
    "What Claude Code and Codex learn goes in .memory/, shared via PRs.",
    font=ImageFont.truetype(fc("Noto Sans"), 18),
    fill=NAVY,
    anchor="ls",
)
img.save(OUT, optimize=True)
print(OUT)
