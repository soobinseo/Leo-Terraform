from . import REPO_ROOT, BACKUP_DIR
from pathlib import Path
from typing import Dict, List, Literal
import shutil


def copy_files(path_mappings: List[Dict]):
    for mapping in path_mappings:
        _backup_and_copy_src_to_dst(
            src=mapping["src"],
            dst=mapping["dst"],
            method="copy",
        )

def link_files(path_mappings: List[Dict]):
    for mapping in path_mappings:
        _backup_and_copy_src_to_dst(
            src=mapping["src"],
            dst=mapping["dst"],
            method="link",
        )


def _resolve_source_path(path: str) -> Path:
    return (REPO_ROOT / path.strip()).absolute()


def _resolve_target_path(path: str) -> Path:
    return Path(path.strip()).expanduser().absolute()


def _backup_and_copy_src_to_dst(src: str, dst: str, method: Literal["copy", "link"]):
    resolved_src = _resolve_source_path(src)
    resolved_dst = _resolve_target_path(dst)

    assert resolved_src.exists(), f"Source path does not exist: {resolved_src}"

    try:
        if resolved_dst.exists():
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            backup_path = BACKUP_DIR / resolved_dst.name
            shutil.move(src=str(resolved_dst), dst=str(backup_path))
            print(f"✅ Backup {resolved_dst} --> {backup_path}")
    except Exception as e:
        print(f"❌ Failed to backup existing path {resolved_dst}: {e}")

    try:
        resolved_dst.parent.mkdir(parents=True, exist_ok=True)
        if method == "copy":
            if resolved_src.is_dir():
                shutil.copytree(src=str(resolved_src), dst=str(resolved_dst))
            else:
                shutil.copy2(src=str(resolved_src), dst=str(resolved_dst))
        elif method == "link":
            resolved_dst.symlink_to(resolved_src)
        else:
            raise ValueError(f"Unknown method: {method}")

        print(f"✅ {method.title()} {resolved_src} --> {resolved_dst}")
    except Exception as e:
        print(f"❌ Failed to {method} {resolved_src} to {resolved_dst}: {e}")
