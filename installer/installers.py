import subprocess
from pathlib import Path


def try_install_oh_my_zsh():
    if (Path.home() / ".oh-my-zsh").exists():
        print("✅️ Oh My Zsh is already installed, skipping installation.")
        return

    res = subprocess.run(
        f"yes | sh -c \"$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)\"",
        shell=True,
    )

    if res.returncode == 0:
        print("✅ Oh My Zsh installation script executed successfully.")
    else:
        print("❌ Oh My Zsh installation script failed to execute.")
        print(res.stderr)
        raise RuntimeError("Oh My Zsh installation failed.")


def try_install_p10k():
    if (Path.home() / ".oh-my-zsh/custom/themes/powerlevel10k").exists():
        print("✅️ Powerlevel10k is already installed, skipping installation.")
        return

    res = subprocess.run(
        "git clone --depth=1 https://github.com/romkatv/powerlevel10k.git ${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}/themes/powerlevel10k",
        shell=True,
    )

    if res.returncode == 0:
        print("✅ Powerlevel10k installation script executed successfully.")
    else:
        print("❌ Powerlevel10k installation script failed to execute.")
        print(res.stderr)
        raise RuntimeError("Powerlevel10k installation failed.")


def try_install_zsh_autosuggestions():
    if (Path.home() / ".oh-my-zsh/custom/plugins/zsh-autosuggestions").exists():
        print("✅️ Zsh Autosuggestions is already installed, skipping installation.")
        return

    res = subprocess.run(
        "git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions",
        shell=True,
    )

    if res.returncode == 0:
        print("✅ Zsh Autosuggestions installation script executed successfully.")
    else:
        print("❌ Zsh Autosuggestions installation script failed to execute.")
        print(res.stderr)
        raise RuntimeError("Zsh Autosuggestions installation failed.")

def try_install_zsh_syntax_highlighting():
    if (Path.home() / ".oh-my-zsh/custom/plugins/zsh-syntax-highlighting").exists():
        print("✅️ Zsh Syntax Highlighting is already installed, skipping installation.")
        return

    res = subprocess.run(
        "git clone https://github.com/zsh-users/zsh-syntax-highlighting.git ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-syntax-highlighting",
        shell=True,
    )

    if res.returncode == 0:
        print("✅ Zsh Syntax Highlighting installation script executed successfully.")
    else:
        print("❌ Zsh Syntax Highlighting installation script failed to execute.")
        print(res.stderr)
        raise RuntimeError("Zsh Syntax Highlighting installation failed.")


def try_install_opencode():
    res = subprocess.run(
        "curl -fsSL https://opencode.ai/install | bash",
        shell=True,
        capture_output=True,
        text=True,
    )

    if res.returncode == 0:
        print("✅ Opencode installation script executed successfully.")
    else:
        print("❌ Opencode installation script failed to execute.")
        print(res.stderr)
        raise RuntimeError("Opencode installation failed.")
