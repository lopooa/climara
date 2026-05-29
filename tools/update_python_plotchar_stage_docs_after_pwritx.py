from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

STAGE_STATUS = ROOT / "docs" / "python_plotchar_stage_status.md"
ROADMAP = ROOT / "docs" / "python_plotchar_completion_roadmap.md"

REQUIRED_FILES = [
    "src/climara/graphics/_plotchar_pwritx_nonfontcap.py",
    "src/climara/graphics/_plotchar_pwritx_runtime_strategy.py",
    "src/climara/graphics/_plotchar_pwritx_provider.py",
    "src/climara/graphics/pwritx_plotchar.py",
    "docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md",
    "docs/ncl_plotchar_pwritx_formula_audit.md",
    "docs/python_plotchar_pwritx_provider_backend_status.md",
    "tools/smoke_python_plotchar_pwritx_public_facade.py",
    "tools/smoke_python_plotchar_pwritx_provider_backend_status.py",
]


STAGE_ADDENDUM = """
## PWRITX / font0 / non-fontcap stage addendum

The PWRITX/font0/non-fontcap branch now has a guarded boundary and explicit provider-backed facade.

### Completed for this branch

- Exact branch packet: `docs/ncl_plotchar_pwritx_nonfontcap_exact_branch_packet.md`
- Formula audit: `docs/ncl_plotchar_pwritx_formula_audit.md`
- Boundary module: `src/climara/graphics/_plotchar_pwritx_nonfontcap.py`
- Runtime strategy contract: `src/climara/graphics/_plotchar_pwritx_runtime_strategy.py`
- Metrics-provider contract: `src/climara/graphics/_plotchar_pwritx_provider.py`
- Public facade: `src/climara/graphics/pwritx_plotchar.py`
- Status document: `docs/python_plotchar_pwritx_provider_backend_status.md`

### Supported opt-in mechanism

```python
from climara.graphics.pwritx_plotchar import compute_plchhq_with_pwritx_provider
```

The facade requires a source-mapped `PwritxMetricsProvider`.

### Still guarded

- Default PWRITX/font0/non-fontcap path.
- Real PWRITX/font0 metrics without a source-mapped provider.
- Font database lookup not yet mapped into Python.
- Medium / Low / Workstation quality behavior.
- PCGETR-visible side effects not yet fully implemented.

### Boundary rule

This is a provider-backed seam, not a full PWRITX/font0 implementation and not a full NCL PLCHHQ parity claim.
""".strip()


ROADMAP_ADDENDUM = """
## PWRITX branch status update

The PWRITX/font0/non-fontcap branch now has the same staged structure as mapped-coordinate and SIZE/address:

- source-map and exact branch packet
- formula audit
- guarded runtime boundary
- runtime strategy contract
- metrics-provider contract
- explicit public facade
- status document and smoke coverage

This means the branch is structurally ready for future source-mapped implementation work, but the real PWRITX/font0 metrics are still not implemented.

### Recommended next choices

1. Implement real SIZE/address-unit formula only after exact manual mapping.
2. Implement real PWRITX/font0 metrics only after font database and extent side effects are mapped.
3. Start remaining inline function-code commands.
4. Add higher-level TextItem/MultiText/LabelBar examples that use the completed default fontcap subset.

### Updated practical answer

For the current TextItem/fontcap milestone, the project is now close to stage-level closure.

For full NCL PLCHHQ parity, major branches remain and should still be treated as long-term work.
""".strip()


def append_once(path: Path, marker: str, addendum: str) -> None:
    if not path.exists():
        raise SystemExit(f"Missing document: {path}")

    text = path.read_text(encoding="utf-8")
    if marker in text:
        print(f"already updated: {path}")
        return

    if not text.endswith("\n"):
        text += "\n"

    text += "\n" + addendum + "\n"
    path.write_text(text, encoding="utf-8")
    print(f"updated {path}")


def main() -> None:
    missing = [item for item in REQUIRED_FILES if not (ROOT / item).exists()]
    if missing:
        raise SystemExit("Missing required PWRITX stage artifacts:\n" + "\n".join(missing))

    append_once(
        STAGE_STATUS,
        "## PWRITX / font0 / non-fontcap stage addendum",
        STAGE_ADDENDUM,
    )
    append_once(
        ROADMAP,
        "## PWRITX branch status update",
        ROADMAP_ADDENDUM,
    )

    print("PWRITX stage docs are up to date")


if __name__ == "__main__":
    main()
