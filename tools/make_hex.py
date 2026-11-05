"""make_hex.py — draws the EEGB hex logos (main + one per course part) as SVG, then
rasterises them to PNG (1024 px and 256 px) with tools/svg2png.js (Node + sharp).

Run from the project root:  python tools/make_hex.py
"""
import math, os, subprocess, random

OUT = "assets/logos"
NAVY = "#12266A"; FRAME1 = "#1A4269"; FRAME2 = "#0F2E4D"; CREAM = "#FBF6EC"; GOLD = "#C99A3B"
SLATE = "#2D5272"; TEAL = "#3A7D8A"; OLIVE = "#A89A5A"; RUST = "#B5541A"
C = (512, 512)


def hexpts(cx, cy, r):
    return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in (-90, -30, 30, 90, 150, 210)]


def poly(p):
    return "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in p) + " Z"


def frame():
    return f'''<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
<stop offset="0" stop-color="{FRAME1}"/><stop offset="1" stop-color="{FRAME2}"/></linearGradient>
<clipPath id="clip"><path d="{poly(hexpts(*C, 372))}"/></clipPath></defs>
<path d="{poly(hexpts(*C, 490))}" fill="url(#g)" stroke="#2B4F75" stroke-width="3"/>
<path d="{poly(hexpts(*C, 428))}" fill="{CREAM}" stroke="#34587C" stroke-width="2"/>
<path d="{poly(hexpts(*C, 392))}" fill="none" stroke="{GOLD}" stroke-width="9"/>
<path d="{poly(hexpts(*C, 376))}" fill="none" stroke="{GOLD}" stroke-width="2.5" opacity=".75"/>'''


def wordmark(y=380, sub=None):
    # EEGB with a small gold globe-dot acting as a full stop between EE and GB
    s = (f'<text x="512" y="{y}" text-anchor="middle" font-family="Lora, Georgia, serif" font-weight="700" '
         f'font-size="150" letter-spacing="6" fill="{NAVY}">EEGB</text>'
         f'<line x1="330" y1="{y + 22}" x2="694" y2="{y + 22}" stroke="{GOLD}" stroke-width="6" stroke-linecap="round"/>'
         f'<circle cx="512" cy="{y + 22}" r="11" fill="{GOLD}"/>')
    if sub:
        s += (f'<text x="512" y="{y + 70}" text-anchor="middle" font-family="Lora, Georgia, serif" font-style="italic" '
              f'font-size="32" fill="{SLATE}">{sub}</text>')
    return s


def ground(col=OLIVE):
    return f'<path d="M120,792 C300,760 430,770 560,782 C700,795 800,782 900,772 L900,1000 L120,1000 Z" fill="{col}"/>'


def motif_main():
    # globe (meridians + parallels) with a gold growth line rising across it
    cx, cy, r = 512, 700, 210
    g = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{TEAL}" opacity=".22"/>'
    for k in (0.35, 0.7):
        g += f'<ellipse cx="{cx}" cy="{cy}" rx="{r * k:.0f}" ry="{r}" fill="none" stroke="{SLATE}" stroke-width="5" opacity=".7"/>'
    for dy in (-120, -60, 0, 60, 120):
        half = math.sqrt(max(r * r - dy * dy, 0))
        g += f'<line x1="{cx - half:.0f}" y1="{cy + dy}" x2="{cx + half:.0f}" y2="{cy + dy}" stroke="{SLATE}" stroke-width="5" opacity=".7"/>'
    g += f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{SLATE}" stroke-width="7"/>'
    pts = [(190, 760), (300, 720), (390, 735), (480, 660), (570, 680), (660, 590), (745, 552), (805, 520)]
    line = " ".join(f"{x},{y}" for x, y in pts)
    g += f'<polyline points="{line}" fill="none" stroke="{GOLD}" stroke-width="12" stroke-linecap="round" stroke-linejoin="round"/>'
    g += f'<circle cx="805" cy="520" r="15" fill="{GOLD}"/>'
    return f'<g clip-path="url(#clip)">{g}{ground()}</g>'


def motif_micro():
    # supply and demand cross with equilibrium point and price/quantity guides
    g = (f'<line x1="250" y1="530" x2="780" y2="790" stroke="{TEAL}" stroke-width="14" stroke-linecap="round"/>'   # demand
         f'<line x1="250" y1="790" x2="780" y2="520" stroke="{SLATE}" stroke-width="14" stroke-linecap="round"/>'  # supply
         f'<line x1="250" y1="657" x2="512" y2="657" stroke="{GOLD}" stroke-width="5" stroke-dasharray="14 10"/>'
         f'<line x1="512" y1="657" x2="512" y2="790" stroke="{GOLD}" stroke-width="5" stroke-dasharray="14 10"/>'
         f'<circle cx="512" cy="657" r="22" fill="{GOLD}" stroke="{CREAM}" stroke-width="6"/>')
    return f'<g clip-path="url(#clip)">{g}{ground()}</g>'


def motif_macro():
    # business cycle oscillating around a rising trend
    trend = f'<line x1="150" y1="770" x2="880" y2="560" stroke="{SLATE}" stroke-width="6" stroke-dasharray="18 12"/>'
    wave = " ".join(f"L{x},{770 - (x - 150) * 0.288 - 70 * math.sin((x - 150) / 62):.1f}" for x in range(150, 885, 5))
    g = trend + f'<path d="M150,770 {wave}" fill="none" stroke="{TEAL}" stroke-width="13" stroke-linecap="round"/>'
    # peak and trough markers
    for x in (150 + 62 * math.pi * 0.5 + 62 * 2 * math.pi, 150 + 62 * math.pi * 1.5 + 62 * 2 * math.pi):
        y = 770 - (x - 150) * 0.288 - 70 * math.sin((x - 150) / 62)
        g += f'<circle cx="{x:.0f}" cy="{y:.0f}" r="15" fill="{GOLD}" stroke="{CREAM}" stroke-width="5"/>'
    return f'<g clip-path="url(#clip)">{g}{ground()}</g>'


def motif_open():
    # globe with trade arcs linking nodes
    cx, cy, r = 512, 720, 200
    g = f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{SLATE}" opacity=".9"/>'
    for k in (0.4, 0.75):
        g += f'<ellipse cx="{cx}" cy="{cy}" rx="{r * k:.0f}" ry="{r}" fill="none" stroke="{CREAM}" stroke-width="3" opacity=".45"/>'
    for dy in (-100, 0, 100):
        half = math.sqrt(r * r - dy * dy)
        g += f'<line x1="{cx - half:.0f}" y1="{cy + dy}" x2="{cx + half:.0f}" y2="{cy + dy}" stroke="{CREAM}" stroke-width="3" opacity=".45"/>'
    nodes = [(250, 640), (420, 600), (600, 610), (780, 650), (520, 700)]
    arcs = [(0, 1), (1, 3), (0, 2), (2, 3), (4, 0), (4, 3)]
    for a, b in arcs:
        (x1, y1), (x2, y2) = nodes[a], nodes[b]
        mx, my = (x1 + x2) / 2, min(y1, y2) - 110
        g += f'<path d="M{x1},{y1} Q{mx:.0f},{my:.0f} {x2},{y2}" fill="none" stroke="{GOLD}" stroke-width="7" stroke-linecap="round"/>'
    for x, y in nodes:
        g += f'<circle cx="{x}" cy="{y}" r="16" fill="{GOLD}" stroke="{CREAM}" stroke-width="5"/>'
    return f'<g clip-path="url(#clip)">{g}{ground(TEAL)}</g>'


def motif_frontiers():
    # scenario fan (central path + widening band) beside a wind turbine
    g = ""
    xs = list(range(170, 600, 6))
    base = lambda x: 740 - (x - 170) * 0.25
    g += f'<path d="M170,740 ' + " ".join(f"L{x},{base(x):.1f}" for x in xs) + f'" fill="none" stroke="{SLATE}" stroke-width="11" stroke-linecap="round"/>'
    fx = list(range(450, 880, 6))
    top = " ".join(f"L{x},{base(x) - (x - 450) * 0.45:.1f}" for x in fx)
    bot = " ".join(f"L{x},{base(x) + (x - 450) * 0.40:.1f}" for x in reversed(fx))
    g += f'<path d="M450,{base(450):.1f} {top} {bot} Z" fill="{TEAL}" opacity=".35"/>'
    g += f'<path d="M450,{base(450):.1f} ' + " ".join(f"L{x},{base(x):.1f}" for x in fx) + f'" fill="none" stroke="{GOLD}" stroke-width="9" stroke-dasharray="20 12"/>'
    # turbine
    tx, ty = 330, 560
    g += f'<path d="M{tx - 9},{ty} L{tx - 16},800 L{tx + 16},800 L{tx + 9},{ty} Z" fill="{NAVY}"/>'
    for ang in (-90, 30, 150):
        a = math.radians(ang)
        x2, y2 = tx + 120 * math.cos(a), ty + 120 * math.sin(a)
        g += f'<line x1="{tx}" y1="{ty}" x2="{x2:.0f}" y2="{y2:.0f}" stroke="{NAVY}" stroke-width="16" stroke-linecap="round"/>'
    g += f'<circle cx="{tx}" cy="{ty}" r="16" fill="{GOLD}"/>'
    return f'<g clip-path="url(#clip)">{g}{ground()}</g>'


def badge(text):
    w = 30 + 15 * len(text)
    return (f'<g><rect x="{512 - w / 2:.0f}" y="168" width="{w}" height="44" rx="22" fill="{NAVY}"/>'
            f'<text x="512" y="199" text-anchor="middle" font-family="Calibri, Carlito, Arial, sans-serif" font-weight="700" '
            f'font-size="24" fill="{GOLD}" letter-spacing="3">{text}</text></g>')


def build(name, motif, sub, tab):
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1024 1024" width="1024" height="1024">'
           f'{frame()}{motif}{wordmark(375, sub)}{badge(tab)}</svg>')
    path = f"{OUT}/{name}.svg"
    open(path, "w", encoding="utf-8").write(svg)
    for size, suffix in ((1024, ""), (256, "_256")):
        subprocess.run(["node", "tools/svg2png.js", path, f"{OUT}/{name}{suffix}.png", str(size)], check=True)
    print("built", name)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    build("eegb_hex", motif_main(), "Economic Environment of Global Business", "MEMBA 14")
    build("eegb_hex_p1", motif_micro(), "Microeconomics &amp; Markets", "PART I")
    build("eegb_hex_p2", motif_macro(), "Macroeconomics, Policy &amp; Risk", "PART II")
    build("eegb_hex_p3", motif_open(), "Open Economy, Trade &amp; Geoeconomics", "PART III")
    build("eegb_hex_p4", motif_frontiers(), "Climate, Risk &amp; Corporate Strategy", "PART IV")
