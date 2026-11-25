"""Execute notebooks from a clean kernel and log the outcome.

Run: python tools/run_notebooks.py [path_or_module ...]
Without arguments every module is executed.
"""

import json
import sys
import time
from pathlib import Path

import nbformat
from nbclient import NotebookClient

sys.path.insert(0, str(Path(__file__).parent))
import build_modules  # noqa: E402
import nbgen  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
LOG = ROOT / "experiments" / "metadata" / "execution_log.json"


def run_one(path, timeout=900):
    notebook = nbformat.read(path, as_version=4)
    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name="python3",
        resources={"metadata": {"path": str(path.parent)}},
    )
    start = time.time()
    status, error = "ok", ""
    try:
        client.execute()
    except Exception as exc:
        status, error = "failed", str(exc)[-1800:]
    nbformat.write(notebook, path)
    return {
        "notebook": str(path.relative_to(ROOT)),
        "status": status,
        "seconds": round(time.time() - start, 1),
        "error": error,
    }


def find_paths(targets):
    specs = build_modules.all_specs()
    if not targets:
        return [nbgen.notebook_path(spec) for spec in specs]
    paths = []
    for spec in specs:
        for target in targets:
            if target in (spec["module"], spec["path"]):
                paths.append(nbgen.notebook_path(spec))
    return paths


def main(targets):
    paths = find_paths(targets)
    log = json.loads(LOG.read_text()) if LOG.exists() else {}
    failed = False
    for path in paths:
        result = run_one(path)
        log[result["notebook"]] = {"status": result["status"], "seconds": result["seconds"]}
        print(result["status"], result["seconds"], result["notebook"], flush=True)
        if result["error"]:
            failed = True
            print(result["error"], flush=True)
        LOG.parent.mkdir(parents=True, exist_ok=True)
        LOG.write_text(json.dumps(log, indent=2, sort_keys=True) + "\n")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
