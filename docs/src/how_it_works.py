"""Render docs/how-it-works.gif.

Usage: python3 docs/src/how_it_works.py
Needs Pillow and fontconfig (fc-match) with Noto Sans and DejaVu Sans / Sans Mono.
The handwriting font (Kalam, SIL OFL) is in docs/src/fonts/.
"""
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "how-it-works.gif"
W, H, SCALE = 960, 540, 2

NAVY, RED, GREEN = "#1A3A5F", "#B5483E", "#2F7A4A"
GREY, DARK, LIGHT = "#777777", "#333333", "#A0A4AC"
PANEL, PANEL_LINE = "#F6F7FA", "#D8DAE2"
PROMPT, PROMPT_LINE = "#E8EFF8", "#C9D8EC"
CARD_LINE = "#DADDE3"
HL, HL_LINE = "#FFF3BF", "#E8C84A"


def fc(pattern):
    return subprocess.run(["fc-match", "-f", "%{file}", pattern], capture_output=True, text=True, check=True).stdout


FONT_FILES = {
    "sans": fc("Noto Sans"),
    "bold": fc("Noto Sans:bold"),
    "mono": fc("DejaVu Sans Mono"),
    "monobold": fc("DejaVu Sans Mono:bold"),
    "symbol": fc("DejaVu Sans"),
    "hand": str(HERE / "fonts" / "Kalam-Bold.ttf"),
}
SYMBOLS = set("✓✗→")
_fonts = {}


def font(kind, size):
    key = (kind, size)
    if key not in _fonts:
        _fonts[key] = ImageFont.truetype(FONT_FILES[kind], size * SCALE)
    return _fonts[key]


def s(*v):
    return tuple(x * SCALE for x in v)


def runs(spans):
    # Split spans so that arrows and check marks use a font that has them.
    for text, kind, color in spans:
        buf = ""
        for ch in text:
            if ch in SYMBOLS and not kind.startswith("mono"):
                if buf:
                    yield buf, kind, color
                    buf = ""
                yield ch, "symbol", color
            else:
                buf += ch
        if buf:
            yield buf, kind, color


def text_width(spans, size):
    return sum(font(k, size).getlength(t) for t, k, _ in runs(spans)) / SCALE


def draw_spans(d, x, y, spans, size):
    # Draw on a shared baseline so fallback symbols line up with the text.
    parts = list(runs(spans))
    base = y + max((font(k, size).getmetrics()[0] for _, k, _ in parts if k != "symbol"), default=0) / SCALE
    for t, k, c in parts:
        d.text(s(x, base), t, font=font(k, size), fill=c, anchor="ls")
        x += font(k, size).getlength(t) / SCALE


def wrap(spans, size, width):
    """Wrap a list of (text, kind, color) spans into lines no wider than width."""
    words = []
    for text, kind, color in spans:
        for i, w in enumerate(text.split(" ")):
            words.append([w, kind, color, i > 0 or (words and text.startswith(" "))])
    lines, line = [], []
    for w, kind, color, space in words:
        piece = (" " if line and space else "") + w
        trial = line + [(piece, kind, color)]
        if line and text_width(trial, size) > width:
            lines.append(line)
            line = [(w, kind, color)]
        else:
            line = trial
    if line:
        lines.append(line)
    return lines


def box(d, x0, y0, x1, y1, fill, outline, width=1, radius=8, dash=False):
    if dash:
        d.rounded_rectangle(s(x0, y0, x1, y1), radius=radius * SCALE, fill=fill)
        step = 5
        for x in range(x0 + radius, x1 - radius, step * 2):
            d.line(s(x, y0, min(x + step, x1 - radius), y0), fill=outline, width=width * SCALE)
            d.line(s(x, y1, min(x + step, x1 - radius), y1), fill=outline, width=width * SCALE)
        for y in range(y0 + radius, y1 - radius, step * 2):
            d.line(s(x0, y, x0, min(y + step, y1 - radius)), fill=outline, width=width * SCALE)
            d.line(s(x1, y, x1, min(y + step, y1 - radius)), fill=outline, width=width * SCALE)
        return
    d.rounded_rectangle(s(x0, y0, x1, y1), radius=radius * SCALE, fill=fill, outline=outline, width=width * SCALE)


class Slide:
    """One slide: two panels, a left stack of cards and a right repo panel."""

    def __init__(self, number, actor, caption, dot):
        self.number, self.actor, self.caption, self.dot = number, actor, caption, dot
        self.left = []  # (kind, lines)
        self.tree = []  # (text, color, bold)
        self.tree_hl = None
        self.right = []  # (lines, size, mono, highlighted line index)
        self.popup = None

    def render(self):
        img = Image.new("RGB", s(W, H), "white")
        d = ImageDraw.Draw(img)
        draw_spans(d, 27, 14, [(f"{self.number}. ", "hand", NAVY), (self.actor, "hand", NAVY)], 28)
        title_w = text_width([(f"{self.number}. {self.actor}", "hand", NAVY)], 28)
        draw_spans(d, 27 + title_w + 16, 30, [(self.caption, "sans", GREY)], 15)

        box(d, 27, 73, 455, 517, PANEL, PANEL_LINE, width=2, radius=10)
        box(d, 477, 73, 933, 517, PANEL, PANEL_LINE, width=2, radius=10)
        d.ellipse(s(43, 93, 53, 103), fill=self.dot)
        draw_spans(d, 62, 88, [(self.actor, "bold", "#555555")], 14)
        draw_spans(d, 494, 88, [("repo", "bold", "#555555")], 14)

        y = 119
        for kind, spans in self.left:
            size = 15
            lines = [l for sp in spans for l in (wrap(sp, size, 370) if sp else [[]])]
            h = 22 * len(lines) + 18
            if kind == "prompt":
                box(d, 44, y, 438, y + h, PROMPT, PROMPT_LINE)
            elif kind == "note":
                box(d, 44, y, 438, y + h, None, "#B8BCC6", dash=True)
            else:
                box(d, 44, y, 438, y + h, "white", CARD_LINE)
            for i, line in enumerate(lines):
                draw_spans(d, 58, y + 8 + 22 * i, line, size)
            y += h + 9

        ty = 120
        for i, (text, color, bold) in enumerate(self.tree):
            if self.tree_hl == i:
                box(d, 492, ty - 3, 917, ty + 22, HL, HL_LINE, radius=5)
            indent = 15 if i else 0
            draw_spans(d, 501 + indent, ty, [(text, "monobold" if bold else "mono", color)], 14)
            ty += 24

        y = ty + 12
        for lines, size, hl in self.right:
            wrapped = []
            for idx, sp in enumerate(lines):
                for l in wrap(sp, size, 395):
                    wrapped.append((l, idx))
            lh = size + 7
            h = lh * len(wrapped) + 16
            box(d, 494, y, 916, y + h, "white", CARD_LINE)
            for i, (line, idx) in enumerate(wrapped):
                if hl == idx:
                    box(d, 503, y + 6 + lh * i, 907, y + 6 + lh * (i + 1), HL, HL_LINE, radius=4)
                draw_spans(d, 508, y + 8 + lh * i, line, size)
            y += h + 10

        if self.popup:
            title, sub = self.popup
            sh = Image.new("RGBA", s(W, H), (0, 0, 0, 0))
            ImageDraw.Draw(sh).rounded_rectangle(s(318, 222, 641, 330), radius=14 * SCALE, fill=(0, 0, 0, 40))
            img.paste(sh, (0, 0), sh)
            box(d, 314, 214, 645, 322, "white", NAVY, width=3, radius=12)
            tw = text_width([(title, "hand", NAVY)], 34)
            draw_spans(d, 480 - tw / 2, 228, [(title, "hand", NAVY)], 34)
            sw = text_width([(sub, "sans", GREY)], 14)
            draw_spans(d, 480 - sw / 2, 284, [(sub, "sans", GREY)], 14)
        return img.resize((W, H), Image.LANCZOS)


def build():
    frames = []

    def hold(slide, n):
        frames.append((slide.render(), n))

    # Slide 1: A's Claude Code tries two approaches and keeps what it learned.
    a = Slide(1, "A’s Claude Code", "what it learns stays in .memory/", NAVY)
    a.tree = [(".memory/", DARK, False), ("INDEX.md", DARK, False)]
    hold(a, 3)
    a.left.append(("prompt", [[("Improve the accuracy of circle symbol detection", "sans", "black")]]))
    hold(a, 7)
    a.left.append(("card", [[("Try 1: binarize with a fixed threshold", "sans", "black")]]))
    hold(a, 6)
    a.left[-1][1].append([("✗ Circles break up in faint drawings (recall 0.62)", "bold", RED)])
    hold(a, 6)
    a.left.append(("card", [[("Try 2: binarize with an adaptive threshold", "sans", "black")]]))
    hold(a, 6)
    a.left[-1][1].append([("✓ Recall 0.81, only 4 ms slower", "bold", GREEN)])
    hold(a, 5)
    a.left.append(("note", [[("Save it so the next person won't repeat it", "sans", GREY)]]))
    hold(a, 3)
    a.tree.append(("+ 2026-10-20-fixed-threshold-rejected.md", GREEN, True))
    a.tree_hl = 2
    hold(a, 2)
    doc = [
        [("---", "mono", GREY)],
        [("title: Fixed-threshold binarization rejected", "mono", GREY)],
        [("author: user-a   status: current", "mono", GREY)],
        [("---", "mono", GREY)],
    ]
    a.right.append((doc, 12, None))
    hold(a, 3)
    doc += [
        [("## ", "mono", GREY), ("Conclusion", "bold", NAVY)],
        [("Binarize with an adaptive threshold. A fixed threshold is not used.", "sans", "black")],
    ]
    hold(a, 3)
    doc += [
        [("## ", "mono", GREY), ("Evidence", "bold", NAVY)],
        [("Recall: fixed 0.62 / adaptive 0.81 (30 evaluation images)", "sans", "black")],
    ]
    hold(a, 2)
    a.tree_hl = 1
    hold(a, 2)
    a.right.append((
        [
            [("INDEX.md", "mono", GREY)],
            [("+ [Fixed-threshold binarization rejected](2026-10-20-…)", "monobold", GREEN)],
        ],
        12,
        None,
    ))
    hold(a, 8)
    a.tree_hl = None
    a.popup = ("PR → merge", "Memories are reviewed with the code")
    hold(a, 8)

    # Slide 2: B's Claude Code reads the memory before starting.
    b = Slide(2, "B’s Claude Code", "checks memories before starting", RED)
    b.tree = [
        (".memory/", DARK, False),
        ("INDEX.md", DARK, False),
        ("2026-10-20-fixed-threshold-rejected.md", DARK, False),
        ("2026-10-24-eval-set-expanded.md", LIGHT, False),
    ]
    # Fade from the end of slide 1 to the empty slide 2.
    last, first = frames[-1][0], b.render()
    for i in range(1, 7):
        frames.append((Image.blend(last, first, i / 6), 1))
    hold(b, 3)
    b.left.append(("prompt", [[("Switching to a fixed threshold would be faster", "sans", "black")]]))
    hold(b, 7)
    b.left.append(("note", [[("Check .memory/INDEX.md → 1 related memory", "sans", GREY)]]))
    b.tree_hl = 1
    index = [
        [("INDEX.md", "mono", GREY)],
        [("[Fixed-threshold binarization rejected](2026-10-20-…)", "mono", "black")],
        [("[Evaluation set grown to 45 images](2026-10-24-…)", "mono", LIGHT)],
    ]
    b.right.append((index, 12, None))
    hold(b, 3)
    b.right[0] = (index, 12, 1)
    hold(b, 7)
    b.tree_hl = 2
    b.right.append((
        [
            [("title: Fixed-threshold binarization rejected", "mono", GREY)],
            [("## ", "mono", GREY), ("Conclusion", "bold", NAVY), ("  Binarize with an adaptive threshold.", "sans", "black")],
            [("## ", "mono", GREY), ("Evidence", "bold", NAVY), ("  Recall: fixed 0.62 / adaptive 0.81", "sans", "black")],
        ],
        12,
        None,
    ))
    hold(b, 6)
    answer = [
        [("That approach was ", "sans", "black"), ("tried on 10/20 and rejected.", "bold", "black")],
        [("Circles broke up in faint drawings and recall fell from 0.81 to 0.62. It only saves 4 ms.", "sans", "black")],
    ]
    b.left.append(("card", answer))
    hold(b, 8)
    answer.append([("→ Keep binarization, make HoughCircles lighter", "bold", GREEN)])
    hold(b, 20)
    b.tree_hl = None
    b.right[0] = (index, 12, None)
    hold(b, 32)
    return frames


def save(frames):
    # One shared palette keeps colors stable between frames.
    strip = Image.new("RGB", (W, H * len(frames)))
    for i, (f, _) in enumerate(frames):
        strip.paste(f, (0, H * i))
    palette = strip.quantize(colors=255, method=Image.Quantize.MEDIANCUT)
    images = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f, _ in frames]
    images[0].save(
        OUT,
        save_all=True,
        append_images=images[1:],
        duration=[n * 100 for _, n in frames],
        loop=0,
        optimize=True,
    )


if __name__ == "__main__":
    frames = build()
    save(frames)
    print(OUT, sum(n for _, n in frames) / 10, "s")
