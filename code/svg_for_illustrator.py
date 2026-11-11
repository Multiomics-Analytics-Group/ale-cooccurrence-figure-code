"""Make a matplotlib SVG import cleanly in Adobe Illustrator, without changing the drawing:
1. each line of a multi-line label (written by matplotlib as a left-anchored line placed with the
   layout font's widths) is anchored at its center, or at its right end, at exactly the point
   matplotlib computed, so a font change (DejaVu Sans -> Arial) cannot shift it sideways. The
   widths are measured with the font list Figure_6.py sets, so they match its layout.
2. 'font: 700 16px ...' becomes separate font-family, font-size and font-weight properties.
3. clip paths, which Illustrator drops with a warning, are removed (nothing here needs them).

usage, from the folder that holds code/ and figures/, after code/Figure_6.py:
  python code/svg_for_illustrator.py figures/Figure_6/Figure_6_raw.svg figures/Figure_6/Figure_6.svg "Build binary|unit matrix" ""
writes Figure_6.svg (run_all.sh then deletes Figure_6_raw.svg). The last two arguments list the
label lines drawn with ha="right" and with ha="left", separated by "|"."""
import re
import sys

import matplotlib as mpl
from matplotlib.font_manager import FontProperties
from matplotlib.textpath import TextToPath

src, dst = sys.argv[1], sys.argv[2]
RIGHT = set(filter(None, sys.argv[3].split("|")))      # lines of labels drawn with ha="right"
LEFT = set(filter(None, sys.argv[4].split("|")))       # lines of labels drawn with ha="left"
mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]    # as in Figure_6.py
t2p = TextToPath()
s = open(src, encoding="utf-8").read()


def width(text, size, bold):
    fp = FontProperties(family="sans-serif", size=size, weight="bold" if bold else "normal")
    return t2p.get_text_width_height_descent(text, fp, ismath=False)[0]


def anchor(m):
    style, x, y, text = m.group(1), float(m.group(2)), float(m.group(3)), m.group(4)
    size = float(re.search(r"([\d.]+)px", style).group(1))
    bold = re.search(r"font:\s*(700|bold)\s", style) is not None
    plain = text.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">")
    if plain in LEFT:
        return m.group(0)
    w = width(plain, size, bold)
    if plain in RIGHT:
        ax_, how = x + w, "end"
    else:
        ax_, how = x + w / 2, "middle"
    return (f'<text style="{style}; text-anchor: {how}" x="{ax_:.6f}" y="{y:.6f}">{text}</text>')


n_lines = len(re.findall(r'<text style="[^"]*" transform="translate\(', s))
s = re.sub(r'<text style="([^"]*)" transform="translate\(([-\d.]+) ([-\d.]+)\)">([^<]*)</text>', anchor, s)


def longhand(m):
    parts = m.group(1).split()
    size = next(p for p in parts if p.endswith("px"))
    out = f"font-family: Arial, Helvetica, sans-serif; font-size: {size}"
    if "700" in parts or "bold" in parts:
        out += "; font-weight: bold"
    if "italic" in parts:
        out += "; font-style: italic"
    return out


s = re.sub(r'font:\s*([^;"]*)', longhand, s)
s = re.sub(r'\s*clip-path="url\(#[^)]*\)"', "", s)
s = re.sub(r'<clipPath id="[^"]*">.*?</clipPath>\s*', "", s, flags=re.S)
open(dst, "w", encoding="utf-8").write(s)
print("multi-line lines anchored:", n_lines)
