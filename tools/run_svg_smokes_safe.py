from pathlib import Path
import os
import subprocess
import sys
import time

ROOT = Path.cwd()
REPORT = ROOT / "outputs/reports/svg_smoke_safe_run.log"
REPORT.parent.mkdir(parents=True, exist_ok=True)

SCRIPTS = [
    "tools/smoke_svg_backend.py",
    "tools/smoke_workstation_frame_svg.py",
    "tools/smoke_ndc_primitives_svg.py",
    "tools/smoke_contour_viewport_svg.py",
    "tools/smoke_contour_panel_svg.py",
    "tools/smoke_map_grid_svg.py",
    "tools/smoke_map_grid_labels_svg.py",
    "tools/smoke_map_panel_svg.py",
    "tools/smoke_panel_svg.py",
    "tools/smoke_panel_main_string_svg.py",
    "tools/smoke_panel_figure_strings_svg.py",
    "tools/smoke_panel_ncl_layout_semantics.py",
    "tools/smoke_panel_rowspec_ncl_semantics.py",
    "tools/smoke_panel_shared_labelbar_svg.py",
    "tools/smoke_plot_strings_svg.py",
    "tools/smoke_svg_labelbar_object_semantics.py",
]

env = os.environ.copy()
env["PYTHONPATH"] = "src"

def write(log, text):
    print(text, flush=True)
    log.write(text + "\n")
    log.flush()

def main():
    failed = []

    with REPORT.open("w", encoding="utf-8") as log:
        write(log, f"SVG smoke safe run")
        write(log, f"root: {ROOT}")
        write(log, "")

        for script in SCRIPTS:
            path = ROOT / script
            if not path.exists():
                failed.append((script, "missing", None))
                write(log, f"❌ MISSING {script}")
                write(log, "")
                continue

            write(log, f"== START {script} ==")
            start = time.time()

            try:
                result = subprocess.run(
                    [sys.executable, "-X", "faulthandler", script],
                    cwd=ROOT,
                    env=env,
                    text=True,
                    capture_output=True,
                    timeout=20,
                )
                elapsed = time.time() - start

                if result.stdout:
                    log.write(result.stdout)
                    if not result.stdout.endswith("\n"):
                        log.write("\n")

                if result.stderr:
                    log.write("[stderr]\n")
                    log.write(result.stderr)
                    if not result.stderr.endswith("\n"):
                        log.write("\n")

                if result.returncode == 0:
                    write(log, f"✅ PASS {script} ({elapsed:.2f}s)")
                else:
                    failed.append((script, "returncode", result.returncode))
                    write(log, f"❌ FAIL {script} returncode={result.returncode} ({elapsed:.2f}s)")

            except subprocess.TimeoutExpired as exc:
                failed.append((script, "timeout", None))
                write(log, f"⏱️ TIMEOUT {script} after 20s")
                if exc.stdout:
                    log.write(str(exc.stdout) + "\n")
                if exc.stderr:
                    log.write("[stderr]\n")
                    log.write(str(exc.stderr) + "\n")

            write(log, "")

        write(log, "== SUMMARY ==")
        if failed:
            for script, kind, code in failed:
                write(log, f"❌ {script}: {kind} {code}")
            write(log, "")
            write(log, f"report: {REPORT}")
            raise SystemExit(1)

        write(log, "✅ all SVG smoke scripts passed")
        write(log, f"report: {REPORT}")

if __name__ == "__main__":
    main()
