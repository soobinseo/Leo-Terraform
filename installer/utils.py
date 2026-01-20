import json
from pathlib import Path
from typing import Dict, List
import subprocess
from pprint import pprint
from . import CFG_PATH


def load_config() -> Dict:
    cfg_path = Path(CFG_PATH)
    if not cfg_path.is_file():
        raise FileNotFoundError(f"Missing config at {cfg_path}")

    with cfg_path.open() as handle:
        cfg = json.load(handle)

    if not isinstance(cfg, dict):
        raise ValueError("Config must be a JSON object")

    return cfg


def check_requirements(requirements: List) -> None:
    satisfied = True
    for req in requirements:
        res = subprocess.run(
            f"which {req}",
            shell=True,
            capture_output=True,
            text=True,
            )
        if res.returncode != 0:
            print(f"❌ {req}")
            satisfied = False
        else:
            print(f"✅ {req}")
    if not satisfied:
        print("Please install the missing requirements and run the script again.")
