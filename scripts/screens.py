"""Small screens: STAGE SELECT cards, the SAVE POINT button and the GAME OVER footer."""
import re
import textwrap

from pixel import PALETTE as P, frame, sprite, svg, text, text_width
from themes import CONTENT

STAGE_COLORS = ["cyan", "pink", "yellow", "purple"]


def stage_card(index, repo):
    """One pinned repo drawn as a level-select tile."""
    w, h = 480, 190
    color = P[STAGE_COLORS[index % len(STAGE_COLORS)]]
    name = repo["name"].upper()
    name_px = 3 if text_width(name, 3) <= w - 70 else 2
    desc = re.sub(r":\w+:", "", repo["description"]).strip().upper()
    lines = textwrap.wrap(desc, 34)[:2]
    lang = repo["language"]
    meta = f"★ {repo['stars']}   FORK {repo['forks']}"
    body = f"""
  <rect width="{w}" height="{h}" fill="{P['night']}"/>
  {frame(2, 2, w - 4, h - 4, color, P['night'], P['panel'], 4)}
  {text(f"STAGE {index // 2 + 1}-{index % 2 + 1}", 2, 30, 28, P['yellow'])}
  {text(meta, 2, w - 30, 28, P['white'], "end")}
  {text(name, name_px, 30, 56, color)}
  {"".join(text(line, 2, 30, 92 + i * 20, P['white']) for i, line in enumerate(lines))}
  <rect x="30" y="{h - 40}" width="14" height="14" fill="{lang['color']}"/>
  {text(lang['name'], 2, 52, h - 40, P['dim'])}
  <g class="blink">{text("▶ ENTER", 2, w - 30, h - 40, color, "end")}</g>"""
    style = ".blink { animation: blink 1.2s steps(1) infinite; } @keyframes blink { 50% { opacity: 0; } }"
    return svg(w, h, f"Stage {index + 1}: {repo['name']} - {desc}", body, style)


def save_point(url_text):
    label = f"▶ SAVE POINT: {url_text}"
    w, h = text_width(label, 2) + 60, 52
    body = f"""
  <rect width="{w}" height="{h}" fill="{P['night']}"/>
  {frame(0, 0, w, h, P['pink'], P['night'], P['panel'], 4)}
  {text(label, 2, w / 2, 19, P['white'], "middle")}"""
    return svg(w, h, f"Blog: {url_text}", body)


COIN = ["..yyyy..", ".yyooyy.", "yyyooyyy", "yyyooyyy", "yyyooyyy", "yyyooyyy", ".yyooyy.", "..yyyy.."]


def game_over():
    w, h = 1000, 220
    digits = "".join(
        f'<g style="opacity:0; animation: c{9 - n} 10s steps(1, end) infinite">{text(str(n), 4, 640, 112, P["yellow"])}</g>'
        for n in range(9, -1, -1)
    )
    count_frames = "".join(
        f"@keyframes c{k} {{ {k * 10}% {{ opacity: 1; }} {(k + 1) * 10}%, 100% {{ opacity: 0; }} }}\n" for k in range(10)
    )
    coin = lambda x: f'<g class="coin">{sprite(COIN, 5, x, 160, {"y": P["yellow"], "o": "#c99a00"})}</g>'
    style = f"""
    .blink {{ animation: blink 1s steps(1) infinite; }}
    @keyframes blink {{ 50% {{ opacity: 0; }} }}
    .coin {{ transform-box: fill-box; transform-origin: center; animation: spin .9s steps(4) infinite; }}
    @keyframes spin {{ 0% {{ transform: scaleX(1); }} 50% {{ transform: scaleX(.15); }} 100% {{ transform: scaleX(1); }} }}
    {count_frames}"""
    body = f"""
  <rect width="{w}" height="{h}" fill="{P['night']}"/>
  {text(CONTENT['game_over'], 5, w / 2 + 4, 34, P['cyan'], "middle")}
  {text(CONTENT['game_over'], 5, w / 2, 30, P['pink'], "middle")}
  {text("CONTINUE?", 4, 380, 112, P['white'])}
  {digits}
  <g class="blink">{text("INSERT COIN", 3, w / 2, 170, P['white'], "middle")}</g>
  {coin(w / 2 - 160)}{coin(w / 2 + 120)}"""
    return svg(w, h, f"{CONTENT['game_over'].capitalize()} Continue? Insert coin.", body, style)
