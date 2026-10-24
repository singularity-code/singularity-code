"""5x7 pixel font, sprite helpers and the shared SVG wrapper."""

from themes import PALETTE

_GLYPHS = """
A 01110 10001 10001 11111 10001 10001 10001
B 11110 10001 10001 11110 10001 10001 11110
C 01111 10000 10000 10000 10000 10000 01111
D 11110 10001 10001 10001 10001 10001 11110
E 11111 10000 10000 11110 10000 10000 11111
F 11111 10000 10000 11110 10000 10000 10000
G 01111 10000 10000 10111 10001 10001 01111
H 10001 10001 10001 11111 10001 10001 10001
I 11111 00100 00100 00100 00100 00100 11111
J 00111 00010 00010 00010 00010 10010 01100
K 10001 10010 10100 11000 10100 10010 10001
L 10000 10000 10000 10000 10000 10000 11111
M 10001 11011 10101 10101 10001 10001 10001
N 10001 11001 10101 10011 10001 10001 10001
O 01110 10001 10001 10001 10001 10001 01110
P 11110 10001 10001 11110 10000 10000 10000
Q 01110 10001 10001 10001 10101 10010 01101
R 11110 10001 10001 11110 10100 10010 10001
S 01111 10000 10000 01110 00001 00001 11110
T 11111 00100 00100 00100 00100 00100 00100
U 10001 10001 10001 10001 10001 10001 01110
V 10001 10001 10001 10001 10001 01010 00100
W 10001 10001 10001 10101 10101 10101 01010
X 10001 10001 01010 00100 01010 10001 10001
Y 10001 10001 01010 00100 00100 00100 00100
Z 11111 00001 00010 00100 01000 10000 11111
0 01110 10001 10011 10101 11001 10001 01110
1 00100 01100 00100 00100 00100 00100 01110
2 01110 10001 00001 00010 00100 01000 11111
3 11110 00001 00001 01110 00001 00001 11110
4 00010 00110 01010 10010 11111 00010 00010
5 11111 10000 11110 00001 00001 10001 01110
6 00110 01000 10000 11110 10001 10001 01110
7 11111 00001 00010 00100 01000 01000 01000
8 01110 10001 10001 01110 10001 10001 01110
9 01110 10001 10001 01111 00001 00010 01100
. 00000 00000 00000 00000 00000 01100 01100
, 00000 00000 00000 00000 01100 00100 01000
: 00000 01100 01100 00000 01100 01100 00000
/ 00001 00001 00010 00100 01000 10000 10000
- 00000 00000 00000 11111 00000 00000 00000
" 01010 01010 01010 00000 00000 00000 00000
' 00100 00100 01000 00000 00000 00000 00000
! 00100 00100 00100 00100 00100 00000 00100
? 01110 10001 00001 00010 00100 00000 00100
+ 00000 00100 00100 11111 00100 00100 00000
# 01010 01010 11111 01010 11111 01010 01010
( 00010 00100 01000 01000 01000 00100 00010
) 01000 00100 00010 00010 00010 00100 01000
& 01100 10010 10100 01000 10101 10010 01101
> 01000 00100 00010 00001 00010 00100 01000
< 00010 00100 01000 10000 01000 00100 00010
_ 00000 00000 00000 00000 00000 00000 11111
= 00000 00000 11111 00000 11111 00000 00000
♥ 00000 01010 11111 11111 01110 00100 00000
★ 00100 00100 11111 01110 01110 11011 00000
▶ 01000 01100 01110 01111 01110 01100 01000
· 00000 00000 00000 01100 01100 00000 00000
"""

FONT = {" ": ["00000"] * 7}
for _line in _GLYPHS.strip().splitlines():
    _ch, *_rows = _line.split()
    FONT[_ch] = _rows


def text_width(text, px):
    return (len(text) * 6 - 1) * px


def text_path(text, px, x, y, anchor="start"):
    """Path data for `text` with its top-left at (x, y); anchor shifts it like SVG text-anchor."""
    text = text.upper()
    if anchor == "middle":
        x -= text_width(text, px) / 2
    elif anchor == "end":
        x -= text_width(text, px)
    d = []
    for i, ch in enumerate(text):
        for r, row in enumerate(FONT.get(ch, FONT["?"])):
            c = 0
            while c < 5:
                if row[c] != "1":
                    c += 1
                    continue
                start = c
                while c < 5 and row[c] == "1":
                    c += 1
                d.append(f"M{x + (i * 6 + start) * px:g} {y + r * px:g}h{(c - start) * px:g}v{px:g}h{-(c - start) * px:g}z")
    return "".join(d)


def text(t, px, x, y, fill, anchor="start", extra=""):
    return f'<path d="{text_path(t, px, x, y, anchor)}" fill="{fill}"{extra}/>'


def sprite_path(rows, px, x=0, y=0, on="1"):
    """Path data for every cell of `rows` equal to `on`, merging horizontal runs."""
    d = []
    for r, row in enumerate(rows):
        c = 0
        while c < len(row):
            if row[c] != on:
                c += 1
                continue
            start = c
            while c < len(row) and row[c] == on:
                c += 1
            d.append(f"M{x + start * px:g} {y + r * px:g}h{(c - start) * px:g}v{px:g}h{-(c - start) * px:g}z")
    return "".join(d)


def sprite(rows, px, x, y, colors):
    """Multi-colour sprite: `colors` maps each cell character to a fill."""
    return "".join(f'<path d="{sprite_path(rows, px, x, y, ch)}" fill="{fill}"/>' for ch, fill in colors.items())


def frame(x, y, w, h, outer, inner, fill, step=6):
    """Pixel-art window frame with notched corners and a double border."""
    def notched(x, y, w, h, s):
        return (f"M{x + s} {y}h{w - 2 * s}v{s}h{s}v{h - 2 * s}h{-s}v{s}h{-(w - 2 * s)}"
                f"v{-s}h{-s}v{-(h - 2 * s)}h{s}z")
    return (f'<path d="{notched(x, y, w, h, step)}" fill="{outer}"/>'
            f'<path d="{notched(x + step, y + step, w - 2 * step, h - 2 * step, step)}" fill="{inner}"/>'
            f'<path d="{notched(x + 2 * step, y + 2 * step, w - 4 * step, h - 4 * step, step)}" fill="{fill}"/>')


def svg(w, h, label, body, style="", defs=""):
    scanlines = f"""<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse">
      <rect width="4" height="2" fill="black" opacity="{PALETTE['scan']}"/>
    </pattern>"""
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{label}">
  <defs>{scanlines}{defs}</defs>
  <style>{style}</style>
{body}
  <rect width="{w}" height="{h}" fill="url(#scan)" pointer-events="none"/>
</svg>
"""
