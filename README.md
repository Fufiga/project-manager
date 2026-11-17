# Project Manager

A small terminal tool to keep track of your projects and open any of them in one keystroke. Each project opens in its own **tmux** session: nvim on the left, a shell in the project folder on the right.

Pure Python (standard library only), nothing to `pip install`.

---

## How it works

- Projects (name, folder, languages) are stored in `data.json`.
- Opening a project creates a tmux session named after it, starting in the project folder. The left pane runs `nvim`, the right pane (30% width) is a plain shell. If the session already exists, it just reattaches.
- When you detach from tmux (`Ctrl+b` then `d`), you come back to the menu.
- The project you opened last is remembered, so it can be resumed from the menu.
- New projects get a folder in `~/Desktop/42`, a `README.md` and a git repository.

```
1. Resume last project
2. Load a project
3. New project
4. Import a project
5. Delete a project
6. Show projects
7. Quit
```

## Requirements

- Linux
- Python 3.9 or newer
- `tmux`
- `git`
- `nvim`

## Usage

```bash
mkdir -p ~/Desktop/Projects/project-manager
git clone git@github.com:Fufiga/gabsec-projectManager.git ~/Desktop/Projects/project-manager
cd ~/Desktop/Projects/project-manager
python3 main.py
```

## Launching it from `.zshrc`

Add one block at the end of `~/.zshrc` and adjust the path. All of them skip tmux panes (otherwise every pane would start the manager again) and use `cd` in a subshell so `data.json` is always found. Use `python3`, not `exec python3`, so quitting the manager gives you your normal prompt.

Any terminal:

```zsh
if [[ -o interactive && -z "$TMUX" ]]; then
    (cd ~/Desktop/Projects/project-manager && python3 main.py)
fi
```

For a specific terminal, replace the first condition with one of these:

| Terminal | Condition |
|---|---|
| WezTerm | `[[ "$TERM_PROGRAM" == "WezTerm" && -z "$TMUX" ]]` |
| kitty | `[[ -n "$KITTY_WINDOW_ID" && -z "$TMUX" ]]` |
| Alacritty | `[[ -n "$ALACRITTY_SOCKET" && -z "$TMUX" ]]` |
| GNOME Terminal | `[[ -n "$VTE_VERSION" && -z "$TMUX" ]]` |
| Konsole | `[[ -n "$KONSOLE_VERSION" && -z "$TMUX" ]]` |

Example for WezTerm:

```zsh
if [[ "$TERM_PROGRAM" == "WezTerm" && -z "$TMUX" ]]; then
    (cd ~/Desktop/Projects/project-manager && python3 main.py)
fi
```

Notes:

- Open a new terminal or run `source ~/.zshrc` after editing.
- Keep `==` outside the quotes, and write `TERM_PROGRAM` with one M.
- To find the variables your terminal sets: `env | grep -i -E "kitty|alacritty|wezterm|konsole|vte"`.

## Troubleshooting

- **tmux opens in `~`**: the folder doesn't exist, or you reattached to an old session. Run `tmux ls`, then `tmux kill-session -t <name>`.
- **Terminal looks broken after a crash**: type `reset`.
- **Several `data.json` files appear**: start the program from its own folder, as in the `.zshrc` examples.