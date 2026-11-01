# update_portrait.py - rebuilds the ASCII portrait when your GitHub profile picture changes.
import hashlib
import io
import os
import sys
import urllib.request
from html import escape

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove

USERNAME = "DebjitXD"            # your GitHub username
OUTPUT = "ascii-portrait.svg"    # the file this script creates (same name your README uses)
HASH_FILE = "avatar.sha"         # remembers which picture we already converted

COLS = 100                       # characters per row (more = more detail)
CHAR_W, LINE_H, PAD = 3.5, 7.0, 10
RAMP = " .`:-=+*cs#%@"           # empty -> dense characters

# 1) Get your profile picture (or a local file if you type its name after the script)
if len(sys.argv) > 1:
    data = open(sys.argv[1], "rb").read()
else:
    url = f"https://github.com/{USERNAME}.png?size=460"
    data = urllib.request.urlopen(url).read()

# 2) Stop early if this is the same picture as last time
new_hash = hashlib.sha256(data).hexdigest()
old_hash = open(HASH_FILE).read().strip() if os.path.exists(HASH_FILE) else ""
if new_hash == old_hash and os.path.exists(OUTPUT):
    print("Profile picture unchanged - nothing to do")
    sys.exit()

# 3) Cut out the person and put them on a black background
photo = Image.open(io.BytesIO(data)).convert("RGB")
person = remove(photo, session=new_session("u2net_human_seg"))   # background becomes transparent
mask = np.array(person)[:, :, 3] > 128                           # True where the person is
black = Image.new("RGBA", person.size, (0, 0, 0, 255))
black.alpha_composite(person)

# 4) Grey + local contrast, then stretch the brightness so the face has detail
grey = cv2.cvtColor(np.array(black.convert("RGB")), cv2.COLOR_RGB2GRAY)
grey = cv2.createCLAHE(clipLimit=6.0, tileGridSize=(6, 6)).apply(grey)
low, high = np.percentile(grey[mask], (3, 97))
grey = np.clip((grey - low) / (high - low), 0, 1)
grey = 255 * grey * mask                                         # background stays black

# 5) Shrink to a grid of characters (rows are fewer because letters are tall)
rows = int(COLS * grey.shape[0] / grey.shape[1] * (CHAR_W / LINE_H))
small = np.array(Image.fromarray(grey.astype(np.uint8)).resize((COLS, rows)))

# 6) Brighter pixel = denser character
lines = []
for row in small:
    lines.append("".join(RAMP[int(((v / 255) ** 0.7) * (len(RAMP) - 1))] for v in row))

# 7) Write the SVG (each row fades in a little after the one above)
width = COLS * CHAR_W + 2 * PAD
height = rows * LINE_H + 2 * PAD
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}">',
    "<style>",
    f"text{{font-family:Consolas,Menlo,monospace;font-size:{CHAR_W / 0.6:.1f}px;font-weight:bold;fill:#e6edf3}}",
    ".r{animation:show .3s ease-out backwards}",
    "@keyframes show{from{opacity:0}to{opacity:1}}",
    "</style>",
    f'<rect width="{width:.0f}" height="{height:.0f}" rx="10" fill="#0d1117" stroke="#30363d"/>',
]
for i, line in enumerate(lines):
    y = PAD + (i + 1) * LINE_H - 2
    svg.append(
        f'<text class="r" x="{PAD}" y="{y:.1f}" xml:space="preserve" '
        f'textLength="{COLS * CHAR_W:.1f}" lengthAdjust="spacingAndGlyphs" '
        f'style="animation-delay:{i * 0.06:.2f}s">{escape(line)}</text>'
    )
svg.append("</svg>")
open(OUTPUT, "w", encoding="utf-8").write("\n".join(svg))
open(HASH_FILE, "w").write(new_hash)
print("Saved", OUTPUT)
