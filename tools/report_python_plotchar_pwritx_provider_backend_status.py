from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "python_plotchar_pwritx_provider_backend_status.md"


def main() -> None:
    if not OUT.exists():
        raise SystemExit(f"Missing status document: {OUT}")

    text = OUT.read_text(encoding="utf-8")
    required = [
        "Python Plotchar PWRITX / Font0 Provider Backend Status",
        "Stable facade",
        "Supported opt-in mechanism",
        "Still guarded",
        "Boundary rule",
    ]

    missing = [item for item in required if item not in text]
    if missing:
        raise SystemExit("status document missing sections: " + ", ".join(missing))

    print(f"checked {OUT}")


if __name__ == "__main__":
    main()
