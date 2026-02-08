# Leo Terraform

Bootstrap terminal tooling and dotfiles (zsh + tmux + git + opencode).

## Requirements
- Python 3.6+
- zsh
- git
- curl

## Install

```bash
git clone git@github.com:Fitree/Leo-Terraform.git "$HOME/Leo-Terraform" && cd "$HOME/Leo-Terraform" && python3 -m installer
```

## What This Installer Installs

It installs/copies (or symlinks) configuration files into your home directory. By default (see `installer/config.json`):

Terminal env:
- `~/.zshrc`
- `~/.p10k.zsh`
- `~/.tmux.conf`
- `~/.gitconfig` (aliases only; it does not set `user.name`/`user.email`)

opencode:
- `~/.config/opencode/opencode.json`
- `~/.config/opencode/agent/`
- `~/.config/opencode/plugins/`

## How Installation Works

- It runs a sequence of stages defined in `installer/config.json`.
- If a destination path already exists and is writable, it is backed up to `~/.leo_terraform_backup/<timestamp>/` before being replaced.
- If a destination file exists but is not writable/movable (common with Docker bind-mounts), that file is skipped and left unchanged.
