#!/usr/bin/env python3
"""Render the GitHub contribution calendar as a monospace ASCII heatmap and
splice it into README.md between the ASCII-HEATMAP markers.

Usage:
    GITHUB_TOKEN=... GH_USER=atikulmunna python scripts/gen_ascii_heatmap.py

The token needs only public read access (the default Actions GITHUB_TOKEN works).
"""
import datetime as dt
import json
import os
import pathlib
import sys
import urllib.request

START = "<!-- ASCII-HEATMAP:START -->"
END = "<!-- ASCII-HEATMAP:END -->"

# light -> dark ramp; index 0 == no contributions
RAMP = ["·", "░", "▒", "▓", "█"]
LEVEL = {
    "NONE": 0,
    "FIRST_QUARTILE": 1,
    "SECOND_QUARTILE": 2,
    "THIRD_QUARTILE": 3,
    "FOURTH_QUARTILE": 4,
}
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
          "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays { contributionLevel date weekday }
        }
      }
    }
  }
}
"""


def fetch(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={
            "Authorization": f"bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": "ascii-heatmap-generator",
        },
    )
    with urllib.request.urlopen(req) as r:
        data = json.load(r)
    if "errors" in data:
        raise SystemExit(f"GraphQL error: {data['errors']}")
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def render(cal):
    weeks = cal["weeks"]
    # grid[weekday][week] -> ramp char
    grid = [[" "] * len(weeks) for _ in range(7)]
    for wi, wk in enumerate(weeks):
        for day in wk["contributionDays"]:
            grid[day["weekday"]][wi] = RAMP[LEVEL[day["contributionLevel"]]]

    # month label row aligned to the week columns where a new month begins
    label = [" "] * len(weeks)
    seen = set()
    for wi, wk in enumerate(weeks):
        first = wk["contributionDays"][0]["date"]
        m = int(first[5:7])
        if m not in seen:
            seen.add(m)
            name = MONTHS[m - 1]
            for k, ch in enumerate(name):
                if wi + k < len(weeks):
                    label[wi + k] = ch

    day_tags = ["   ", "Mon", "   ", "Wed", "   ", "Fri", "   "]
    lines = ["    " + "".join(label)]
    for r in range(7):
        lines.append(f"{day_tags[r]} " + "".join(grid[r]))

    total = cal["totalContributions"]
    legend = "    less " + "".join(RAMP) + f" more      {total:,} contributions in the last year"
    lines.append("")
    lines.append(legend)
    return "\n".join(lines)


def splice(readme: pathlib.Path, block: str):
    text = readme.read_text(encoding="utf-8")
    if START not in text or END not in text:
        raise SystemExit(f"Markers {START} / {END} not found in {readme}")
    pre = text.split(START)[0]
    post = text.split(END)[1]
    new = f"{pre}{START}\n<pre>\n{block}\n</pre>\n{END}{post}"
    if new != text:
        readme.write_text(new, encoding="utf-8")
        print("README updated.")
    else:
        print("No change.")


def main():
    login = os.environ.get("GH_USER") or os.environ.get("GITHUB_REPOSITORY_OWNER")
    token = os.environ.get("GITHUB_TOKEN") or os.environ.get("GH_TOKEN")
    if not login or not token:
        sys.exit("Set GH_USER and GITHUB_TOKEN.")
    cal = fetch(login, token)
    block = render(cal)
    print(block)
    readme = pathlib.Path(__file__).resolve().parent.parent / "README.md"
    splice(readme, block)


if __name__ == "__main__":
    main()
