from __future__ import annotations

from climara.graphics._plotchar_state import (
    PlotcharState,
    PlotcharStateError,
    PlotcharUnsupportedError,
    build_textitem_plotchar_state,
    normalize_plotchar_font_number,
    pcrset,
)


def almost_equal(value, expected, tol=1e-12):
    assert abs(value - expected) <= tol, (value, expected)


def main():
    state = PlotcharState.defaults()

    almost_equal(state.pcgetr("DL"), 0.0)
    almost_equal(state.pcgetr("DR"), 0.0)
    almost_equal(state.pcgetr("DB"), 0.0)
    almost_equal(state.pcgetr("DT"), 0.0)
    almost_equal(state.pcgetr("TE"), 0.0)
    almost_equal(state.pcgetr("CS"), 0.0)
    almost_equal(state.pcgetr("PH"), 21.0)
    almost_equal(state.pcgetr("PW"), 16.0)

    state.pcseti("TE", 9)
    almost_equal(state.pcgetr("TE"), 1.0)
    state.pcseti("TE", -9)
    almost_equal(state.pcgetr("TE"), 0.0)

    state.pcseti("QU", 9)
    almost_equal(state.pcgetr("QU"), 2.0)
    state.pcseti("QU", -9)
    almost_equal(state.pcgetr("QU"), 0.0)

    state.pcsetr("CS", 0.125)
    almost_equal(state.cons, 0.0625)
    almost_equal(state.pcgetr("CS"), 0.125)

    state.pcsetr("PH", 21.0)
    state.pcsetr("PW", 10.5)
    almost_equal(state.pcgetr("PH"), 21.0)
    almost_equal(state.pcgetr("PW"), 10.5)
    almost_equal(state.ymul[0], 1.0)
    almost_equal(state.xmul[0], 10.5 / 16.0)

    state.pcsetc("FC", "~")
    assert state.nfcc == ord("~")

    state.pcsetc("FN", "HELVETICA")
    almost_equal(state.pcgetr("FN"), 21.0)
    state.pcseti("FN", 99)
    almost_equal(state.pcgetr("FN"), 1.0)
    assert normalize_plotchar_font_number(137) == 137
    assert normalize_plotchar_font_number(138) == 1

    state._set_extent_vectors_from_plchhq(dl=0.11, dr=0.22, db=0.033, dt=0.044)
    almost_equal(state.pcgetr("DL"), 0.11)
    almost_equal(state.pcgetr("DR"), 0.22)
    almost_equal(state.pcgetr("DB"), 0.033)
    almost_equal(state.pcgetr("DT"), 0.044)

    state.reset()
    almost_equal(state.pcgetr("DL"), 0.0)
    almost_equal(state.pcgetr("DR"), 0.0)
    almost_equal(state.pcgetr("DB"), 0.0)
    almost_equal(state.pcgetr("DT"), 0.0)
    almost_equal(state.pcgetr("FN"), 0.0)

    fresh = pcrset()
    assert isinstance(fresh, PlotcharState)
    almost_equal(fresh.pcgetr("PH"), 21.0)

    try:
        state.pcsetc("FC", "")
    except PlotcharStateError as exc:
        assert "non-empty" in str(exc)
    else:
        raise AssertionError("empty function-code character must stay guarded")

    try:
        state.plchhq(0.5, 0.5, "ABC", 0.02, 360.0, -1.0)
    except PlotcharUnsupportedError as exc:
        message = str(exc)
        assert "PLCHHQ" in message
        assert "fixed-width" in message
        assert "character-count" in message
    else:
        raise AssertionError("PLCHHQ must not be replaced by a heuristic")

    try:
        from climara.graphics._ncl_plotchar_textitem import (
            build_ncl_plotchar_textitem_state,
        )
        from climara.graphics._text_semantics import build_text_item_semantics
    except Exception:
        build_ncl_plotchar_textitem_state = None
        build_text_item_semantics = None

    if build_ncl_plotchar_textitem_state is not None and build_text_item_semantics is not None:
        semantics = build_text_item_semantics(
            "ABC",
            func_code="~",
            font=21,
            font_height=0.04,
            font_aspect=2.0,
            font_quality="High",
            constant_spacing=0.125,
        )
        textitem_state = build_ncl_plotchar_textitem_state(semantics)
        pstate = build_textitem_plotchar_state(textitem_state)
        almost_equal(pstate.pcgetr("TE"), 1.0)
        almost_equal(pstate.pcgetr("CS"), 0.125)
        almost_equal(pstate.pcgetr("PH"), 21.0)
        almost_equal(pstate.pcgetr("PW"), 10.5)
        almost_equal(pstate.pcgetr("QU"), 0.0)
        almost_equal(pstate.pcgetr("FN"), 21.0)
        assert pstate.nfcc == ord("~")

    print("✅ Python Plotchar state model smoke passed")


if __name__ == "__main__":
    main()
