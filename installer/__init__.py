from pathlib import Path
from datetime import datetime


REPO_ROOT = Path(__file__).resolve(strict=False).parents[1]
CFG_PATH = Path(__file__).resolve(strict=False).parent / "config.json"

BACKUP_DIR = Path.home() / f".leo_terraform_backup/{datetime.now().strftime('%Y%m%d_%H%M%S')}"
