# Project Manager

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python&logoColor=white)
![Dependencies](https://img.shields.io/badge/Dependencies-Zero_(Stdlib_only)-brightgreen?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS-lightgrey?style=flat-square&logo=linux&logoColor=white)

A lightweight terminal tool to keep track of your projects and jump into any workspace in a single keystroke. Each project launches in its own dedicated **tmux** session: **Neovim** on the left, and a ready-to-use shell on the right.

Built with **pure Python** (standard library only) — zero `pip install` required.

> [!NOTE]
> **Status (`v0.1.0`):** Functional early release. Projects are currently stored in `~/Desktop/Projects/` by default (you can still import existing folders from anywhere on your system). Custom configuration file support is planned for upcoming releases.

---

## ✨ How It Works

* **Automatic Workspace Layout:** Opening a project creates a named `tmux` session rooted in the project directory, running `nvim` on the left pane (70%) and a plain shell on the right pane (30%). If the session already exists, it seamlessly reattaches.
* **Session Persistence:** Detaching from `tmux` (`Ctrl+b` then `d`) drops you right back into the manager menu.
* **Quick Resume:** Remembers your last active project so you can pick up where you left off immediately.
* **Instant Scaffolding:** Creating a new project automatically initializes a directory in `~/Desktop/Projects/`, a `README.md`, and a fresh `git` repository.
* **Local Metadata:** Project names, paths, and languages are stored cleanly in `data.json`.

### Menu Overview

```text
1. Resume last project
2. Load a project
3. New project
4. Import a project
5. Delete a project
6. Show projects
7. Quit
```

---

## 📋 Requirements

* **OS:** Linux or macOS
* **Runtime:** Python `3.9` or newer
* **Tools:** `tmux`, `git`, and `nvim` installed and available in your `$PATH`

### Installing Dependencies on macOS

If you are on macOS, you can install all required tools at once using [Homebrew](https://brew.sh/):

```bash
brew install python tmux neovim git
```

---

## 🚀 Quick Start

```bash
mkdir -p ~/Desktop/Projects/project-manager
git clone https://github.com/Fufiga/project-manager.git ~/Desktop/Projects/project-manager
cd ~/Desktop/Projects/project-manager
python3 main.py
```

---

## ⚡ Auto-Launch from `.zshrc`

You can trigger Project Manager automatically whenever you open a new terminal window. Add one of the blocks below to the end of your `~/.zshrc` (adjusting the path if needed).

> [!TIP]
> The `-z "$TMUX"` check ensures the manager doesn't recursively launch inside every new `tmux` pane, while the `(cd ...)` subshell guarantees `data.json` is always found. Use `python3` (not `exec python3`) so quitting the manager drops you back into your normal shell prompt.

### Option A: Any Terminal

```zsh
if [[ -o interactive && -z "$TMUX" ]]; then
    (python3 main.py)
fi
```

### Option B: Specific Terminal Emulator

Replace the `if` condition above with the one matching your terminal:

| Terminal | Platform | Condition |
| :--- | :--- | :--- |
| **WezTerm** | Linux / macOS | `[[ "$TERM_PROGRAM" == "WezTerm" && -z "$TMUX" ]]` |
| **Kitty** | Linux / macOS | `[[ -n "$KITTY_WINDOW_ID" && -z "$TMUX" ]]` |
| **Alacritty** | Linux / macOS | `[[ -n "$ALACRITTY_SOCKET" && -z "$TMUX" ]]` |
| **Apple Terminal** | macOS | `[[ "$TERM_PROGRAM" == "Apple_Terminal" && -z "$TMUX" ]]` |
| **iTerm2** | macOS | `[[ "$TERM_PROGRAM" == "iTerm.app" && -z "$TMUX" ]]` |
| **GNOME Terminal** | Linux | `[[ -n "$VTE_VERSION" && -z "$TMUX" ]]` |
| **Konsole** | Linux | `[[ -n "$KONSOLE_VERSION" && -z "$TMUX" ]]` |

**Example for WezTerm:**

```zsh
if [[ "$TERM_PROGRAM" == "WezTerm" && -z "$TMUX" ]]; then
    (python3 main.py)
fi
```

**Good to know:**
* Reload your config with `source ~/.zshrc` (or open a new terminal) after editing.
* Keep `==` outside the quotes, and spell `TERM_PROGRAM` with a single `M`.
* To inspect the environment variables set by your terminal, run: `env | grep -i -E "kitty|alacritty|wezterm|konsole|vte|term_program"`.

---

## 🛠️ Troubleshooting

| Symptom | Cause & Fix |
| :--- | :--- |
| **`tmux` opens in `~`** | The target folder doesn't exist, or you reattached to a stale session. List active sessions with `tmux ls` and remove the old one via `tmux kill-session -t <name>`. |
| **Garbled terminal after a crash** | Run `reset` in your terminal to restore normal display settings. |
| **Duplicate `data.json` files appear** | Always launch the script from its own directory (using the `(cd ...)` subshell pattern shown in the `.zshrc` setup). |

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
