from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn

class ProgressManager:
    def __init__(self, with_pct: bool = False) -> None:
        # Configure the progress bar layout
        if with_pct:
            self.progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                "[progress.percentage]{task.percentage:>3.0f}%",
                TimeElapsedColumn(),
            )
        else:
            self.progress = Progress(
                TextColumn("[bold blue]{task.description}"),
                BarColumn(),
                TimeElapsedColumn(),
            )
        self.task_id = None

    def start(self, description: str, total: int = None) -> None:
        """Start the progress display and add a task."""
        self.progress.start()
        self.task_id = self.progress.add_task(description, total=total)

    def remove_task(self) -> None:
        """Remove a task from the progress display."""
        self.progress.remove_task(self.task_id)

    def advance(self, step: int = 1) -> None:
        """Advance the progress by a given step."""
        self.progress.update(self.task_id, advance=step)

    def stop(self) -> None:
        """Stop the progress display."""
        self.progress.stop()

    def end(self) -> None:
        """Stop the progress display and clear all tasks."""
        self.remove_task()
        self.progress.stop()
        self.progress = None
        self.task_id = None

