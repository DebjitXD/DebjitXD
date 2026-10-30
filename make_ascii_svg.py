# make_ascii_svg.py - turns a photo into a self-typing ASCII portrait (SVG).
import sys
from html import escape

import numpy as np
from PIL import Image

PHOTO = sys.argv[1] if len(sys.argv) > 1 else "photo.jpg"  # your photo file
OUTPUT = "ascii-portrait.svg"                              # file we create

COLS = 100         # characters per row (more = more detail)
CHAR_W = 3.5       # width of one character in pixels
LINE_H = 7.0       # height of one row in pixels (about 2x the width)
PAD = 10           # empty space around the portrait

RAMP = " .`:-=+*cs#%@"   # dark/empty (sparse) -> bright (dense)

# 1) Open the prepared photo (grey, black background)
img = Image.open(PHOTO).convert("L")

# 2) Shrink it to a grid of COLS x rows (rows are fewer because letters are tall)
rows = int(COLS * img.height / img.width * (CHAR_W / LINE_H))
img = img.resize((COLS, rows))
pixels = np.array(img)

# 3) Turn each pixel's brightness into a character from RAMP
lines = []
for row in pixels:
    line = ""
    for value in row:
        shade = value / 255                          # 0 = black, 1 = white
        index = int(shade * (len(RAMP) - 1))         # brighter -> denser character
        line += RAMP[index]
    lines.append(line)

# 4) Build the SVG
width = COLS * CHAR_W + 2 * PAD
height = rows * LINE_H + 2 * PAD
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}">',
    "<style>",
    f"text{{font-family:Consolas,Menlo,monospace;font-size:{CHAR_W / 0.6:.1f}px;fill:#c9d1d9}}",
    # each row starts invisible, then fades in once (so the portrait "prints")
    ".r{animation:show .3s ease-out backwards}",
    "@keyframes show{from{opacity:0}to{opacity:1}}",
    "</style>",
    f'<rect width="{width:.0f}" height="{height:.0f}" rx="10" fill="#0d1117" stroke="#30363d"/>',
]
for i, line in enumerate(lines):
    y = PAD + (i + 1) * LINE_H - 2
    delay = i * 0.06    # each row starts 0.06s after the previous one
    svg.append(
        f'<text class="r" x="{PAD}" y="{y:.1f}" xml:space="preserve" '
        f'textLength="{COLS * CHAR_W:.1f}" lengthAdjust="spacingAndGlyphs" '
        f'style="animation-delay:{delay:.2f}s">{escape(line)}</text>'
    )
svg.append("</svg>")

# 5) Save it
with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print("Saved", OUTPUT, f"({COLS} x {rows} characters)")
