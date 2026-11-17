from time import sleep
from json_management import *
import os
import subprocess
from pathlib import Path
import sys
import termios
import tty
import shutil
import random


GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN   = "\033[36m"
BLUE   = "\033[34m"
RED    = "\033[31m"
GOLD = "\033[38;5;220m"
ORANGE = "\033[38;5;208m"
RESET = "\033[0m"


def show_banner():
    print(GOLD, "██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████████╗     ")
    print("██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔════╝╚══██╔══╝           ")
    print("██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║        ██║              ")
    print("██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║        ██║              ")
    print("██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╗   ██║              ")
    print("╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝   ╚═╝              ")
    print("███╗   ███╗ █████╗ ███╗   ██╗ █████╗  ██████╗ ███████╗██████╗        ")
    print("████╗ ████║██╔══██╗████╗  ██║██╔══██╗██╔════╝ ██╔════╝██╔══██╗       ")
    print("██╔████╔██║███████║██╔██╗ ██║███████║██║  ███╗█████╗  ██████╔╝       ")
    print("██║╚██╔╝██║██╔══██║██║╚██╗██║██╔══██║██║   ██║██╔══╝  ██╔══██╗       ")
    print("██║ ╚═╝ ██║██║  ██║██║ ╚████║██║  ██║╚██████╔╝███████╗██║  ██║       ")
    print("╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═╝", RESET)


def git_init(path):
    path = Path(path).expanduser()
    subprocess.run(["git", "init", "-b", "main"], cwd=path, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def clean_screen():
    subprocess.run(["clear"])


def wait_for_key(key=" ", message="Press space to continue..."):
    print(message, end="", flush=True)

    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)    # save the terminal state
    try:
        tty.setraw(fd)                      # read keys without waiting for Enter
        while True:
            ch = sys.stdin.read(1)
            if ch == key:
                break
            if ch == "\x03":                # Ctrl+C is not caught in raw mode
                raise KeyboardInterrupt
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)   # always restore
    print()


def remove_project(name):
    if name.isdigit():
        p = retrieve_projectId(name)
    else:
        p = retrieve_projectName(name)
    if p is None:
        print(f"Project '{name}' not found. ")
        return

    # Typing the name is harder to do by accident than Y/n
    confirm = input(f"Type '{p.name}' to confirm deletion (anything else to cancel): ")
    if confirm != p.name:
        clean_screen()
        show_banner()
        print("Cancelled.")
        wait_for_key()
        return

    also_folder = input("Also delete the folder and its files? (Y/n) ").lower() == "y"

    # Stop its tmux session first (silent if it doesn't exist)
    subprocess.run(["tmux", "kill-session", "-t", f"={p.name}"], capture_output=True)

    if also_folder:
        folder = Path(p.path).expanduser().resolve()
        base = Path("~/Desktop/42").expanduser().resolve()
        if folder.is_dir() and folder.is_relative_to(base) and folder != base:
            shutil.rmtree(folder)
        else:
            print("Folder is outside ~/Desktop/42, not deleting it.")

    delete_project(p.name)
    print("Project deleted.")


def tmux(*args):
    """Run a tmux command and return its output as a string."""
    result = subprocess.run(
        ["tmux", *args],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def open_in_tmux(session, path):
    path = Path(path).expanduser()

    sleep(1)
    if not path.is_dir():
        print(f"Directory does not exist: {path}")
        return

    path = str(path)
    
    exists = subprocess.run(
        ["tmux", "has-session", "-t", session],
        capture_output=True,
    ).returncode == 0

    if exists:
        print(f"Session '{session}' already exists, reattaching (setup skipped).")

    if not exists:
        # Create the session and get the ID of its first pane (e.g. "%5")
        editor_pane = tmux(
            "new-session", "-d", "-s", session, "-c", path,
            "-P", "-F", "#{pane_id}",
        )

        # Split that pane; the new pane is the shell on the right
        tmux("split-window", "-h", "-l", "30%", "-t", editor_pane, "-c", path)

        # nvim only in the editor pane
        tmux("send-keys", "-t", editor_pane, "nvim", "Enter")

        # Focus back on the editor pane
        tmux("select-pane", "-t", editor_pane)

    if os.environ.get("TMUX"):
        tmux("switch-client", "-t", session)
    else:
        subprocess.run(["tmux", "attach-session", "-t", session])


def create_project(name: str, languages: dict):
    base = "~/Desktop/Projects"
    path = Path(base).expanduser() / name
    path.mkdir(parents=True, exist_ok=True)
    file = path / "README.md"
    file.touch()

    git_init(path)
    project = Project(0, name, str(path), languages, False)
    return put_intoJson(project)


def import_project():
    print()
    rawPath = input("What is the path of the project ? (empty to cancel) ")

    while True:
        if rawPath.strip() == "":
            return None

        path = Path(rawPath.strip()).expanduser()

        try:
            is_dir = path.is_dir()
        except OSError:
            rawPath = input("Unable to open that path. Please try with another path: ")
            continue

        if not is_dir:
            if path.exists():
                rawPath = input("That's a file, not a folder. Please input the project folder's path: ")
            else:
                rawPath = input("That folder doesn't exist. Please input the project folder's path: ")
            continue

        path = path.resolve()

        if not os.access(path, os.R_OK | os.X_OK):
            rawPath = input("You don't have access rights to this folder. Try again: ")
            continue

        if path in registered_paths():
            rawPath = input("This folder is already registered. Try again: ")
            continue

        break

    name = input(f"Project name [{path.name}]: ").strip() or path.name
    while exists(name):
        name = input(f"Project '{name}' already exists. Please give it another name: ").strip()
        if name == "":
            return None

    p = Project(0, name, str(path), [], False)
    return put_intoJson(p)


def open_project(name):
    p = retrieve_projectName(name)
    if p is None:
        print(f"Project '{name}' not found.")
        return
    switch_last(p.name)
    open_in_tmux(p.name, p.path)


def show_options():
    print("")
    print(f"{GOLD}What do you want to do ?{RESET}")
    print("   1. Resume last project.")
    print("   2. Load a project.")
    print("   3. New project.")
    print("   4. Import a project.")
    print("   5. Delete a project.")
    print("   6. Show projects.")
    print("   7. Quit.")
    print("")


def main():
    while True:
        clean_screen()
        show_banner()
        show_options()

        choice = input("Your choice: ")
        
        # Open the last opened project.
        if choice == "1":
            proj = retrieve_last()
            if proj is None:
                clean_screen()
                show_banner()
                print()
                print("No project were last opened. Please load one.")
                wait_for_key()
            else:
                open_project(proj.name)
        
        # Load a project
        elif choice == "2":
            clean_screen()
            show_banner()
            if is_empty():
                print()
                print("You do not have projects available, please create or import one.")
                wait_for_key()
            else:
                print()
                show = input("Do you want to show the projects you can load ? (Y/n) ")
                if (show.lower() == "y"):
                    show_infos()
                while True:
                    to_load = input("Which one do you want to load ? ")
                    if to_load.isdigit() and exists_id(int(to_load)):
                        project = retrieve_projectId(int(to_load))
                        switch_last(project.name)
                        open_project(project.name)
                        break
                    elif not to_load.isdigit() and exists(to_load):
                        project = retrieve_projectName(to_load)
                        switch_last(project.name)
                        open_project(project.name)
                        break
                    elif to_load == "s":
                        show_infos()
                    else:
                        print("No projects has this id or name. Please try again. (press s to show the projects list)")
                        sleep(1)
        
        # Create a new project
        elif choice == "3":
            name = input("What should we name this project ? (leave empty to cancel)")
            cancel = 0;
            while exists(name) or name == "":
                print("")
                if exists(name):
                    name = input("Project " + name + " already exists. Please give it another name : ")
                else:
                    cancel = 1;
                    break
            if cancel == 0:
                languages = []
                #lang = input("What languages will the project use ? (can set multiple ones, leave empty to finish) ")
                #while (lang != ""):
                    #languages.append(lang.capitalize())
                    #lang = input("What languages will the project use ? (can set multiple ones, leave empty to finish) ")
                create_project(name, languages)
                questionOpen = input("Project created. Should we open it ? (Y/n) ")
                if (questionOpen.lower() == "y"):
                    open_project(name)
                    switch_last(name)
                if (questionOpen.lower() == "n"):
                    show_options()
        
        # Import an existing project
        elif choice == "4":
            clean_screen()
            show_banner()
            if import_project():
                print("Project imported.")
            else:
                print("Import cancelled or failed.")
            sleep(2)

        # Delete an existing project
        elif choice == "5":
            clean_screen()
            show_banner()
            empt = 0
            if is_empty():
                print()
                print("You have no projects.")
                wait_for_key()
                empt = 1
            while True and not empt:
                print()
                show = input("Do you want to show the projects list ? (Y/n) ")
                if show.lower() == "y":
                    print()
                    show_infos()
                    break
                elif show.lower() == "n":
                    break
                else:
                    print()
                    print("Please put a valid input, either y or n (yes or no).")
            if not empt:
                name = input("What project do you want to remove (leave empty to cancel) ? ")
                remove_project(name)

        # Show projects
        elif choice == "6":
            clean_screen()
            show_banner()
            print("")
            show_infos()
            wait_for_key()

        # Quit
        elif choice == "7":
            clean_screen()
            show_banner()
            print()
            print("Goodbye.")
            break
        
        elif choice == "":
            continue

        # When anything else is written
        else:
            clean_screen()
            show_banner()
            print()
            print("Please use a correct option. Just type the digit.")
            wait_for_key()


if __name__ == "__main__":
    main()
