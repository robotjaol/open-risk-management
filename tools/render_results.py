"""Write saved results into each module README. Run: python tools/render_results.py"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import build_modules  # noqa: E402
import nbgen  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
MAX_ROWS = 28


def short(value):
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def scalar_rows(metrics):
    rows = []
    for key, value in metrics.items():
        if key.startswith("acceptance"):
            continue
        if isinstance(value, (int, float, bool)) or (isinstance(value, str) and len(value) <= 70):
            rows.append((key, short(value)))
        elif isinstance(value, dict) and 0 < len(value) <= 16:
            scalar_types = (int, float, bool, str)
            if all(isinstance(v, scalar_types) and len(str(v)) <= 40 for v in value.values()):
                for sub_key, sub_value in value.items():
                    rows.append((f"{key}.{sub_key}", short(sub_value)))
    return rows[:MAX_ROWS]


def acceptance_flags(metrics):
    flags = {}
    for key, value in metrics.items():
        if key.startswith("acceptance") and isinstance(value, dict):
            for name, flag in value.items():
                if isinstance(flag, bool):
                    flags[name] = flag
    return flags


def block_text(result):
    lines = [
        f"Source: `experiments/results/{result['module']}.json`. Data kind: **{result['data_kind']}**. "
        f"Dataset: `{result['dataset']}`. Observations: {result['n_obs']}. Seed: {result['seed']}. "
        f"Created: {result['created']}.",
        "",
        "| Metric | Value |",
        "|---|---|",
    ]
    for key, value in scalar_rows(result["metrics"]):
        lines.append(f"| `{key}` | {value} |")
    flags = acceptance_flags(result["metrics"])
    if flags:
        lines += ["", "Acceptance checks computed by the notebook:", ""]
        for name, flag in flags.items():
            lines.append(f"* `{name}`: {'passed' if flag else '**not met**'}")
    lines += ["", "Limitations recorded with the results:", ""]
    for item in result["limitations"]:
        lines.append(f"* {item}")
    return "\n".join(lines)


def main():
    for spec in build_modules.all_specs():
        result_path = ROOT / "experiments" / "results" / f"{spec['module']}.json"
        readme = nbgen.module_dir(spec) / "README.md"
        if not result_path.exists() or not readme.exists():
            print("skipped", spec["module"])
            continue
        result = json.loads(result_path.read_text())
        text = readme.read_text()
        start = text.index(nbgen.RESULTS_START) + len(nbgen.RESULTS_START)
        end = text.index(nbgen.RESULTS_END)
        readme.write_text(text[:start] + "\n" + block_text(result) + "\n" + text[end:])
        print("rendered", spec["module"])


if __name__ == "__main__":
    main()
