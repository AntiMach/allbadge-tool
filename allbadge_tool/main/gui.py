import tkinter as tk
from tkinter import ttk
from pathlib import Path

from allbadge_tool.main.program import Program
from allbadge_tool.misc.tkextra import CheckboxButtons, FileSelect, ScrolledTextLog
from allbadge_tool.misc.const import BASE_DIR, VERSIONS_130, VERSIONS_131, VERSIONS_PC, Version


class VersionFrame(ttk.Frame):
    def __init__(self, master):
        self.label = ttk.Label(master, text="Select versions", anchor="center")
        self.selection_130 = CheckboxButtons(master, options=VERSIONS_130)
        self.selection_131 = CheckboxButtons(master, options=VERSIONS_131)
        self.selection_pc = CheckboxButtons(master, options=VERSIONS_PC)

    def grid(self, row: int, column: int, **kwargs) -> int:
        self.label.grid(row=row, column=column, rowspan=3, **kwargs)
        self.selection_130.grid(row=row, column=column + 1, **kwargs)
        self.selection_131.grid(row=row + 1, column=column + 1, **kwargs)
        self.selection_pc.grid(row=row + 2, column=column + 1, **kwargs)
        return row + 3

    def disable(self):
        self.selection_130.disable()
        self.selection_131.disable()
        self.selection_pc.disable()

    def enable(self):
        self.selection_130.enable()
        self.selection_131.enable()
        self.selection_pc.enable()

    @property
    def versions(self) -> list[Version]:
        return [
            *self.selection_130.value(),
            *self.selection_131.value(),
            *self.selection_pc.value(),
        ]


class ProgramGUI(tk.Tk, Program):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title("Allbadge Tool")
        self.geometry("500x400")
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_text = tk.StringVar(self, "")

        self.version_frame = VersionFrame(self)

        self.boot9_selection = FileSelect(self, title="Select boot9 file", is_dir=False, default=BASE_DIR / "boot9.bin")
        self.data_selection = FileSelect(self, title="Select data folder", is_dir=True, default=BASE_DIR / "data")

        self.begin_button = ttk.Button(self, text="Begin", command=self.begin)
        self.prog_bar = ttk.Progressbar(self, variable=self.progress_var, maximum=1.0)
        self.prog_label = ttk.Label(self, textvariable=self.progress_text, anchor="center")
        self.message_log = ScrolledTextLog(self)

        self.add_rows(
            (self.version_frame, 1),
            (self.boot9_selection, 1),
            (self.data_selection, 1),
            (self.begin_button, 2),
            (self.prog_bar, 2),
            (self.prog_label, 2),
            (self.message_log, 2),
        )

    def add_rows(self, *widgets: tuple[tk.Widget, int]):
        next_row = 0
        for widget, span in widgets[:-1]:
            res = widget.grid(row=next_row, column=0, padx=5, pady=(5, 0), sticky="ew", columnspan=span)
            next_row = res or (next_row + 1)

        widget, span = widgets[-1]
        res = widget.grid(row=next_row, column=0, padx=5, pady=5, sticky="nsew", columnspan=span)

        self.rowconfigure(next_row, weight=1)

    @property
    def versions(self) -> list[Version]:
        return self.version_frame.versions

    @property
    def boot9_path(self) -> Path:
        return Path(self.boot9_selection.var.get())

    @property
    def data_path(self) -> Path:
        return Path(self.data_selection.var.get())

    def set_progress(self, text: str, ratio: float):
        self.progress_var.set(ratio)
        self.progress_text.set(f"{text} [{ratio * 100:.2f}%]")
        self.update()

    def set_error(self, error: str):
        self.progress_var.set(0)
        self.progress_text.set(error)
        self.update()

    def log_message(self, message: str):
        self.message_log.log_message(message)

    def start(self):
        self.version_frame.disable()
        self.boot9_selection.disable()
        self.data_selection.disable()
        self.begin_button.config(state=tk.DISABLED)

    def end(self):
        self.version_frame.enable()
        self.boot9_selection.enable()
        self.data_selection.enable()
        self.begin_button.config(state=tk.NORMAL)
