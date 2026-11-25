"""Build every module from tools/specs. Run: python tools/build_modules.py [module ...]"""

import importlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import nbgen  # noqa: E402

MODULES = [
    "duration_and_convexity",
    "probability_of_default",
    "credit_scoring",
    "expected_credit_loss",
    "historical_var",
    "parametric_var",
    "expected_shortfall",
    "backtesting",
]


def load_spec(name):
    return importlib.import_module(f"specs.{name}").SPEC


def all_specs():
    found = []
    for name in MODULES:
        if (Path(__file__).parent / "specs" / f"{name}.py").exists():
            found.append(load_spec(name))
    return found


def main(selected):
    names = selected or [m for m in MODULES if (Path(__file__).parent / "specs" / f"{m}.py").exists()]
    for name in names:
        spec = load_spec(name)
        nbgen.write_module(spec)
        print("built", spec["path"])


if __name__ == "__main__":
    main(sys.argv[1:])
