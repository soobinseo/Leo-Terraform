import datetime
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple

CONFIG_PATH = Path(__file__).resolve().parent / "install_config.json"
CLONE_ROOT = Path(__file__).resolve().parent


def load_install_config(path: Path) -> Tuple[List[Dict[str, Path]], Path]:
    if not path.is_file():
        raise FileNotFoundError(f"Missing config at {path}")

    with path.open() as handle:
        payload = json.load(handle)

    if not isinstance(payload, dict):
        raise ValueError("Config must be a JSON object")

    target_root = payload.get("target_root")
    if not isinstance(target_root, str) or not target_root.strip():
        raise ValueError("Config must specify a non-empty 'target_root'")

    links = payload.get("links")
    if not isinstance(links, list):
        raise ValueError("Config must contain a 'links' array")

    target_root_path = Path(target_root).expanduser().resolve(strict=False)

    seen_targets: Set[Path] = set()
    validated_links: List[Dict[str, Path]] = []
    for index, link in enumerate(links, start=1):
        if not isinstance(link, dict):
            raise ValueError(f"Link at index {index} must be an object")

        source = link.get("source")
        target = link.get("target")
        if not isinstance(source, str) or not source.strip():
            raise ValueError(f"Link at index {index} requires a non-empty 'source'")
        if not isinstance(target, str) or not target.strip():
            raise ValueError(f"Link at index {index} requires a non-empty 'target'")

        source_str = source.strip()
        target_str = target.strip()
        source_path = Path(source_str)
        if source_path.is_absolute():
            raise ValueError(f"Source must be relative: '{source_path}'")
        if any(part == ".." for part in source_path.parts):
            raise ValueError(f"Source must not traverse upward: '{source_path}'")

        source_abs = (CLONE_ROOT / source_path).resolve(strict=False)

        target_path = Path(target_str)
        if target_path.is_absolute():
            raise ValueError(f"Target must be relative: '{target_path}'")
        if any(part == ".." for part in target_path.parts):
            raise ValueError(f"Target must not traverse upward: '{target_path}'")

        target_abs = (target_root_path / target_path).resolve(strict=False)
        try:
            target_abs.relative_to(target_root_path)
        except ValueError:
            raise ValueError(f"Target '{target_abs}' falls outside target_root '{target_root_path}'")

        if target_abs in seen_targets:
            raise ValueError(f"Duplicate target detected: '{target_abs}'")

        seen_targets.add(target_abs)

        validated_links.append({"source": source_abs, "target": target_abs})

    print(f"Loaded {len(validated_links)} links from {CONFIG_PATH}")
    return validated_links, target_root_path


def mark_existing_targets(entries: List[Dict[str, Path]]) -> None:
    for entry in entries:
        target = entry["target"]
        entry["target_exist"] = target.exists() or target.is_symlink()

    existing = sum(1 for entry in entries if entry.get("target_exist"))
    print(f"Found {existing} existing target{'s' if existing != 1 else ''}")


def backup_existing(entries: List[Dict[str, Path]], target_root: Path) -> None:
    to_backup = [entry for entry in entries if entry.get("target_exist")]
    if not to_backup:
        print("No existing targets to back up")
        return

    symlinks: List[Path] = []
    non_symlinks: List[Dict[str, Path]] = []
    for entry in to_backup:
        target = entry["target"]
        if target.is_symlink():
            symlinks.append(target)
        else:
            non_symlinks.append(entry)

    for target in symlinks:
        print(f"Unlinking symlink {target}")
        target.unlink()

    if not non_symlinks:
        print("Skipping backup directory because only symlink targets existed")
        return

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_root = target_root / "backup" / stamp
    if backup_root.exists():
        raise FileExistsError(f"Backup directory already exists: {backup_root}")
    backup_root.mkdir(parents=True)
    print(f"Backing up existing targets into {backup_root}")

    non_symlinks.sort(key=lambda entry: len(entry["target"].parts), reverse=True)
    for entry in non_symlinks:
        target = entry["target"]
        relative = target.relative_to(target_root)
        dest = backup_root / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        print(f"Backing up {target} -> {dest}")
        shutil.move(str(target), str(dest))


def create_symlinks(entries: List[Dict[str, Path]]) -> None:
    for entry in entries:
        source = entry["source"]
        if not source.exists():
            raise FileNotFoundError(f"Missing repository source: {source}")
        target = entry["target"]
        target.parent.mkdir(parents=True, exist_ok=True)
        print(f"Linking {source} -> {target}")
        target.symlink_to(source)


def main() -> None:
    print("Starting OpenCode installer")
    print(f"Using config {CONFIG_PATH}")
    entries, target_root = load_install_config(CONFIG_PATH)
    target_root.mkdir(parents=True, exist_ok=True)

    mark_existing_targets(entries)
    backup_existing(entries, target_root)
    create_symlinks(entries)
    print("Installation complete.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"Error: {error}")
        sys.exit(1)
