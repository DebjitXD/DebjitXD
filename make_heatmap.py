# make_heatmap.py - downloads your contribution calendar and draws an animated SVG.
import re
import sys
from datetime import date

import requests
from bs4 import BeautifulSoup

USERNAME = "DebjitXD"          # <- your GitHub username
OUTPUT = "contrib-heatmap.svg"  # <- the file this script creates

# One colour per level: 0 = no contributions ... 4 = most contributions
COLOURS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

BOX = 12   # size of each square (pixels)
GAP = 4    # space between squares

# 1) Download GitHub's public calendar page (no token needed)
url = f"https://github.com/users/{USERNAME}/contributions"
html = requests.get(url, timeout=30).text
soup = BeautifulSoup(html, "html.parser")

# 2) Read the "N contributions in the last year" heading
heading = soup.find("h2").get_text(" ", strip=True)
total = re.search(r"([\d,]+)\s+contributions", heading).group(1)

# 3) Read every day: its date and its level (0-4)
days = []
for cell in soup.select("td.ContributionCalendar-day"):
    d = date.fromisoformat(cell["data-date"])
    days.append((d, int(cell["data-level"])))
days.sort()
if not days:
    sys.exit("No data found - is the username right?")

# 4) Work out where each square goes (column = week, row = weekday)
first = days[0][0]
squares = []
for d, level in days:
    row = (d.weekday() + 1) % 7                      # Sunday = row 0
    col = ((d - first).days + (first.weekday() + 1) % 7) // 7
    squares.append((col, row, level))

width = (max(c for c, _, _ in squares) + 1) * (BOX + GAP) + 20
height = 7 * (BOX + GAP) + 50

# 5) Build the SVG text
svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}">',
    "<style>",
    # every square starts invisible/small, then pops in once and stays
    "rect.b{animation:pop .5s ease-out backwards}",
    "@keyframes pop{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:scale(1)}}",
    "text{font-family:monospace;font-size:12px;fill:#8b949e}",
    "</style>",
]
for col, row, level in squares:
    x = 10 + col * (BOX + GAP)
    y = 10 + row * (BOX + GAP)
    delay = (col + row) * 0.02   # diagonal wave: later squares start later
    svg.append(
        f'<rect class="b" x="{x}" y="{y}" width="{BOX}" height="{BOX}" rx="3" '
        f'fill="{COLOURS[level]}" style="animation-delay:{delay:.2f}s;'
        f'transform-box:fill-box;transform-origin:center"/>'
    )
svg.append(f'<text x="10" y="{height - 12}">{total} contributions in the last year</text>')
svg.append("</svg>")

# 6) Save it
with open(OUTPUT, "w") as f:
    f.write("\n".join(svg))
print("Saved", OUTPUT)
