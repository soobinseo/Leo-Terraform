from . import CFG_PATH, REPO_ROOT
from pathlib import Path
from .utils import load_config, check_requirements
from .installers import (
    try_install_oh_my_zsh,
    try_install_p10k,
    try_install_zsh_autosuggestions,
    try_install_zsh_syntax_highlighting,
    try_install_opencode,
)
from .file_handler import copy_files, link_files


STAGES = {
    "check_requirements": check_requirements,
    "try_install_oh_my_zsh": try_install_oh_my_zsh,
    "try_install_p10k": try_install_p10k,
    "try_install_zsh_autosuggestions": try_install_zsh_autosuggestions,
    "try_install_zsh_syntax_highlighting": try_install_zsh_syntax_highlighting,
    "try_install_opencode": try_install_opencode,
    "copy_files": copy_files,
    "link_files": link_files,
}


if __name__ == "__main__":
    cfg = load_config()

    for stage in cfg["stages"]:
        stage_name = stage.pop("name")
        stage_fn = STAGES.get(stage_name)
        print("=" * 10, stage_name.center(20), "=" * 30)

        stage_fn(**stage)

        print()