#!/usr/bin/env python3
"""Generate an animated, theme-adaptive tagline SVG: a terminal line that
types out the roles with a blinking cursor. Pure SMIL/CSS, no JS.

Run:  python scripts/gen_tagline.py
Out:  assets/tagline.svg
"""
import math
import pathlib

PROMPT = "❯ "
ROLES = "ML / DL  •  Computer Vision  •  Edge AI"

FS = 24
CHAR_W = FS * 0.60        # monospace advance estimate
PAD_X = 28
H = 56
FONT = ("ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, "
        "'Liberation Mono', monospace")

PER_CHAR = 0.075          # seconds per typed character

USERNAME = "atikulmunna"
SIGNATURE = (
    f"<!-- Source & credit: github.com/{USERNAME} — "
    f"do not reuse without attribution. -->"
    f'<metadata>Created by @{USERNAME} (github.com/{USERNAME}). '
    f"All rights reserved.</metadata>"
)


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build():
    n = len(ROLES)
    cw = CHAR_W
    roles_w = n * cw
    prompt_w = len(PROMPT) * cw
    cur_w = cw * 0.55
    total_w = prompt_w + roles_w + cur_w
    W = int(math.ceil(total_w + 2 * PAD_X))

    x0 = (W - total_w) / 2
    prompt_x = x0
    roles_x = x0 + prompt_w
    cy = H / 2
    typing_dur = n * PER_CHAR

    # discrete reveal: one character per step
    widths = ";".join(f"{i*cw:.1f}" for i in range(n + 1))
    cur_xs = ";".join(f"{roles_x + i*cw:.1f}" for i in range(n + 1))
    keytimes = ";".join(f"{i/n:.4f}" for i in range(n + 1))

    cur_y = cy - FS * 0.52
    cur_h = FS * 1.04

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" \
width="{W}" height="{H}" font-family="{FONT}" role="img" \
aria-label="{esc(PROMPT + ROLES)}">
  {SIGNATURE}
  <style>
    .tx     {{ fill:#1f2328; font-weight:700; }}
    .prompt {{ fill:#6e7681; font-weight:700; }}
    .cur    {{ fill:#1f2328; }}
    @media (prefers-color-scheme: dark) {{
      .tx     {{ fill:#f0f6fc; }}
      .prompt {{ fill:#8b949e; }}
      .cur    {{ fill:#f0f6fc; }}
    }}
  </style>

  <clipPath id="reveal">
    <rect x="{roles_x:.1f}" y="0" height="{H}" width="0">
      <animate attributeName="width" values="{widths}" keyTimes="{keytimes}"
               calcMode="discrete" dur="{typing_dur:.2f}s" fill="freeze"/>
    </rect>
  </clipPath>

  <text class="prompt" x="{prompt_x:.1f}" y="{cy:.1f}" font-size="{FS}"
        dominant-baseline="central">{esc(PROMPT)}</text>

  <text class="tx" x="{roles_x:.1f}" y="{cy:.1f}" font-size="{FS}"
        dominant-baseline="central" clip-path="url(#reveal)"
        xml:space="preserve">{esc(ROLES)}</text>

  <rect class="cur" y="{cur_y:.1f}" width="{cur_w:.1f}" height="{cur_h:.1f}"
        x="{roles_x:.1f}">
    <animate attributeName="x" values="{cur_xs}" keyTimes="{keytimes}"
             calcMode="discrete" dur="{typing_dur:.2f}s" fill="freeze"/>
    <animate attributeName="opacity" values="1;1;0;0" keyTimes="0;0.5;0.5;1"
             calcMode="discrete" dur="1.05s" repeatCount="indefinite"/>
  </rect>
</svg>"""


def main():
    p = pathlib.Path(__file__).resolve().parent.parent / "assets" / "tagline.svg"
    p.write_text(build(), encoding="utf-8")
    print(f"Wrote {p} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
