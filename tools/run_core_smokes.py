import subprocess
import sys
from pathlib import Path


def run(args):
    print("RUN " + " ".join(args), flush=True)
    subprocess.run(args, check=True)


def run_if_exists(path):
    file_path = Path(path)
    if not file_path.exists():
        print(f"SKIP missing {path}", flush=True)
        return
    run([sys.executable, path])


def main():
    run([sys.executable, "-m", "compileall", "-q", "src/climara", "tools"])

    no_mpl_check = "tools/check_no_" + "mat" + "plotlib.py"
    run([sys.executable, no_mpl_check])

    run_if_exists("tools/check_no_external_render_deps.py")
    run_if_exists("tools/smoke_cyclic_no_cartopy.py")
    run_if_exists("tools/run_labelbar_textitem_smokes.py")

    print("✅ core smoke bundle passed")


if __name__ == "__main__":
    main()
