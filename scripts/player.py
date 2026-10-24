"""PLAYER 1 character sheet: pixel avatar, profile lines and stat bars that fill up on load."""
from pixel import PALETTE as P, frame, sprite, svg, text, text_width
from themes import CONTENT

W, H = 1000, 420

# Hooded, stillsuit-masked, blue-in-blue eyes.
AVATAR = [
    "................",
    ".....kkkkkk.....",
    "....khhhhhhk....",
    "...khhhhhhhhk...",
    "..khhhhhhhhhhk..",
    "..khhsssssshhk..",
    "..khsggssggshk..",
    "..khsgwssgwshk..",
    "..khsssssssshk..",
    "..khmmmmmmmmhk..",
    "..khmmtmmtmmhk..",
    "...khmmmmmmhk...",
    "...khhhhhhhhk...",
    "..kppppppppppk..",
    ".kppdppppppdppk.",
    ".kddddddddddddk.",
]

# (label, filled segments out of 20, palette key, note)
STATS = [
    ("LEAD", 19, "yellow", "TEAM BUFF"),
    ("WEB", 18, "cyan", "REACT / VUE"),
    ("API", 16, "pink", "NODE / SPRING"),
    ("APP", 14, "purple", "SWIFT / RN"),
    ("GAME", 8, "green", "UE5 / GODOT"),
]


def render():
    seg, gap = 13, 3
    colors = {"k": P["ink"], "h": P["hair"], "s": P["skin"], "g": P["cyan"], "w": "#ffffff",
              "p": P["suit"], "d": P["shade"], "m": P["mask"], "t": P["ink"]}
    avatar = sprite(AVATAR, 10, 60, 105, colors)
    info = [("ID", "CL"), ("CLASS", CONTENT["class"]), ("WORLD", "SYDNEY, AU"), ("MOTTO", '"MAKE IT SIMPLE AND BETTER."')]
    info = "".join(
        text(k, 3, 300, 100 + i * 34, P["dim"]) + text(v, 3, 420, 100 + i * 34, P["white"])
        for i, (k, v) in enumerate(info)
    )
    bars = []
    for i, (label, filled, key, note) in enumerate(STATS):
        color = P[key]
        y = 255 + i * 26
        bars.append(text(label, 2, 300, y + 2, P["dim"]))
        for s in range(20):
            x = 370 + s * (seg + gap)
            if s < filled:
                delay = 0.4 + i * 0.25 + s * 0.04
                bars.append(f'<rect class="seg" x="{x}" y="{y}" width="{seg}" height="16" fill="{color}" style="animation-delay:{delay:.2f}s"/>')
            else:
                bars.append(f'<rect x="{x}" y="{y}" width="{seg}" height="16" fill="{P["track"]}"/>')
        bars.append(text(f"{filled * 5:>3}", 2, 700, y + 2, P["white"]))
        bars.append(text(note, 2, 760, y + 2, color))
    new_badge = f'<g class="blink">{text("NEW!", 2, 760 + text_width(STATS[-1][3], 2) + 16, 255 + 4 * 26 + 2, P["yellow"])}</g>'

    style = """
    .seg { opacity: 0; animation: on .05s steps(1) forwards; }
    @keyframes on { to { opacity: 1; } }
    .bob { animation: bob 1.2s steps(1) infinite; }
    @keyframes bob { 50% { transform: translateY(-6px); } }
    .blink { animation: blink 1s steps(1) infinite; }
    @keyframes blink { 50% { opacity: 0; } }"""
    body = f"""
  <rect width="{W}" height="{H}" fill="{P['night']}"/>
  {frame(10, 10, W - 20, H - 20, P['cyan'], P['pink'], P['panel'])}
  {text("PLAYER 1", 4, 300, 42, P['yellow'])}
  <g class="blink">{text("▶", 4, 270, 42, P['yellow'])}</g>
  {frame(48, 80, 184, 214, P['purple'], P['ink'], P['well'], 4)}
  <g class="bob">{avatar}</g>
  {text("LV.99", 3, 140, 312, P['cyan'], "middle")}
  {text("♥♥♥", 3, 140, 340, P['pink'], "middle")}
  {info}
  {"".join(bars)}
  {new_badge}"""
    return svg(W, H, f"PLAYER 1 - CL, {CONTENT['class'].title()}, Sydney. Motto: Make it simple and better.", body, style)
