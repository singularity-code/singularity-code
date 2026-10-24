"""RPG inventory grid of the tech stack, with a selection cursor that tours a few items."""
import base64
import pathlib

from pixel import PALETTE as P, frame, svg, text
from themes import CONTENT

W, H = 1000, 620
SLOT, GAP = 60, 8
STEP = SLOT + GAP

# (heading, palette key for the border, icon ids in scripts/icons/)
ROWS = [
    ("WEAPONS · LANGUAGES", "cyan", ["ts", "js", "py", "java", "cs", "c", "cpp", "swift", "html", "css", "powershell"]),
    ("SPELLS · FRONTEND", "pink", ["react", "vue", "redux", "styledcomponents", "jquery"]),
    ("ARMOR · BACKEND & DATA", "yellow", ["nodejs", "express", "spring", "prisma", "mysql", "postgres", "mongodb"]),
    ("TOOLS · CLOUD & CRAFT", "purple", ["aws", "azure", "docker", "maven", "gradle", "git", "github", "gitlab", "bitbucket", "figma", "unreal"]),
]

STOP_SECONDS = 2.5


# Icons from skillicons.dev, vendored so builds never depend on that service.
ICONS = pathlib.Path(__file__).resolve().parent / "icons"


def _icon(name):
    return "data:image/svg+xml;base64," + base64.b64encode((ICONS / f"{name}.svg").read_bytes()).decode()


def render():
    TOUR = CONTENT["tour"]  # items the cursor visits: (icon id, name, flavour text)
    widest = max(len(ids) for _, _, ids in ROWS)
    x0 = (W - (widest * STEP - GAP)) // 2
    slots, positions = [], {}
    y = 82
    for heading, key, ids in ROWS:
        color = P[key]
        slots.append(text(heading, 2, x0, y, color))
        y += 22
        for i, name in enumerate(ids):
            x = x0 + i * STEP
            positions[name] = (x, y)
            slots.append(frame(x, y, SLOT, SLOT, color, P["ink"], P["well"], 3))
            slots.append(f'<image href="{_icon(name)}" x="{x + 9}" y="{y + 9}" width="{SLOT - 18}" height="{SLOT - 18}"/>')
        y += SLOT + 22

    # Cursor jumps between items; each description is visible only while the cursor rests on its item.
    n = len(TOUR)
    pct = lambda k: f"{k * 100 / n:g}%"
    cursor_frames = " ".join(
        f"{pct(k)} {{ transform: translate({positions[item][0] - 6}px, {positions[item][1] - 6}px); }}"
        for k, (item, _, _) in enumerate(TOUR)
    ) + f" 100% {{ transform: translate({positions[TOUR[-1][0]][0] - 6}px, {positions[TOUR[-1][0]][1] - 6}px); }}"
    desc_frames = "".join(
        f"@keyframes d{k} {{ 0% {{ opacity: {1 if k == 0 else 0}; }} {pct(k)} {{ opacity: 1; }} {pct(k + 1)} {{ opacity: 0; }} 100% {{ opacity: 0; }} }}\n"
        for k in range(n)
    )
    total = n * STOP_SECONDS
    c = SLOT + 12
    corner = 14
    cursor = (f'<path class="cursor" fill="none" stroke="{P["cursor"]}" stroke-width="4" d="'
              f"M0 {corner}V0H{corner} M{c - corner} 0H{c}V{corner} M{c} {c - corner}V{c}H{c - corner} M{corner} {c}H0V{c - corner}\"/>")

    panel_y = y + 4
    descs = "".join(
        f'<g style="animation: d{k} {total:g}s steps(1, end) infinite">'
        f'{text("▶ " + name, 3, x0 + 24, panel_y + 20, P["yellow"])}'
        f'{text(flavour, 2, x0 + 24, panel_y + 52, P["white"])}</g>'
        for k, (_, name, flavour) in enumerate(TOUR)
    )

    style = f"""
    .cursor {{ animation: tour {total:g}s steps(1, end) infinite, pulse .5s steps(1) infinite; }}
    @keyframes tour {{ {cursor_frames} }}
    @keyframes pulse {{ 50% {{ stroke: {P['yellow']}; }} }}
    {desc_frames}"""
    body = f"""
  <rect width="{W}" height="{H}" fill="{P['night']}"/>
  {frame(10, 10, W - 20, H - 20, P['pink'], P['cyan'], P['panel'])}
  {text("INVENTORY", 4, x0, 34, P['yellow'])}
  {text("ITEMS: " + str(sum(len(ids) for _, _, ids in ROWS)), 2, W - x0, 44, P['dim'], "end")}
  {"".join(slots)}
  {frame(x0, panel_y, widest * STEP - GAP, 90, P['white'], P['night'], P['night'], 3)}
  {descs}
  {cursor}"""
    return svg(W, H, "Inventory: the languages, frameworks and tools CL works with", body, style)
