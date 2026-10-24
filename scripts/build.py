"""Fetch live GitHub numbers and regenerate every SVG in assets/.

Usage: GITHUB_TOKEN=... python3 scripts/build.py
"""
import datetime as dt
import json
import os
import pathlib
import urllib.request

import arrakis
import inventory
import player
import screens

LOGIN = os.environ.get("PROFILE_LOGIN", "singularity-code")
ASSETS = pathlib.Path(__file__).resolve().parent.parent / "assets"
BLOG = "SINGULARITY-CODE.GITHUB.IO"

# Pinned stages; the fallback text is used when a repo has no description.
STAGES = [
    ("GoogleAppsScript-SheetToCalendar", None),
    ("GoogleAppsScript-FormToCalendar", None),
    ("scim-endpoint", "Spring Boot SCIM 2.0 server with pluggable persistence"),
    ("prisma-express", "TypeScript REST API built with Express and Prisma ORM"),
]


def graphql(query):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode(),
        headers={"Authorization": f"bearer {os.environ['GITHUB_TOKEN']}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        payload = json.load(r)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]


def fetch():
    created = graphql(f'{{ user(login: "{LOGIN}") {{ createdAt }} }}')["user"]["createdAt"]
    first_year = int(created[:4])
    now = dt.datetime.now(dt.timezone.utc)
    years = "".join(
        f'y{y}: contributionsCollection(from: "{y}-01-01T00:00:00Z", to: "{y}-12-31T23:59:59Z") '
        f"{{ contributionCalendar {{ totalContributions }} }} "
        for y in range(first_year, now.year + 1)
    )
    repos = "".join(
        f'r{i}: repository(name: "{name}") {{ name description stargazerCount forkCount '
        f"primaryLanguage {{ name color }} }} "
        for i, (name, _) in enumerate(STAGES)
    )
    user = graphql(f"""{{ user(login: "{LOGIN}") {{
        {years}
        {repos}
        recent: contributionsCollection {{ contributionCalendar {{ totalContributions }} }}
        repositories(ownerAffiliations: OWNER, privacy: PUBLIC, first: 100) {{ totalCount nodes {{ stargazerCount }} }}
    }} }}""")["user"]

    stats = {
        "contrib_year": user["recent"]["contributionCalendar"]["totalContributions"],
        "contrib_all": sum(user[f"y{y}"]["contributionCalendar"]["totalContributions"] for y in range(first_year, now.year + 1)),
        "years": now.year - first_year,
        "repos": user["repositories"]["totalCount"],
        "stars": sum(n["stargazerCount"] for n in user["repositories"]["nodes"]),
    }
    stages = []
    for i, (_, fallback) in enumerate(STAGES):
        r = user[f"r{i}"]
        lang = r["primaryLanguage"] or {"name": "N/A", "color": "#8a7bb0"}
        stages.append({
            "name": r["name"],
            "description": r["description"] or fallback or "",
            "stars": r["stargazerCount"],
            "forks": r["forkCount"],
            "language": {"name": lang["name"], "color": lang["color"] or "#8a7bb0"},
        })
    return stats, stages


def main():
    stats, stages = fetch()
    ASSETS.mkdir(exist_ok=True)
    outputs = {
        "banner.svg": arrakis.banner(),
        "game.svg": arrakis.game(stats),
        "player.svg": player.render(),
        "inventory.svg": inventory.render(),
        "save-point.svg": screens.save_point(BLOG),
        "game-over.svg": screens.game_over(),
    }
    for i, repo in enumerate(stages):
        outputs[f"stage-{i + 1}.svg"] = screens.stage_card(i, repo)
    for name, content in outputs.items():
        (ASSETS / name).write_text(content)
    print(json.dumps(stats))


if __name__ == "__main__":
    main()
