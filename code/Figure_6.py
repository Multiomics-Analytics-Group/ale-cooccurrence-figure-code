"""Figure 6: metro map of the configurable analysis pipeline, with dashed callouts that list each
output's files.

usage, from the folder that holds code/ and figures/:
  python code/Figure_6.py figures/Figure_6
writes Figure_6.png and Figure_6_raw.svg into the folder given as the first argument. Then
  python code/svg_for_illustrator.py figures/Figure_6/Figure_6_raw.svg figures/Figure_6/Figure_6.svg "Build binary|unit matrix" ""
writes Figure_6.svg (run_all.sh then deletes Figure_6_raw.svg)."""
import sys
from pathlib import Path

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle

mpl.rcParams["svg.fonttype"] = "none"
mpl.rcParams["pdf.fonttype"] = 42
mpl.rcParams["figure.facecolor"] = "white"
mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]

OUT = Path(sys.argv[1])
DPI = 300

FONTSIZE, FS_LINE, FS_FEED, FS_ICON = 16, 16, 15, 15
LW, R_ST, R_IX = 7.0, 0.20, 0.27
INK, QC, PEX, DESC, OUTC, FEED = "#111111", "#338FC7", "#673672", "#BA7331", "#2E7D5B", "#6E7A85"
ONC_FILL, ONC_EMPTY = "#458B57", "#eef1f4"
DASH = (0, (4, 3))

XL, XR, YB, YT = -1.9, 27.4, -2.6, 10.6
fig = plt.figure(figsize=(23.5 * (XR - XL) / 28.5, 23.5 * (YT - YB) / 28.5))
ax = fig.add_axes([0, 0, 1, 1])


def route(pts, color, lw=None, z=1):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw or LW, solid_capstyle="round", solid_joinstyle="round", zorder=z)


def station(x, y, label, color, kind="stop", dx=0.0, dy=-0.55, ha="center", va="top", z=5):
    if kind == "ix":
        ax.add_patch(Circle((x, y), R_IX + 0.07, facecolor="white", edgecolor=INK, lw=2.0, zorder=z))
        ax.add_patch(Circle((x, y), R_IX - 0.05, facecolor=color, edgecolor="none", zorder=z + 1))
    else:
        ax.add_patch(Circle((x, y), R_ST, facecolor="white", edgecolor=color, lw=3.0, zorder=z))
    ax.annotate(label, (x + dx, y + dy), ha=ha, va=va, fontsize=FONTSIZE, color=INK, zorder=z + 2,
                linespacing=1.25)


def feeder(x, y_line, label, up=1.35, h=0.80, w=2.60):
    y_end = y_line + up
    ax.plot([x, x], [y_line, y_end], color=FEED, lw=2.0, ls=(0, (2, 2)), zorder=0)
    y_box = y_end if up > 0 else y_end - h
    ax.add_patch(Rectangle((x - w / 2, y_box), w, h, facecolor="white", edgecolor=FEED, lw=1.6, zorder=4))
    ax.annotate(label, (x, y_box + h / 2), ha="center", va="center", fontsize=FS_FEED, color=FEED, zorder=5,
                linespacing=1.15)


def output(xc, yc, label, w, h):
    """Output box with square corners. Returns its edges."""
    ax.add_patch(Rectangle((xc - w / 2, yc - h / 2), w, h, facecolor="white", edgecolor=OUTC, lw=3.4, zorder=6))
    ax.annotate(label, (xc, yc), ha="center", va="center", fontsize=FONTSIZE + 1, color=INK, zorder=7,
                linespacing=1.15, fontweight="bold")
    return xc - w / 2, xc + w / 2, yc - h / 2


def source(x, y, label, w=2.0, h=0.8):
    ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h, boxstyle="round,pad=0.02,rounding_size=0.35",
                                facecolor="white", edgecolor=INK, lw=2.6, zorder=6))
    ax.annotate(label, (x, y), ha="center", va="center", fontsize=FONTSIZE, color=INK, zorder=7,
                fontweight="bold")


def callout(bx0, bx1, by, rx0, rx1, rtop, rbot):
    """Dashed outline that opens from the bottom of an output box into the box listing its files."""
    xs = [bx0, rx0, rx0, rx1, rx1, bx1]
    ys = [by, rtop, rbot, rbot, rtop, by]
    ax.plot(xs, ys, color=OUTC, lw=3.0, ls=DASH, zorder=2, solid_joinstyle="miter")


def page(x, y, w, h, fold=0.22, z=5):
    pts = [(x, y), (x + w, y), (x + w, y + h - fold), (x + w - fold, y + h), (x, y + h)]
    ax.add_patch(plt.Polygon(pts, closed=True, facecolor="white", edgecolor=OUTC, lw=2.2, zorder=z,
                             joinstyle="round"))
    ax.add_patch(plt.Polygon([(x + w - fold, y + h), (x + w - fold, y + h - fold), (x + w, y + h - fold)],
                             closed=True, facecolor="#E3EEE8", edgecolor=OUTC, lw=1.8, zorder=z + 1,
                             joinstyle="round"))


def glyph_table(x, y, w, h, z=7):
    x0, x1 = x + 0.11, x + w - 0.11
    top = y + h - 0.30
    ax.plot([x0, x1], [top, top], color=OUTC, lw=2.6, zorder=z, solid_capstyle="butt")
    for k in range(1, 5):
        ax.plot([x0, x1], [top - k * 0.13] * 2, color="#9DB7AA", lw=1.3, zorder=z, solid_capstyle="butt")
    ax.plot([x0 + 0.20] * 2, [top - 4 * 0.13, top], color="#9DB7AA", lw=1.2, zorder=z)


def glyph_matrix(x, y, w, h, z=7):
    rng = np.random.default_rng(3)
    m, n = 5, 4
    cw, ch = (w - 0.22) / m, 0.12
    top = y + h - 0.32
    for i in range(n):
        for j in range(m):
            ax.add_patch(Rectangle((x + 0.11 + j * cw, top - (i + 1) * ch), cw * 0.86, ch * 0.80,
                                   facecolor=ONC_FILL if rng.random() < 0.38 else ONC_EMPTY, edgecolor="none",
                                   zorder=z))


def doc(xc, ytop, label, kind="table", stack=False, w=0.78, h=0.98):
    x, y = xc - w / 2, ytop - h
    if stack:
        page(x + 0.16, y + 0.14, w, h, z=3)
        page(x + 0.08, y + 0.07, w, h, z=4)
    page(x, y, w, h)
    (glyph_matrix if kind == "matrix" else glyph_table)(x, y, w, h)
    ax.text(xc + (0.08 if stack else 0), y - 0.18, label, fontsize=FS_ICON, ha="center", va="top", color=INK,
            zorder=8, linespacing=1.2)


# ============================ map ============================================
YQ, YCONN, YMAIN, YUP, YDN, YDESC = 7.6, 6.0, 3.6, 4.8, 2.4, 1.2
qx = [1.9, 4.9, 7.9, 10.9, 13.9, 16.9, 19.9]

# outputs
qcb = output(23.70, 8.58, "QC report", w=3.60, h=1.00)
prb = output(23.55, 3.50, "Pair tables\nand summaries", w=3.70, h=1.22)

route([(0.0, YQ)] + [(x, YQ) for x in qx], QC)
route([(19.9, YQ), (20.9, YQ + 1.0), (qcb[0], YQ + 1.0)], QC)
route([(19.9, YQ), (19.9 - (YQ - YCONN), YCONN), (1.3 + (YCONN - YMAIN), YCONN), (1.3, YMAIN)], QC)
route([(1.3, YMAIN), (5.0, YMAIN)], PEX, z=2)
_dU, _dD = YUP - YMAIN, YMAIN - YDN
route([(5.0, YMAIN), (5.0 + _dU, YUP), (10.5 - _dU, YUP), (10.5, YMAIN)], PEX, z=2)
route([(5.0, YMAIN), (5.0 + _dD, YDN), (10.5 - _dD, YDN), (10.5, YMAIN)], PEX, z=2)
route([(10.5, YMAIN), (prb[0], YMAIN)], PEX, z=2)
_dP = YMAIN - YDESC
route([(1.3, YMAIN), (1.3 + _dP, YDESC), (20.95 - _dP, YDESC), (20.95, YMAIN)], DESC, z=1)

source(0.0, YQ, "ALEdb")
qc_names = ["Load and\nnormalize records", "Select species\nand condition", "Remove starting-\nstrain mutations",
            "Remove\nhypermutators", "Normalize\ngene names", "Remove excluded\nexperiments"]
for x, nm in zip(qx[:-1], qc_names):
    station(x, YQ, nm, QC)
station(qx[-1], YQ, "Cleaned\nmutation table", QC, kind="ix", dx=-0.85, dy=0.45, ha="center", va="bottom")
for x, nm in zip(qx[:-1], ["Species\ntable", "Condition\ntable", "Starting-strain\nmutation list",
                           "Hypermutator\ngene list", "Gene alias table", "Experiment\nexclusion list"]):
    feeder(x, YQ, nm)

station(1.3, YMAIN, "Build binary\nunit matrix", PEX, kind="ix", dx=-0.55, dy=0.0, ha="right", va="center")
feeder(1.3, YMAIN, "User mutation\nor unit table", up=-1.70)
station(5.0, YMAIN, "Testability\nfilter", PEX, kind="ix", dx=-0.35, dy=-0.62)
station(7.75, YUP, "Fisher's exact test", PEX, dy=0.42, va="bottom")
station(7.75, YDN, "DISCOVER", PEX, dy=0.40, va="bottom")
station(10.5, YMAIN, "FDR correction", PEX, kind="ix", dx=0.42, dy=0.42, ha="left", va="bottom")
station(7.75, YDESC, "Pearson / phi", DESC, dy=-0.45, va="top")

# ============================ callouts: what each output holds ===============
callout(qcb[0], qcb[1], qcb[2], 20.60, 26.75, 7.50, 5.40)
for xc, lab, stack in [(21.95, "QC\nsummary", False), (23.65, "Review\ntables", True),
                       (25.35, "Removed\nrecords", True)]:
    doc(xc, 7.40, lab, stack=stack)

callout(prb[0], prb[1], prb[2], 20.55, 26.65, 2.40, -2.05)
for xc, lab in [(21.55, "All tested\npairs"), (23.55, "Significant\npairs"), (25.55, "Experiment\nsummary")]:
    doc(xc, 2.20, lab)
doc(23.55, 0.10, "Per-experiment\nmatrices", kind="matrix", stack=True)

# ============================ legend =========================================
handles = [Line2D([], [], color=QC, lw=LW, solid_capstyle="round", label="Data preparation"),
           Line2D([], [], color=PEX, lw=LW, solid_capstyle="round", label="Statistical testing"),
           Line2D([], [], color=DESC, lw=LW, solid_capstyle="round", label="Descriptive correlation")]
leg1 = ax.legend(handles=handles, loc="lower left", bbox_to_anchor=(-1.045, -2.5), bbox_transform=ax.transData,
                 fontsize=FS_LINE, frameon=False, handlelength=1.6, labelspacing=0.7)
ax.add_artist(leg1)
key = [Line2D([], [], ls="", marker="o", ms=11, mfc="white", mec=INK, mew=2.5, label="Stage"),
       Line2D([], [], ls="", marker="o", ms=15, mfc=INK, mec=INK, mew=2.5, label="Shared stage (interchange)"),
       Line2D([], [], ls="", marker="s", ms=11, mfc="white", mec=FEED, mew=2.0, label="User-supplied table"),
       Line2D([], [], ls="", marker="s", ms=13, mfc="white", mec=OUTC, mew=2.4, label="Output")]
ax.legend(handles=key, loc="lower left", bbox_to_anchor=(7.79, -2.5), bbox_transform=ax.transData,
          fontsize=FS_LINE, frameon=False, handlelength=1.2, labelspacing=0.7)

ax.set_xlim(XL, XR); ax.set_ylim(YB, YT)
ax.set_aspect("equal"); ax.axis("off")
OUT.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT / "Figure_6.png", dpi=DPI, facecolor="white", bbox_inches="tight")
fig.savefig(OUT / "Figure_6_raw.svg", facecolor="white", bbox_inches="tight")   # fixed for Illustrator next
print("wrote", OUT / "Figure_6.png", "and Figure_6_raw.svg")
