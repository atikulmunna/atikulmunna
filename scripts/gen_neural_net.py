#!/usr/bin/env python3
"""Generate a self-contained, theme-adaptive animated neural-net + particle-field
SVG banner. Pure SMIL/CSS (no JS) so it animates inside a GitHub <img> embed.

Run:  python scripts/gen_neural_net.py
Out:  assets/neural-net.svg
"""
import math
import pathlib
import random

random.seed(7)  # reproducible layout

W, H = 1000, 240
LAYERS = [4, 6, 6, 4]          # nodes per layer
X_PAD = 120
Y_PAD = 40
NUM_PARTICLES = 38
NUM_SIGNALS = 30               # animated pulses traveling along edges


def layer_nodes():
    """Return list of layers, each a list of (x, y) node centers."""
    xs = [X_PAD + i * (W - 2 * X_PAD) / (len(LAYERS) - 1) for i in range(len(LAYERS))]
    layers = []
    for li, n in enumerate(LAYERS):
        span = H - 2 * Y_PAD
        ys = [Y_PAD + (j + 0.5) * span / n for j in range(n)]
        layers.append([(xs[li], y) for y in ys])
    return layers


def build():
    layers = layer_nodes()
    edges = []  # (x1, y1, x2, y2)
    for a, b in zip(layers, layers[1:]):
        for (x1, y1) in a:
            for (x2, y2) in b:
                edges.append((x1, y1, x2, y2))

    parts = []
    parts.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="100%" role="img" aria-label="Animated neural network">'
    )

    # --- theme-adaptive palette (works in GitHub light & dark) ---
    parts.append("""<style>
  .ink   { stroke:#0b0b0b; }
  .inkf  { fill:#0b0b0b; }
  .edge  { stroke:#0b0b0b; stroke-width:.6; opacity:.10; }
  .sig   { fill:#0b0b0b; }
  .dust  { fill:#0b0b0b; }
  .node  { fill:#ffffff; stroke:#0b0b0b; stroke-width:1.4; }
  .flash { fill:#111111; }
  @media (prefers-color-scheme: dark) {
    .ink   { stroke:#ffffff; }
    .inkf  { fill:#ffffff; }
    .edge  { stroke:#ffffff; opacity:.14; }
    .sig   { fill:#ffffff; }
    .dust  { fill:#ffffff; }
    .node  { fill:#0b0b0b; stroke:#ffffff; }
    .flash { fill:#ffffff; }
  }
</style>""")

    # --- soft glow filter for the node flashes ---
    parts.append(
        '<defs>'
        '<filter id="glow" x="-200%" y="-200%" width="500%" height="500%">'
        '<feGaussianBlur stdDeviation="4.5"/>'
        '</filter>'
        '</defs>'
    )

    # --- background particle field (twinkle + drift) ---
    parts.append('<g>')
    for _ in range(NUM_PARTICLES):
        x = random.uniform(0, W)
        y = random.uniform(0, H)
        r = random.uniform(0.6, 1.8)
        dur = random.uniform(2.5, 6.0)
        beg = random.uniform(0, 5)
        dx = random.uniform(-14, 14)
        dy = random.uniform(-10, 10)
        op = random.uniform(0.05, 0.22)
        parts.append(
            f'<circle class="dust" cx="{x:.1f}" cy="{y:.1f}" r="{r:.2f}" opacity="{op:.2f}">'
            f'<animate attributeName="opacity" values="0;{op:.2f};0" dur="{dur:.1f}s" '
            f'begin="{beg:.1f}s" repeatCount="indefinite"/>'
            f'<animateTransform attributeName="transform" type="translate" '
            f'values="0 0; {dx:.0f} {dy:.0f}; 0 0" dur="{dur*2:.1f}s" '
            f'begin="{beg:.1f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    parts.append('</g>')

    # --- edges (faint, static) ---
    parts.append('<g class="edge">')
    for (x1, y1, x2, y2) in edges:
        parts.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}"/>')
    parts.append('</g>')

    # --- traveling signal pulses along a random subset of edges ---
    parts.append('<g>')
    for e in random.sample(edges, min(NUM_SIGNALS, len(edges))):
        x1, y1, x2, y2 = e
        dur = random.uniform(1.4, 3.0)
        beg = random.uniform(0, 3.0)
        parts.append(
            f'<circle class="sig" r="2.4" opacity="0">'
            f'<animate attributeName="cx" values="{x1:.1f};{x2:.1f}" dur="{dur:.2f}s" '
            f'begin="{beg:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y1:.1f};{y2:.1f}" dur="{dur:.2f}s" '
            f'begin="{beg:.2f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" dur="{dur:.2f}s" '
            f'begin="{beg:.2f}s" repeatCount="indefinite"/>'
            f'</circle>'
        )
    parts.append('</g>')

    # --- nodes: bright blurred white flash, then a crisp core on top ---
    parts.append('<g>')
    for layer in layers:
        for (x, y) in layer:
            r = 6.0
            dur = random.uniform(1.8, 3.2)
            beg = random.uniform(0, dur)
            # blurred bloom that punches bright then decays — the eye-catcher
            parts.append(
                f'<circle class="flash" cx="{x:.1f}" cy="{y:.1f}" r="{r}" '
                f'filter="url(#glow)" opacity="0">'
                f'<animate attributeName="opacity" values="0;1;0.55;0" '
                f'keyTimes="0;0.08;0.35;1" calcMode="spline" '
                f'keySplines="0.1 0.8 0.2 1;0.4 0 0.6 1;0.4 0 0.6 1" '
                f'dur="{dur:.2f}s" begin="{beg:.2f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="r" values="{r+1};{r+11};{r+4}" '
                f'keyTimes="0;0.08;1" dur="{dur:.2f}s" begin="{beg:.2f}s" '
                f'repeatCount="indefinite"/>'
                f'</circle>'
            )
            # crisp node core sitting on top of the glow
            parts.append(
                f'<circle class="node" cx="{x:.1f}" cy="{y:.1f}" r="{r}">'
                f'<animate attributeName="r" values="{r};{r+1.6};{r}" '
                f'dur="{dur:.2f}s" begin="{beg:.2f}s" repeatCount="indefinite"/>'
                f'</circle>'
            )
    parts.append('</g>')

    parts.append('</svg>')
    return "\n".join(parts)


def main():
    out = pathlib.Path(__file__).resolve().parent.parent / "assets" / "neural-net.svg"
    out.write_text(build(), encoding="utf-8")
    print(f"Wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
