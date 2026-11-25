"""Save experiment results and figures in a fixed, machine readable layout."""

import json
import platform
from datetime import datetime, timezone
from importlib import metadata
from pathlib import Path

REQUIRED_KEYS = [
    "module",
    "methodology",
    "data_kind",
    "dataset",
    "n_obs",
    "seed",
    "parameters",
    "assumptions",
    "metrics",
    "baseline",
    "limitations",
    "created",
    "environment",
]
DATA_KINDS = ["synthetic", "illustrative", "empirical"]
PACKAGES = ["numpy", "pandas", "scipy", "scikit-learn", "statsmodels", "matplotlib"]


def find_root(start=None):
    """Walk upward until pyproject.toml is found."""
    folder = Path(start or Path.cwd()).resolve()
    for candidate in [folder, *folder.parents]:
        if (candidate / "pyproject.toml").exists():
            return candidate
    raise FileNotFoundError("repository root not found")


def environment():
    """Python and package versions for the results file."""
    versions = {}
    for name in PACKAGES:
        try:
            versions[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            versions[name] = "missing"
    return {"python": platform.python_version(), "platform": platform.system(), "packages": versions}


def _clean(value):
    """Make numpy values JSON friendly."""
    if isinstance(value, dict):
        return {str(key): _clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(item) for item in value]
    if hasattr(value, "tolist"):
        return _clean(value.tolist())
    if isinstance(value, float) and value != value:
        return None
    return value


def save_result(module, **fields):
    """Write experiments/results/<module>.json and return the path."""
    missing = [key for key in REQUIRED_KEYS if key not in fields and key not in {"module", "created", "environment"}]
    if missing:
        raise ValueError(f"missing result fields: {missing}")
    if fields["data_kind"] not in DATA_KINDS:
        raise ValueError(f"data_kind must be one of {DATA_KINDS}")
    payload = {"module": module}
    payload.update(fields)
    payload["created"] = datetime.now(timezone.utc).isoformat(timespec="seconds")
    payload["environment"] = environment()
    folder = find_root() / "experiments" / "results"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{module}.json"
    path.write_text(json.dumps(_clean(payload), indent=2) + "\n")
    return path


def figure_path(module, name):
    """Path for a figure, creating the folder when needed."""
    folder = find_root() / "experiments" / "figures" / module
    folder.mkdir(parents=True, exist_ok=True)
    return folder / name


def save_config(module, config):
    """Write experiments/configurations/<module>.yaml."""
    import yaml

    folder = find_root() / "experiments" / "configurations"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{module}.yaml"
    path.write_text(yaml.safe_dump(_clean(config), sort_keys=False))
    return path
