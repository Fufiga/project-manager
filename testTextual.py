from os import system

from main import *
from textual.app import App, ComposeResult
from textual import events, on
from textual.widgets import Label, Button

class ProjectManager(App[str]):
    CSS_PATH = "style.tcss"

    def compose(self) -> ComposeResult:
        yield Label("=== GABSEC ===", id="centered")
        #yield Label("What do you want to do ?")
        yield Button("Stay", id="stay", variant="primary")
        yield Button("Leave", id="leave", variant="error")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "leave":
            self.exit(event.button.id)

    #Interesting because I can open, for example, tmux and give
    #@on(Button.Pressed, "#stay")
    #def run_external_editor(self) -> None:
    #    with self.suspend():
    #        open_in_tmux("gnl", "~/Desktop/42/get_next_line")


if __name__ == "__main__":
    app = ProjectManager()
    app.run()