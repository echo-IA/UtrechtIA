#!/usr/bin/env python3
import os
import argparse
import numpy as np
import matplotlib
matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle, Polygon
from matplotlib.font_manager import FontProperties

# ---------- Defaults ----------
COLOR_SCHEMES = {
    "white": {"PRIMARY": "#FFFFFF", "ACCENT": "#FFFFFF", "TEXT": "#FFFFFF"},
    "utrecht":  {"PRIMARY": "#FFCD00", "ACCENT": "#C00A35", "TEXT": "#000000"},
}

FONTFACE = "Gill Sans"

PNG_NAME = "utrechtIA_logo.png"
JPG_NAME = "utrechtIA_logo.jpg"
SVG_NAME = "utrechtIA.svg"

TILT_ANGLE = -60
LW = 4.5

# Slightly smaller ellipse (windmill blades illusion)
ELLIPSE_WIDTH = 3.8
ELLIPSE_HEIGHT = 2.2

ARC_DEG = 20
ARC_START_DEG = -270 + ARC_DEG
ARC_END_DEG = 90 - ARC_DEG
ARC_LW = LW

# Spiral params
THETA_MAX = 2 * np.pi
ARM_PHASE = np.pi
B_SHAPE = 2.0
FILL = 0.92
LINEWIDTH = LW

# Arrow
ARROW_LEN = 2
ARROW_LW = 2.5

# Text
TITLE = "UtrechtIA"
SUBTITLE = "Appropriately ridiculous acronym"
TITLE_FS = 40
SUB_FS = 20
ITAL_SUB = True


# ---------- Helpers ----------
def rot2d(theta_deg: float) -> np.ndarray:
    t = np.deg2rad(theta_deg)
    c, s = np.cos(t), np.sin(t)
    return np.array([[c, -s], [s, c]])

def normalized_spiral(theta, b=B_SHAPE):
    u = (1.0 + theta/THETA_MAX)
    r = (u**b - 1.0) / ((1.0 + 1.0)**b - 1.0)
    return np.clip(r, 0.0, 1.0)

def pts_to_figfrac(pts, fig_height_in):
    return pts / (72.0 * fig_height_in)


def draw_logo(
    output_dir: str,
    color_mode: str,
    show_text: bool,
    dpi: int = 300,
    figsize=(8, 6),
    png_name: str = PNG_NAME,
    jpg_name: str = JPG_NAME,
    svg_name: str = SVG_NAME,
    fontface: str = FONTFACE,
):
    colors = COLOR_SCHEMES[color_mode]
    PRIMARY = colors["PRIMARY"]

    os.makedirs(output_dir, exist_ok=True)
    fig = plt.figure(figsize=figsize)

    if show_text:
        text_band_pts = 1.1*TITLE_FS + 1.1*SUB_FS + 25
        top_pad = pts_to_figfrac(text_band_pts, figsize[1])
        axes_rect = [0.08, 0.08, 0.84, 1.0 - 0.08 - top_pad]
    else:
        axes_rect = [0.06, 0.06, 0.88, 0.88]

    ax = fig.add_axes(axes_rect)
    ax.set_aspect('equal')
    ax.axis('off')

    a = ELLIPSE_WIDTH / 2.0
    b = ELLIPSE_HEIGHT / 2.0

    theta = np.linspace(0, THETA_MAX, 1200)
    r1 = normalized_spiral(theta)
    x1 = r1 * np.cos(theta)
    y1 = r1 * np.sin(theta)

    r2 = normalized_spiral(theta)
    x2 = r2 * np.cos(theta + ARM_PHASE)
    y2 = r2 * np.sin(theta + ARM_PHASE)

    X1 = np.vstack([a * FILL * x1, b * FILL * y1])
    X2 = np.vstack([a * FILL * x2, b * FILL * y2])

    R = rot2d(TILT_ANGLE)
    arm1 = R @ X1
    arm2 = R @ X2

    ax.plot(arm1[0], arm1[1], color=PRIMARY, lw=LINEWIDTH, solid_capstyle='round')
    ax.plot(arm2[0], arm2[1], color=PRIMARY, lw=LINEWIDTH, solid_capstyle='round')

    # C-shaped arc
    tt = np.deg2rad(np.linspace(ARC_START_DEG, ARC_END_DEG, 400))
    x_e = (ELLIPSE_WIDTH / 2.0)  * np.cos(tt)
    y_e = (ELLIPSE_HEIGHT / 2.0) * np.sin(tt)
    arc = R @ np.vstack([x_e, y_e])
    ax.plot(arc[0], arc[1], color=PRIMARY, lw=ARC_LW, solid_capstyle='round')

    # Central bulge
    bulge_r = min(a, b) * 0.15
    ax.add_patch(Circle((0, 0), radius=bulge_r, facecolor=PRIMARY, edgecolor='none', zorder=0))

    # Arrow
    start_local = np.array([0.0, 0.0])
    dir_local   = np.array([0.0, ARROW_LEN])
    R_ell = rot2d(TILT_ANGLE)
    start_rot = (R_ell @ start_local).tolist()
    end_rot   = (R_ell @ (start_local + dir_local)).tolist()

    arrow = FancyArrowPatch(
        start_rot, end_rot,
        arrowstyle='Simple,head_length=10,head_width=18,tail_width=3',
        linewidth=ARROW_LW, color=PRIMARY
    )
    ax.add_patch(arrow)

        # -----------------------------
    # Windmill tower (outline + brick pattern only)
    # -----------------------------
    base_height = 3.6
    base_top_width = 1.0
    base_bottom_width = 2.2

    y_top = -ELLIPSE_HEIGHT / 2 - 0.15
    y_bottom = y_top - base_height

    # Tower outline only (no fill)
    tower = Polygon([
        (-base_top_width / 2, y_top),
        ( base_top_width / 2, y_top),
        ( base_bottom_width / 2, y_bottom),
        (-base_bottom_width / 2, y_bottom),
    ],
        closed=True,
        facecolor="none",                 # ← no solid fill
        edgecolor=colors["TEXT"],         # black outline
        linewidth=2.5,
        zorder=1
    )
    ax.add_patch(tower)

    # ---- Brick lines (red) ----
    brick_rows = 12
    for i in range(brick_rows + 1):
        frac = i / brick_rows
        y = y_bottom + frac * base_height

        width = base_bottom_width - (base_bottom_width - base_top_width) * frac
        x_left = -width / 2
        x_right = width / 2

        # horizontal mortar lines
        ax.plot([x_left, x_right], [y, y],
                color=colors["ACCENT"],   # red bricks
                lw=1.2,
                zorder=2)

        # vertical staggered brick seams
        if i < brick_rows:
            offset = 0.25 if i % 2 == 0 else 0.0
            brick_w = 0.45
            x = x_left + offset
            while x < x_right:
                ax.plot([x, x], [y, y + base_height/brick_rows],
                        color=colors["ACCENT"],
                        lw=0.8,
                        zorder=2)
                x += brick_w

    # -----------------------------
    # Tulips (real flower silhouette)
    # -----------------------------
    def draw_tulip(x, y, scale=1.0):
        stem_h = 1.2 * scale
        flower_h = 0.9 * scale
        flower_w = 0.8 * scale

        # Stem (black)
        ax.plot([x, x], [y, y + stem_h],
                color=colors["TEXT"],
                lw=2,
                zorder=3)

        # Leaves (curved look using small angled lines)
        ax.plot([x, x - 0.5*scale],
                [y + 0.5*scale, y + 0.9*scale],
                color=colors["TEXT"],
                lw=2,
                zorder=3)
        ax.plot([x, x + 0.5*scale],
                [y + 0.4*scale, y + 0.8*scale],
                color=colors["TEXT"],
                lw=2,
                zorder=3)

        # Tulip head (three-petal crown shape)
        petal = Polygon([
            (x - flower_w/2, y + stem_h),
            (x - flower_w/4, y + stem_h + flower_h*0.6),
            (x,              y + stem_h + flower_h),
            (x + flower_w/4, y + stem_h + flower_h*0.6),
            (x + flower_w/2, y + stem_h),
            (x + flower_w/4, y + stem_h + flower_h*0.4),
            (x,              y + stem_h + flower_h*0.7),
            (x - flower_w/4, y + stem_h + flower_h*0.4),
        ],
            closed=True,
            facecolor=colors["ACCENT"],   # red petals
            edgecolor=colors["TEXT"],     # black outline
            linewidth=1.5,
            zorder=4
        )

        ax.add_patch(petal)

    ground_y = y_bottom

    draw_tulip(-2.0, ground_y, 1.0)
    draw_tulip(-1.3, ground_y, 0.9)
    draw_tulip(1.3, ground_y, 0.9)
    draw_tulip(2.0, ground_y, 1.0)

    # Text
    if show_text:
        title_fp = FontProperties(family=fontface, weight='light')
        sub_fp   = FontProperties(family=fontface, weight='light',
                                  style='italic' if ITAL_SUB else 'normal')

        band_bottom = axes_rect[1] + axes_rect[3]
        band_top    = 0.995

        fig_h_in = figsize[1]
        line_spacing = 1.15
        n_lines = len(SUBTITLE.split("\n"))

        title_h = (TITLE_FS / 72.0) / fig_h_in
        sub_h   = (n_lines * SUB_FS * line_spacing) / 72.0 / fig_h_in
        band_height = band_top - band_bottom
        G = max(0.0, (band_height - title_h - sub_h) / 2.0)

        title_y      = band_top
        subtitle_top = band_top - title_h - G
        sub_step     = (SUB_FS * line_spacing) / 72.0 / fig_h_in

        fig.text(0.5, title_y, TITLE,
                 fontproperties=title_fp,
                 ha='center', va='top',
                 fontsize=TITLE_FS, color=PRIMARY)

        for i, line in enumerate(SUBTITLE.split("\n")):
            y = subtitle_top - i * sub_step
            fig.text(0.5, y, line,
                     fontproperties=sub_fp,
                     ha='center', va='top',
                     fontsize=SUB_FS, color=PRIMARY)

    # Frame
    margin = 1
    ax.set_xlim(-ELLIPSE_WIDTH/2 - margin, ELLIPSE_WIDTH/2 + margin)
    ax.set_ylim(y_bottom - 1.5, ELLIPSE_HEIGHT/2 + margin)

    # Save
    suffix = "_text" if show_text else "_notext"
    c_sfx = "" if color_mode == "utrecht" else "_white"

    png_path = os.path.join(output_dir, PNG_NAME.replace(".png", f"{suffix}{c_sfx}.png"))
    jpg_path = os.path.join(output_dir, JPG_NAME.replace(".jpg", f"{suffix}{c_sfx}.jpg"))
    svg_path = os.path.join(output_dir, SVG_NAME.replace(".svg", f"{suffix}{c_sfx}.svg"))

    fig.savefig(png_path, dpi=dpi, bbox_inches='tight', transparent=True)
    fig.savefig(jpg_path, dpi=dpi, bbox_inches='tight', transparent=True)
    fig.savefig(svg_path, dpi=dpi, bbox_inches='tight', transparent=True)
    plt.close(fig)


def parse_args():
    p = argparse.ArgumentParser(description="Generate UtrechtIA logo variants.")
    p.add_argument("--output-dir", default="docs/output_data/logo_output")
    p.add_argument("--dpi", type=int, default=300)
    p.add_argument("--figsize", type=float, nargs=2, default=(8, 6))
    p.add_argument("--modes", nargs="+", default=["utrecht", "white"],
                   choices=list(COLOR_SCHEMES.keys()))
    group = p.add_mutually_exclusive_group()
    group.add_argument("--with-text", dest="with_text", action="store_true")
    group.add_argument("--no-text", dest="no_text", action="store_true")
    return p.parse_args()


def main():
    args = parse_args()

    if args.with_text:
        text_variants = [True]
    elif args.no_text:
        text_variants = [False]
    else:
        text_variants = [True, False]

    for mode in args.modes:
        for show_text in text_variants:
            draw_logo(
                output_dir=args.output_dir,
                color_mode=mode,
                show_text=show_text,
                dpi=args.dpi,
                figsize=tuple(args.figsize),
            )
            print(f"Saved {mode} {'text' if show_text else 'notext'} variants to {os.path.abspath(args.output_dir)}")


if __name__ == "__main__":
    main()