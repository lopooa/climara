from __future__ import annotations

import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "adjusted_labelbar_supplied_metrics_svg.py"


def load_example_main():
    if not EXAMPLE.exists():
        raise FileNotFoundError(EXAMPLE)

    spec = importlib.util.spec_from_file_location(
        "adjusted_labelbar_supplied_metrics_svg_example",
        EXAMPLE,
    )

    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load example module from {EXAMPLE}")

    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.main


def main():
    example_main = load_example_main()

    with TemporaryDirectory() as tmp:
        output = example_main(tmp)

        assert isinstance(output, Path)
        assert output.exists()
        assert output.name == "adjusted_labelbar_supplied_metrics.svg"

        svg = output.read_text(encoding="utf-8")

        assert svg.startswith("<svg ")
        assert 'data-climara-labelbar-adjusted="supplied-plotchar-metrics"' in svg
        assert "Adjusted LabelBar demo" in svg
        assert "<polygon " in svg
        assert "<line " in svg
        assert "<text " in svg
        assert "Cold" in svg
        assert "Hot" in svg

    print("✅ adjusted LabelBar supplied-metrics example smoke passed")


if __name__ == "__main__":
    main()
