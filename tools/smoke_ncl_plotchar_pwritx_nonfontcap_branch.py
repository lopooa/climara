from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from climara.graphics._text_bbox import build_text_item_bbox_request, compute_text_item_bbox
from climara.graphics._text_semantics import build_text_item_semantics


ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "docs" / "ncl_plotchar_pwritx_nonfontcap_branch_source_map.md"


def assert_guarded(message_part: str, func) -> None:
    try:
        func()
    except Exception as exc:
        message = str(exc)
        assert message_part in message, message
    else:
        raise AssertionError(f"Expected guarded failure containing {message_part!r}")


def compute_text(text: str, *, font=21, font_quality="High"):
    semantics = build_text_item_semantics(
        text,
        direction="Across",
        func_code="~",
        just="CenterCenter",
        angle=0.0,
        font=font,
        font_height=0.03,
        font_quality=font_quality,
    )
    request = build_text_item_bbox_request(semantics, x=0.5, y=0.5)
    return compute_text_item_bbox(request)


def main() -> None:
    subprocess.run(
        [sys.executable, "tools/report_ncl_plotchar_pwritx_nonfontcap_branch.py"],
        cwd=ROOT,
        check=True,
    )

    if not DOC.exists():
        raise AssertionError(f"Expected report to exist: {DOC}")

    text = DOC.read_text(encoding="utf-8")
    required = [
        "NCL Plotchar PWRITX / Non-Fontcap Branch Source Map",
        "Current decision",
        "Current supported Python subset",
        "Keyword source windows",
        "Checklist before implementation",
        "Guard rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise AssertionError(
            "PWRITX/non-fontcap source-map report is missing required sections: "
            + ", ".join(missing)
        )

    ok = compute_text("ABC", font=21, font_quality="High")
    assert ok.width > 0.0
    assert ok.height > 0.0

    assert_guarded(
        "PWRITX",
        lambda: compute_text("ABC", font=0, font_quality="High"),
    )

    for quality in ("Medium", "Low", "Workstation"):
        assert_guarded(
            "high-quality fontcap branch" if quality != "Workstation" else "Workstation",
            lambda quality=quality: compute_text("ABC", font=21, font_quality=quality),
        )

    print("✅ NCL Plotchar PWRITX/non-fontcap branch source-map smoke passed")


if __name__ == "__main__":
    main()
