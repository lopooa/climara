from pathlib import Path

from climara.graphics._plotchar_fontcap import glyphs_to_rdgu, load_fontcap
from climara.graphics._plotchar_svg_runtime import _pieces_from_rdgu_glyph


def fontcap_dir():
    return Path("/mnt/d/Projects/NCL/common/src/fontcap")


def stats_for_text(text, font_number=21):
    fontcap = load_fontcap(font_number, fontcap_dir())
    glyphs = [fontcap.glyph_for_ascii(ord(char)) for char in text]
    rdgu_glyphs = glyphs_to_rdgu(
        glyphs,
        fontcap.metrics,
        chgt=21.0,
    )

    total_pieces = 0
    stroke_pieces = 0
    fillable_pieces = 0
    total_points = 0
    fillable_points = 0

    for char, glyph in zip(text, rdgu_glyphs):
        pieces = _pieces_from_rdgu_glyph(glyph)
        char_total = len(pieces)
        char_fillable = sum(1 for _, fillable in pieces if fillable)
        char_stroke = char_total - char_fillable

        char_points = sum(len(points) for points, _ in pieces)
        char_fillable_points = sum(len(points) for points, fillable in pieces if fillable)

        total_pieces += char_total
        stroke_pieces += char_stroke
        fillable_pieces += char_fillable
        total_points += char_points
        fillable_points += char_fillable_points

        print(
            f"{char!r}: pieces={char_total:3d} "
            f"stroke={char_stroke:3d} fillable={char_fillable:3d} "
            f"points={char_points:4d} fillable_points={char_fillable_points:4d}"
        )

    print()
    print(f"text: {text!r}")
    print(f"total pieces: {total_pieces}")
    print(f"stroke pieces: {stroke_pieces}")
    print(f"fillable pieces: {fillable_pieces}")
    print(f"total points: {total_points}")
    print(f"fillable points: {fillable_points}")

    if fillable_pieces == 0:
        print()
        print("fill conclusion: no source-marked fillable pieces detected")
        print("do not claim solid/fill glyph parity for this fontcap path")
    else:
        print()
        print("fill conclusion: source-marked fillable pieces detected")
        print("fill rendering may be enabled only for these marked pieces")


def main():
    for text in ["ABC", "O0@%&", "abcdefghijklmnopqrstuvwxyz"]:
        print("=" * 72)
        stats_for_text(text, font_number=21)


if __name__ == "__main__":
    main()
