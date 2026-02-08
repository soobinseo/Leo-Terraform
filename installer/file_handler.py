from . import REPO_ROOT, BACKUP_DIR
from pathlib import Path
from typing import Dict, List, Literal
import errno
import shutil

IMMUTABLE_ERRNOS = {errno.EBUSY, errno.EPERM, errno.EACCES, errno.EROFS}


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


def _alternate_install_path(path: Path) -> Path:
    suffix = ".opencode"
    candidate = path.with_name(f"{path.name}{suffix}")
    if not candidate.exists():
        return candidate

    index = 1
    while True:
        candidate = path.with_name(f"{path.name}{suffix}.{index}")
        if not candidate.exists():
            return candidate
        index += 1


def _is_errno(exc: Exception, codes) -> bool:
    return isinstance(exc, OSError) and exc.errno in codes


def _install_instruction(path: Path) -> str:
    name = path.name.lower()
    if name == ".zshrc" or name.startswith(".zshrc."):
        return f"To use it: source {path}"
    return f"To use it: manually merge from {path}"


def _backup_and_copy_src_to_dst(src: str, dst: str, method: Literal["copy", "link"]):
    resolved_src = _resolve_source_path(src)
    resolved_dst = _resolve_target_path(dst)

    assert resolved_src.exists(), f"Source path does not exist: {resolved_src}"

    backup_succeeded = True
    try:
        if resolved_dst.exists():
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            backup_path = BACKUP_DIR / resolved_dst.name
            try:
                shutil.move(src=str(resolved_dst), dst=str(backup_path))
                print(f"Backup {resolved_dst} --> {backup_path}")
            except Exception as move_error:
                if _is_errno(move_error, {errno.EXDEV}):
                    try:
                        if resolved_dst.is_dir():
                            shutil.copytree(src=str(resolved_dst), dst=str(backup_path))
                        else:
                            shutil.copy2(src=str(resolved_dst), dst=str(backup_path))
                        print(f"Backup (copy) {resolved_dst} --> {backup_path}")
                    except Exception as copy_error:
                        backup_succeeded = False
                        print(f"Failed to backup existing path {resolved_dst}: {copy_error}")
                    else:
                        try:
                            if resolved_dst.is_dir():
                                shutil.rmtree(str(resolved_dst))
                            else:
                                resolved_dst.unlink()
                        except Exception as remove_error:
                            backup_succeeded = False
                            print(
                                f"Backup created but could not remove {resolved_dst}: {remove_error}"
                            )
                        else:
                            print(f"Removed original after backup {resolved_dst}")
                elif _is_errno(move_error, IMMUTABLE_ERRNOS):
                    print(
                        f"Skipping install for {resolved_dst}; destination not writable: {move_error}"
                    )
                    return
                else:
                    backup_succeeded = False
                    print(f"Failed to backup existing path {resolved_dst}: {move_error}")
    except Exception as e:
        backup_succeeded = False
        print(f"Failed to backup existing path {resolved_dst}: {e}")

    install_dst = resolved_dst
    if resolved_dst.exists() and not backup_succeeded:
        install_dst = _alternate_install_path(resolved_dst)
        install_dst.parent.mkdir(parents=True, exist_ok=True)
        print(f"Existing path left in place: {resolved_dst}")
        print(f"Installing to alternate path: {install_dst}")

    try:
        install_dst.parent.mkdir(parents=True, exist_ok=True)
        if method == "copy":
            if resolved_src.is_dir():
                shutil.copytree(src=str(resolved_src), dst=str(install_dst))
            else:
                shutil.copy2(src=str(resolved_src), dst=str(install_dst))
        elif method == "link":
            install_dst.symlink_to(resolved_src)
        else:
            raise ValueError(f"Unknown method: {method}")

        print(f"{method.title()} {resolved_src} --> {install_dst}")
        if install_dst != resolved_dst:
            print(_install_instruction(install_dst))
    except Exception as e:
        if install_dst == resolved_dst and _is_errno(e, IMMUTABLE_ERRNOS):
            print(
                f"Skipping install for {resolved_dst}; destination not writable: {e}"
            )
            return
        print(f"Failed to {method} {resolved_src} to {install_dst}: {e}")
