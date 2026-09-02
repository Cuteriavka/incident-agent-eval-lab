from __future__ import annotations

import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NOTEBOOK = PROJECT_ROOT / "notebooks" / "00_cloudopsbench_orientation.ipynb"


def test_public_notebook_has_no_saved_outputs_or_execution_state() -> None:
    payload = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    assert payload["nbformat"] == 4
    code_cells = [cell for cell in payload["cells"] if cell["cell_type"] == "code"]
    assert code_cells
    assert all(cell.get("execution_count") is None for cell in code_cells)
    assert all(cell.get("outputs") == [] for cell in code_cells)


def test_notebook_has_one_learner_todo_and_compare_only_gate() -> None:
    payload = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    tagged = {
        tag
        for cell in payload["cells"]
        for tag in cell.get("metadata", {}).get("tags", [])
    }
    assert "learner-todo" in tagged
    assert "compare-only" in tagged
    assert "completion-checkpoint" in tagged
    assert sum(
        "learner-todo" in cell.get("metadata", {}).get("tags", [])
        for cell in payload["cells"]
    ) == 1


def test_tracked_starter_requires_repository_external_runtime_config() -> None:
    payload = json.loads(NOTEBOOK.read_text(encoding="utf-8"))
    source = "\n".join(
        "".join(cell.get("source", [])) for cell in payload["cells"]
    )
    assert ".n00.runtime.json" in source
    assert "请勿直接运行仓库中的 starter" in source
    assert "scripts\\start_n00.py" in source
