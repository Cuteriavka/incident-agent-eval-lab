"""Create and open the repository-external N00 learning workbook."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

from cloudopsbench_tutorial import ensure_external_path, load_pre_reveal_case


PROJECT_ROOT = Path(__file__).resolve().parents[1]
STARTER = PROJECT_ROOT / "notebooks" / "00_cloudopsbench_orientation.ipynb"
LOCAL_CONFIG = PROJECT_ROOT / ".learning.local.json"


def prepare_external_workbook(*, refresh_starter: bool = False) -> Path:
    if not LOCAL_CONFIG.is_file():
        raise FileNotFoundError(
            "Missing ignored .learning.local.json. Copy the one-field example from "
            "docs/data/CLOUDOPSBENCH_TUTORIAL.md after preparing the external data."
        )
    config = json.loads(LOCAL_CONFIG.read_text(encoding="utf-8"))
    tutorial_root = ensure_external_path(
        Path(config["cloudopsbench_tutorial_root"])
    )
    load_pre_reveal_case(tutorial_root)

    workbook_root = tutorial_root / "workbook"
    workbook_root.mkdir(parents=True, exist_ok=True)
    workbook = workbook_root / STARTER.name
    if refresh_starter or not workbook.exists():
        shutil.copy2(STARTER, workbook)

    runtime_config = {
        "project_root": str(PROJECT_ROOT),
        "tutorial_root": str(tutorial_root),
    }
    (workbook_root / ".n00.runtime.json").write_text(
        json.dumps(runtime_config, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return workbook


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Create the external workbook without starting JupyterLab.",
    )
    parser.add_argument(
        "--refresh-starter",
        action="store_true",
        help="Replace the external workbook with the current empty starter.",
    )
    args = parser.parse_args()
    workbook = prepare_external_workbook(refresh_starter=args.refresh_starter)
    if args.prepare_only:
        print(f"N00 external workbook ready: {workbook}")
        return

    subprocess.run(
        [
            sys.executable,
            "-m",
            "jupyterlab",
            f"--ServerApp.root_dir={workbook.parent}",
            workbook.name,
        ],
        cwd=workbook.parent,
        check=True,
    )


if __name__ == "__main__":
    main()
