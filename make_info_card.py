# make_info_card.py - draws a terminal-style info card as an animated SVG.
from html import escape

OUTPUT = "info-card.svg"   # the file this script creates

# Edit these lines to change what the card says: (label, value, colour)
ROWS = [
    ("Name",      "Debjit",                          "#ffd60a"),
    ("Role",      "B.Tech ECE @ IEM Kolkata",        "#00e5ff"),
    ("IEEE",      "Secretary, EDS IEM Student Branch", "#ff4fd8"),
    ("Now",       "10 projects in 10 days",          "#39ff88"),
    ("Stack",     "ESP32 | Python | Verilog | TCAD", "#ff9f1c"),
    ("Focus",     "Embedded | VLSI | AI/ML",         "#00e5ff"),
    ("Highlight", "HTA Makers DIY - Top 20 finalist", "#ffd60a"),
]

WIDTH = 490
LINE_HEIGHT = 26
HEIGHT = 80 + len(ROWS) * LINE_HEIGHT   # grows with the number of rows

svg = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}">',
    "<style>",
    "text{font-family:Consolas,Menlo,monospace;font-size:14px}",
    # each line starts invisible and slightly left, then slides in once
    ".l{animation:in .5s ease-out backwards}",
    "@keyframes in{from{opacity:0;transform:translateX(-12px)}to{opacity:1;transform:translateX(0)}}",
    "</style>",
    # the window background and title bar
    f'<rect width="{WIDTH}" height="{HEIGHT}" rx="10" fill="#0d1117" stroke="#30363d"/>',
    f'<rect width="{WIDTH}" height="30" rx="10" fill="#161b22"/>',
    '<circle cx="18" cy="15" r="5" fill="#ff5f56"/>',
    '<circle cx="36" cy="15" r="5" fill="#ffbd2e"/>',
    '<circle cx="54" cy="15" r="5" fill="#27c93f"/>',
    # the command line
    '<text x="20" y="58" fill="#8b949e" class="l" style="animation-delay:0s">debjit@github ~ $ neofetch</text>',
]

# one <text> line per row, each appearing 0.3s after the one before
for i, (label, value, colour) in enumerate(ROWS):
    y = 90 + i * LINE_HEIGHT
    delay = 0.5 + i * 0.3
    svg.append(
        f'<g class="l" style="animation-delay:{delay:.1f}s">'
        f'<text x="20" y="{y}" fill="{colour}" font-weight="bold">{escape(label)}</text>'
        f'<text x="125" y="{y}" fill="#e6edf3">{escape(value)}</text>'
        f'</g>'
    )

svg.append("</svg>")

with open(OUTPUT, "w", encoding="utf-8") as f:
    f.write("\n".join(svg))
print("Saved", OUTPUT)
