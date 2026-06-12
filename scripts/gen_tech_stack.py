#!/usr/bin/env python3
"""Generate a high-contrast, theme-adaptive tech-stack panel as a self-contained
SVG: monospace pill chips with rounded borders + accent-barred category labels.
No logos, no JS. Renders in GitHub light & dark.

Run:  python scripts/gen_tech_stack.py
Out:  assets/tech-stack.svg

Edit STACK below to change content.
"""
import math
import pathlib
import random

random.seed(11)

# (CATEGORY LABEL, [items])  — items shown lowercase, terminal-style
STACK = [
    ("LANGUAGES",        ["python", "typescript", "kotlin", "c", "go"]),
    ("AI · ML · CV",     ["pytorch", "hugging face", "langchain", "langgraph",
                          "yolo", "vit", "mediapipe", "onnx", "gradio"]),
    ("DATABASES",        ["postgresql", "redis", "qdrant", "neo4j", "prisma"]),
    ("ROBOTICS",         ["arduino", "raspberry pi", "mujoco"]),
    ("BACKEND · DEVOPS", ["fastapi", "node.js", "express", "kafka", "aws s3",
                          "cloudflare r2", "docker", "prometheus", "grafana", "git"]),
    ("FRONTEND",         ["react", "next.js", "streamlit", "vite", "tailwind css"]),
]

W = 1000
PAD_L = 24
PAD_T = 26
PAD_B = 26

LABEL_X = PAD_L + 14          # text start (after accent bar)
LABEL_W = 196                 # reserved width for the label column
PILLS_X = PAD_L + LABEL_W     # pills start here
PILLS_MAX = W - 24            # right edge for pills

PILL_H = 30
PILL_RX = 8
PILL_PAD_X = 14
PILL_GAP = 9
LINE_GAP = 10
ROW_GAP = 16

FS_PILL = 14
FS_LABEL = 13
CHAR_W = FS_PILL * 0.60       # monospace advance estimate
FONT = ("ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, "
        "'Liberation Mono', monospace")


def pill_w(text):
    return int(math.ceil(len(text) * CHAR_W)) + 2 * PILL_PAD_X


def build():
    out = []
    out.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {{H}}" '
        f'width="100%" font-family="{FONT}" role="img" '
        f'aria-label="Tech stack">'
    )
    out.append("""<style>
  .label { fill:#1f2328; font-weight:700; letter-spacing:2px; }
  .bar   { fill:#1f2328; }
  .pill  { fill:none; stroke:#d0d7de; }
  .pilltx{ fill:#24292f; }
  .dot   { fill:#1f2328; opacity:.10; }
  @media (prefers-color-scheme: dark) {
    .label { fill:#f0f6fc; }
    .bar   { fill:#f0f6fc; }
    .pill  { stroke:#30363d; }
    .pilltx{ fill:#c9d1d9; }
    .dot   { fill:#f0f6fc; opacity:.10; }
  }
</style>""")

    body = []
    y = PAD_T
    for label, items in STACK:
        row_top = y
        cy = y + PILL_H / 2
        # accent bar + category label
        body.append(
            f'<rect class="bar" x="{PAD_L}" y="{cy-9:.1f}" width="4" height="18" rx="1.5"/>'
        )
        body.append(
            f'<text class="label" x="{LABEL_X}" y="{cy:.1f}" font-size="{FS_LABEL}" '
            f'dominant-baseline="central">{escape(label)}</text>'
        )
        # pills, wrapping within the content column
        x = PILLS_X
        for it in items:
            w = pill_w(it)
            if x + w > PILLS_MAX and x > PILLS_X:
                x = PILLS_X
                y += PILL_H + LINE_GAP
            pcy = y + PILL_H / 2
            body.append(
                f'<rect class="pill" x="{x}" y="{y}" width="{w}" height="{PILL_H}" '
                f'rx="{PILL_RX}" stroke-width="1"/>'
            )
            body.append(
                f'<text class="pilltx" x="{x+w/2:.1f}" y="{pcy:.1f}" '
                f'font-size="{FS_PILL}" text-anchor="middle" '
                f'dominant-baseline="central">{escape(it)}</text>'
            )
            x += w + PILL_GAP
        y += PILL_H + ROW_GAP
        _ = row_top

    H = y - ROW_GAP + PAD_B

    # faint scattered dots for subtle texture
    deco = []
    for _ in range(26):
        dx = random.uniform(PILLS_X, W - 12)
        dy = random.uniform(8, H - 8)
        deco.append(f'<circle class="dot" cx="{dx:.0f}" cy="{dy:.0f}" r="1.1"/>')

    out.append("".join(deco))
    out.append("".join(body))
    out.append("</svg>")
    return "\n".join(out).replace("{H}", str(int(H)))


def escape(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def main():
    p = pathlib.Path(__file__).resolve().parent.parent / "assets" / "tech-stack.svg"
    p.write_text(build(), encoding="utf-8")
    print(f"Wrote {p} ({p.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
