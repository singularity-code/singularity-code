"""Dune scenes: the Arrakis title screen and the sandworm-vs-harvesters game with live stats."""
import math

from pixel import PALETTE as P, frame, sprite, sprite_path, svg, text

W = 1000

SAND = {"light": "#f2d7a6", "mid": "#e2b77c", "deep": "#c98f52", "dark": "#a8683a", "rust": "#8a4a22"}

WORM_COLORS = {"o": "#5a3a1f", "t": "#fff3d6", "m": "#2a160b", "p": "#b5764a",
               "h": "#ddb083", "b": "#c99263", "s": "#9c6a40", "r": "#a8683a"}
WORM_PX = 4
WORM_SEGMENTS = 14


def _disc(radius, head=False, ring=False):
    """Round pixel segment; the head is a maw ringed with teeth, body segments are shaded."""
    rows = []
    for y in range(-radius, radius + 1):
        row = ""
        for x in range(-radius, radius + 1):
            d = math.hypot(x, y)
            if d > radius + 0.3:
                row += "."
            elif d > radius - 0.7:
                row += "o"
            elif head:
                row += "m" if d < radius * 0.42 else ("t" if d < radius * 0.62 and (x + y) % 2 == 0 else
                                                      "m" if d < radius * 0.62 else "p")
            elif ring:
                row += "r"
            else:
                row += "h" if x + y < -radius * 0.5 else ("s" if x + y > radius * 0.6 else "b")
        rows.append(row)
    return rows


def _breach(uid, cx, ground, t_start, loop, span, height, duration=1.6, lag=0.055):
    """A worm arcing out of the sand around cx: segments trail the head along one parabola.

    Returns (css, svg). Everything below `ground` must be clipped by the caller.
    """
    pct = lambda t: f"{min(max(t, 0), loop) / loop * 100:.3f}%"

    def at(u):
        return cx + (u - 0.5) * 2 * span, ground + 34 - height * 4 * u * (1 - u)

    css, shapes = [], []
    for k in reversed(range(WORM_SEGMENTS)):
        radius = round(7 - 4 * k / (WORM_SEGMENTS - 1))
        rows = _disc(radius, head=k == 0, ring=k % 3 == 2)
        size = len(rows) * WORM_PX
        frames = []
        for step in range(21):
            u = step / 20
            x, y = at(u)
            frames.append(f"{pct(t_start + (u + k * lag) * duration)} {{ transform: translate({x - size / 2:.1f}px, {y - size / 2:.1f}px); }}")
        x0, y0 = at(0)
        x1, y1 = at(1)
        css.append(f"@keyframes {uid}s{k} {{ 0% {{ transform: translate({x0 - size / 2:.1f}px, {y0 - size / 2:.1f}px); }} "
                   f"{' '.join(frames)} 100% {{ transform: translate({x1 - size / 2:.1f}px, {y1 - size / 2:.1f}px); }} }}")
        shapes.append(f'<g style="animation: {uid}s{k} {loop:g}s linear infinite">'
                      f'{sprite(rows, WORM_PX, 0, 0, WORM_COLORS)}</g>')
    return css, "".join(shapes)


HARVESTER = ["....kkkkkkkk........", "...kyyyyyyyyk.......", "..kyywwyyyyyykkkk...", "..kyywwyyyyyyyyyyk..",
             ".kyyyyyyyyyyyyyyyyk.", "kkkkkkkkkkkkkkkkkkkk", "kgkgkgkgkgkgkgkgkgkk", "kkkkkkkkkkkkkkkkkkkk"]
HARVESTER_COLORS = {"k": "#3d2914", "y": "#d9902c", "w": "#7fc8ff", "g": "#8a6a45"}

THOPTER_A = ["wwwwwwwww..wwwwwwwww", ".........kk.........", "....kkkkkkkkkkkk....",
             "...kbbbccbbbbbbbkkkk", "....kkkkkkkkkkkk....", ".....k........k....."]
THOPTER_B = ["....................", "..wwwwwwwkkwwwwwww..", "....kkkkkkkkkkkk....",
             "...kbbbccbbbbbbbkkkk", "....kkkkkkkkkkkk....", ".....k........k....."]
THOPTER_COLORS = {"w": "#5a4636", "k": "#3d2914", "b": "#9a8468", "c": "#7fc8ff"}

MOUND = ["...111111...", ".1111111111.", "111111111111"]


def _dune(seed, base, amp, step=8, width=W):
    """Stair-stepped dune ridge (pixel look) as a closed path down to the bottom edge."""
    pts = []
    for x in range(0, width + step, step):
        y = base - amp * (0.6 * math.sin(x / 140 + seed) + 0.4 * math.sin(x / 57 + seed * 2.3))
        pts.append((x, round(y / 4) * 4))
    d = f"M0 {pts[0][1]}"
    for x, y in pts[1:]:
        d += f"H{x}V{y}"
    return d + f"V2000H0Z"


def _thopter(x, y, px, cls):
    a = f'<g class="fa">{sprite(THOPTER_A, px, x, y, THOPTER_COLORS)}</g>'
    b = f'<g class="fb">{sprite(THOPTER_B, px, x, y, THOPTER_COLORS)}</g>'
    return f'<g class="{cls}">{a}{b}</g>'


FLAP = """.fa { animation: fa .3s steps(1) infinite; } @keyframes fa { 50% { opacity: 0; } }
    .fb { opacity: 0; animation: fb .3s steps(1) infinite; } @keyframes fb { 50% { opacity: 1; } }
    .blink { animation: blink 1.1s steps(1) infinite; } @keyframes blink { 50% { opacity: 0; } }"""


def banner():
    H = 320
    worm_x, ground = 170, 262
    worm_css, worm = _breach("bw", worm_x, ground, 2.5, 9, span=150, height=150)
    worm_css = "\n    ".join(worm_css)
    defs = f"""
    <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fdf3e1"/><stop offset="0.6" stop-color="#f7dcae"/><stop offset="1" stop-color="#efb878"/>
    </linearGradient>
    <clipPath id="above"><rect width="{W}" height="{ground}"/></clipPath>"""
    style = f"""{FLAP}
    {worm_css}
    .spray {{ opacity: 0; animation: spray 9s infinite; }}
    @keyframes spray {{ 0%, 26% {{ opacity: 0; transform: translateY(0); }} 29% {{ opacity: 1; }} 42% {{ opacity: 0; transform: translateY(-50px); }} 100% {{ opacity: 0; }} }}
    .fly {{ animation: fly 16s linear infinite; }}
    @keyframes fly {{ from {{ transform: translate({W + 40}px, 0); }} to {{ transform: translate(-200px, 30px); }} }}
    .haze {{ animation: haze 12s linear infinite; }}
    @keyframes haze {{ from {{ transform: translateX(0); }} to {{ transform: translateX(-200px); }} }}"""
    spray = "".join(
        f'<rect x="{worm_x - 150 + dx}" y="{ground - 6 - abs(dx) // 5}" width="6" height="6" fill="{SAND["deep"]}"/>'
        for dx in range(-40, 41, 10)
    )
    haze = "".join(f'<rect x="{x}" y="{y}" width="{w}" height="3" fill="#fff" opacity=".35"/>'
                   for x, y, w in [(60, 150, 180), (420, 175, 260), (760, 140, 160), (1060, 165, 200), (300, 200, 120)])
    body = f"""
  <rect width="{W}" height="{H}" fill="url(#sky)"/>
  <circle cx="830" cy="150" r="62" fill="#fff6dc"/>
  <circle cx="830" cy="150" r="76" fill="#fff6dc" opacity=".35"/>
  <circle cx="150" cy="70" r="16" fill="#fffaf0" opacity=".8"/>
  <circle cx="196" cy="96" r="9" fill="#fffaf0" opacity=".65"/>
  <g class="haze">{haze}</g>
  <path d="{_dune(0.3, 205, 26)}" fill="{SAND['light']}"/>
  <path d="{_dune(1.7, 232, 22)}" fill="{SAND['mid']}"/>
  <g clip-path="url(#above)">
    {worm}
  </g>
  <g class="spray">{spray}</g>
  <path d="{_dune(3.1, 268, 14)}" fill="{SAND['deep']}"/>
  {_thopter(0, 110, 4, "fly")}
  {text("SINGULARITY-CODE", 6, W / 2 + 4, 38, "#e46a1c", "middle")}
  {text("SINGULARITY-CODE", 6, W / 2, 34, P['ink'], "middle")}
  {text("THE CODE MUST FLOW", 3, W / 2, 98, SAND['rust'], "middle")}
  <g class="blink"><rect x="{W / 2 - 115:g}" y="276" width="230" height="37" fill="{P['ink']}" opacity="0.8"/>{text("PRESS START", 3, W / 2, 284, "#fbf3e2", "middle")}</g>"""
    return svg(W, H, "SINGULARITY-CODE - The code must flow - Press start", body, style, defs)


def game(stats):
    """Harvesters gather spice; a sandworm ripples under the sand and swallows two of them."""
    H, T, ground = 480, 12.0, 390
    pct = lambda t: f"{t / T * 100:.3f}%"
    harvesters = [230, 500, 770]
    # (harvester index eaten, time the jaws close, where the ripple starts)
    attacks = [(0, 3.6, -60), (2, 8.6, 230)]
    hw = len(HARVESTER[0]) * 4
    style = [FLAP]
    parts = []

    for i, cx in enumerate(harvesters):
        plume = "".join(
            f'<rect class="spice" x="{cx - hw / 2 + 6 + k * 7}" y="{ground - 40}" width="6" height="6" fill="#e46a1c" style="animation-delay:-{k * 0.35:.2f}s"/>'
            for k in range(4)
        )
        eaten = next((a for a in attacks if a[0] == i), None)
        attr = ""
        if eaten:
            t = eaten[1]
            style.append(f"@keyframes h{i} {{ 0%, {pct(t - 0.15)} {{ opacity: 1; }} {pct(t - 0.14)}, 100% {{ opacity: 0; }} }}")
            attr = f' style="animation: h{i} {T:g}s linear infinite"'
        parts.append(f'<g{attr}>{plume}{sprite(HARVESTER, 4, cx - hw / 2, ground - 32, HARVESTER_COLORS)}</g>')
    style.append(".spice { animation: spice 1.4s linear infinite; } "
                 "@keyframes spice { 0% { transform: translateY(0); opacity: 1; } 100% { transform: translateY(-46px); opacity: 0; } }")

    span, duration = 140, 1.6
    for n, (i, t, start) in enumerate(attacks):
        cx = harvesters[i]
        # The head passes over the harvester halfway through the breach.
        t_breach = t - duration / 2
        t_rip, t_rise, t_dive = t - 3.0, t_breach, t_breach + 0.8
        mound_w = len(MOUND[0]) * 5
        style.append(
            f"@keyframes r{n} {{ 0%, {pct(t_rip)} {{ opacity: 0; transform: translateX({start - mound_w / 2}px); }} "
            f"{pct(t_rip + 0.01)} {{ opacity: 1; transform: translateX({start - mound_w / 2}px); }} "
            f"{pct(t_rise)} {{ opacity: 1; transform: translateX({cx - span - mound_w / 2}px); }} "
            f"{pct(t_rise + 0.01)}, 100% {{ opacity: 0; transform: translateX({cx - span - mound_w / 2}px); }} }}"
        )
        parts.append(f'<path d="{sprite_path(MOUND, 5, 0, ground - 15)}" fill="{SAND["dark"]}" style="opacity:0; animation: r{n} {T:g}s linear infinite"/>')
        worm_css, worm = _breach(f"w{n}", cx, ground, t_breach, T, span=span, height=210, duration=duration)
        style.extend(worm_css)
        parts.append(f'<g clip-path="url(#above)">{worm}</g>')
        style.append(f"@keyframes s{n} {{ 0%, {pct(t_rise)} {{ opacity: 0; transform: translateY(0); }} "
                     f"{pct(t_rise + 0.1)} {{ opacity: 1; }} {pct(t_dive)} {{ opacity: 0; transform: translateY(-70px); }} 100% {{ opacity: 0; }} }}")
        spray = "".join(f'<rect x="{cx - span + 10 + dx}" y="{ground - 8 - abs(dx) // 5}" width="7" height="7" fill="{SAND["deep"]}"/>'
                        for dx in range(-42, 43, 14))
        parts.append(f'<g style="opacity:0; animation: s{n} {T:g}s infinite">{spray}</g>')

    style.append(f".fly {{ animation: fly {T:g}s linear infinite; }} "
                 f"@keyframes fly {{ from {{ transform: translate({W}px, 0); }} to {{ transform: translate(-120px, 20px); }} }}")

    hud = [
        text("SPICE · 12 MONTHS", 2, 50, 30, P["ink"]),
        text(f"{stats['contrib_year']:05d}", 3, 50, 50, P["pink"]),
        text("TOTAL SPICE · ALL TIME", 2, W / 2, 30, P["ink"], "middle"),
        text(f"{stats['contrib_all']:05d}", 3, W / 2, 50, P["pink"], "middle"),
        text("YEARS ON ARRAKIS", 2, W - 50, 30, P["ink"], "end"),
        text(f"{stats['years']:02d}", 3, W - 50, 50, P["pink"], "end"),
    ]
    footer = [
        text(f"REPOS {stats['repos']:03d}", 2, 50, ground + 58, P["ink"]),
        f'<g class="blink">{text("SPICE = GITHUB CONTRIBUTIONS · UPDATED DAILY", 2, W / 2, ground + 58, SAND["rust"], "middle")}</g>',
        text(f"★ {stats['stars']:03d}", 2, W - 50, ground + 58, P["yellow"], "end"),
    ]
    defs = f"""
    <linearGradient id="gsky" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#fdf3e1"/><stop offset="1" stop-color="#f3cf98"/>
    </linearGradient>
    <clipPath id="above"><rect width="{W}" height="{ground}"/></clipPath>
    <clipPath id="screen"><rect x="12" y="12" width="{W - 24}" height="{H - 24}"/></clipPath>"""
    content = f"""
  <rect width="{W}" height="{H}" fill="{P['night']}"/>
  {frame(4, 4, W - 8, H - 8, P['purple'], P['night'], "url(#gsky)", 4)}
  <circle cx="860" cy="130" r="40" fill="#fff6dc"/>
  <path d="{_dune(0.9, 300, 30, width=W - 24)}" transform="translate(12 0)" fill="{SAND['light']}"/>
  <path d="{_dune(2.4, 345, 22, width=W - 24)}" transform="translate(12 0)" fill="{SAND['mid']}"/>
  <rect x="12" y="{ground}" width="{W - 24}" height="{H - ground - 12}" fill="{SAND['deep']}"/>
  <rect x="12" y="{ground}" width="{W - 24}" height="4" fill="{SAND['dark']}"/>
  <g clip-path="url(#screen)">{_thopter(0, 95, 3, "fly")}</g>
  {"".join(parts)}
  {"".join(hud)}
  {"".join(footer)}"""
    label = (f"Sandworm attract mode. Spice harvested: {stats['contrib_year']} contributions in the last 12 months, "
             f"{stats['contrib_all']} all time, {stats['repos']} public repos, {stats['stars']} stars.")
    return svg(W, H, label, content, "\n    ".join(style), defs)
