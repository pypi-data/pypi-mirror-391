from typing import Literal

from textual.widgets import ProgressBar, Static


class Notification(Static):
    def __init__(self, message: str, duration: int = 3, variant: Literal["success", "info", "warning", "error"] = "success"):
        super().__init__()

        if variant == "success":
            self.add_class("success-notification")
        elif variant == "error":
            self.add_class("error-notification")

        self.message = message
        self.duration = duration

    def compose(self):
        progress_bar = ProgressBar(total=self.progress_duration(), show_percentage=False, show_eta=False)
        progress_bar.update(progress=self.progress_duration())
        yield Static(self.message)
        yield progress_bar

    def on_mount(self) -> None:
        self.set_timer(self.progress_duration(), lambda: self.add_class("fade-out"))
        self.set_timer(self.duration, lambda: self.remove())
        self.set_interval(0.01, self.make_progress)

    def make_progress(self) -> None:
        self.query_one(ProgressBar).advance(-0.01)

    def progress_duration(self) -> float:
        return self.duration - 0.5
