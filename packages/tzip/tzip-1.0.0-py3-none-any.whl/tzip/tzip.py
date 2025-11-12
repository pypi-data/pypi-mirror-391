from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import List, Optional, Sequence

from textual import events, work
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from textual.screen import ModalScreen
from textual.widgets import (Button, DataTable, DirectoryTree, Footer, Header,
                             Input, Label, Static)

from tzip.archiver import ArchiveEntry, create_archiver_for


class DestinationModal(ModalScreen[Optional[str]]):
    def __init__(self, default_path: Path):
        super().__init__()
        self._default_path = default_path

    """A simple modal that collects a destination path from the user."""

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog"):
            yield Label("Enter destination directory (leave empty for default):")
            yield Input(value=str(self._default_path), id="dest_input")
            with Horizontal(id="dialog_buttons"):
                yield Button("OK", id="ok", variant="primary")
                yield Button("Cancel", id="cancel")

    def on_mount(self) -> None:
        input_widget = self.query_one("#dest_input", Input)
        input_widget.focus()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        self.dismiss(event.value)

    def on_key(self, event: events.Key) -> None:
        if event.key == "escape":
            self.dismiss(None)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        input_widget: Input = self.query_one("#dest_input", Input)
        if event.button.id == "ok":
            self.dismiss(input_widget.value)
        else:
            self.dismiss(None)


class ArchiveExplorerApp(App):
    """A Textual application to explore and extract archive contents."""

    CSS_PATH = "tzip.tcss"

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("e", "extract_selected", "Extract selected entries"),
        ("E", "extract_all", "Extract entire archive"),
    ]

    current_archive: reactive[Optional[Path]] = reactive(None)
    archive_entries: reactive[List[ArchiveEntry]] = reactive([])

    def compose(self) -> ComposeResult:
        """Compose the layout of the application."""
        yield Header(show_clock=True)
        # Toolbar
        toolbar = Static(id="toolbar")
        toolbar.update(
            "Navigate the left tree to select an archive. Use the table on the right to select files.\n"
            "Press 'e' to extract selected rows or 'E' to extract the entire archive."
        )
        yield toolbar
        with Container(id="content"):
            # Directory tree to browse local filesystem
            yield DirectoryTree(os.getcwd(), id="tree")
            # DataTable to display contents of selected archive
            table = DataTable(id="table")
            table.add_column("Name", key="name", width=60)
            table.add_column("Size", key="size", width=12)
            table.add_column("Type", key="type", width=8)
            yield table
        # Status bar for messages
        yield Static("", id="status_bar")
        yield Footer()

    async def on_mount(self) -> None:
        """Called after the app is mounted; set up initial state."""
        # cache references to widgets found in the DOM.  Avoid assigning to
        # attributes such as ``tree`` which Textual may define internally
        # (``self.tree`` is a property on App used for DOM access).  Instead
        # use custom names like ``dir_tree``.
        self.table: DataTable = self.query_one(DataTable)
        self.dir_tree: DirectoryTree = self.query_one(DirectoryTree)

    async def load_archive(self, path: Path) -> None:
        """Load the contents of the given archive and populate the table."""
        self.current_archive = path
        entries: List[ArchiveEntry] = []
        ext = path.suffix.lower()

        archiver = create_archiver_for(path)
        if archiver:
            try:
                entries = archiver.get_file_list(path)
            except Exception as ex:
                entries = []
                # Display the error in the status bar
                self.set_status_text(f"Failed to read archive: {ex}")
        else:
            self.set_status_text(f"'{path.name}' is not an archive file.")
            self.table.clear()
            return

        # Sort entries by name for display
        entries.sort(key=lambda e: e.name)
        self.archive_entries = entries
        self.populate_table(entries)
        self.set_status_text(f"Loaded {len(entries)} entries from {path.name}")

    def populate_table(self, entries: Sequence[ArchiveEntry]) -> None:
        """Populate the data table with entries."""
        table = self.table
        table.clear()
        table.cursor_type = "row"
        for entry in entries:
            size_str = self.format_size(entry.size)
            entry_type = "Dir" if entry.is_dir else "File"
            table.add_row(entry.name, size_str, entry_type)

    def format_size(self, size: Optional[int]) -> str:
        """Format a byte count as a human-readable string."""
        if size is None:
            return ""
        power = 0
        units = ["B", "KB", "MB", "GB", "TB"]
        value = float(size)
        while value >= 1024 and power < len(units) - 1:
            value /= 1024
            power += 1
        return f"{value:.1f} {units[power]}"

    def set_status_text(self, text: str) -> None:
        """Update the status bar with a status message."""
        status: Static = self.query_one(
            "#status_bar")  # type: ignore[assignment]
        status.update(text)

    def get_selected_entries(self) -> List[ArchiveEntry]:
        """Return a list of entries currently selected in the table."""
        selected_indices = self.table.cursor_row
        # DataTable supports only a single selection at the moment; convert index to entry
        entries: List[ArchiveEntry] = []
        if isinstance(selected_indices, int) and 0 <= selected_indices < len(self.archive_entries):
            entries.append(self.archive_entries[selected_indices])
        return entries

    @work
    async def action_extract_selected(self) -> None:
        """Extract the currently selected entries from the archive."""
        if self.current_archive is None or not self.archive_entries:
            self.set_status_text("No archive loaded or nothing selected.")
            return
        selected = self.get_selected_entries()
        if not selected:
            self.set_status_text("Please select a row in the table.")
            return

        # Prompt the user for a destination
        dest = await self.prompt_destination()
        if not dest:
            self.set_status_text("Cancelled action.")
            return

        await self.extract_entries(self.current_archive, selected, dest)

    @work
    async def action_extract_all(self) -> None:
        """Extract all entries from the archive."""
        if self.current_archive is None or not self.archive_entries:
            self.set_status_text("No archive loaded to extract.")
            return

        # Prompt the user for a destination
        dest = await self.prompt_destination()
        if not dest:
            self.set_status_text("Cancelled action.")
            return

        await self.extract_entries(self.current_archive, None, dest)

    async def prompt_destination(self) -> Optional[Path]:
        """Prompt the user to enter a destination directory for extraction.

        Returns the destination as a Path object.  If the input is empty
        (user just presses enter), a default directory under the current
        working directory named after the archive (without extension) is
        used.
        """
        # Default directory: cwd/<archive_name_without_ext>
        default_name = self.current_archive.stem if self.current_archive else "output"
        dest_path = Path(os.getcwd()) / default_name

        # Display an Input widget in a modal to capture destination
        dest_str = await self.push_screen_wait(DestinationModal(dest_path),)
        if not dest_str:
            return None
        dest_path = Path(dest_str).expanduser()
        dest_path.mkdir(parents=True, exist_ok=True)
        return dest_path

    async def extract_entries(
        self, archive_path: Path, entries: Optional[Sequence[ArchiveEntry]], dest: Path
    ) -> None:
        """Extract the given entries (or all if None) to the destination."""

        archiver = create_archiver_for(archive_path)
        if not archiver:
            return

        def run_extraction() -> str:
            try:
                archiver.extract(archive_path, entries, dest)
                return "Extraction complete"
            except Exception as ex:
                return f"Extraction failed: {ex}"

        # Run the blocking extraction in a thread to avoid freezing UI
        result = await asyncio.to_thread(run_extraction)
        self.set_status_text(result)

    # ------------------------------------------------------------------
    # Event handlers for DirectoryTree
    #
    # type: ignore[override]
    async def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Called when the user activates a file node in the directory tree.

        Pressing Enter or double-clicking a file will trigger this event.
        If the selected file is a supported archive type, the archive
        contents are loaded into the table.  Otherwise the table is
        cleared.
        """
        path = Path(event.path)
        if path.is_file():
            await self.load_archive(path)
        else:
            self.table.clear()


def main():
    # Instantiate and run the app
    app = ArchiveExplorerApp()
    app.run()


if __name__ == "__main__":
    main()
