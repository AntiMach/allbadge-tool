import asyncio
import tkinter as tk
from tkinter import ttk
from pathlib import Path
from zipfile import ZipFile
from abc import ABC, abstractmethod, abstractproperty

from allbadge_tool.ctr.boss import BOSS
from allbadge_tool.ctr.sarc import SARC
from allbadge_tool.ctr.boot9 import Boot9
from allbadge_tool.ctr.allbadge import allbadge_factory

from allbadge_tool.misc.beep import beep
from allbadge_tool.misc.asyncdl import AsyncDownloader
from allbadge_tool.misc.tkextra import CheckboxButtons, FileSelect
from allbadge_tool.misc.const import BASE_DIR, VERSIONS_130, VERSIONS_131, VERSIONS_PC, Version


class Logic(ABC):
    @abstractproperty
    def versions(self) -> list[Version]:
        ...

    @abstractproperty
    def boot9_path(self) -> Path:
        ...

    @abstractproperty
    def data_path(self) -> Path:
        ...

    @abstractmethod
    def set_progress(self, text: str, ratio: float):
        ...

    @abstractmethod
    def set_error(self, error: str):
        ...

    def begin(self):
        try:
            self._begin()
        except FileNotFoundError as e:
            self.set_error(f"File not found: {e.filename}")
        except Exception as e:
            self.set_error(e.args[0])
        finally:
            beep()

    def _begin(self):
        self.boot9 = Boot9.unpack(self.boot9_path.read_bytes())

        if not self.versions:
            raise ValueError("No versions selected")

        asyncio.run(self.download_files())
        self.decrypt_files()
        self.unpack_files()
        self.set_progress("Done", 1)

    def download_progress(self, ratio: float):
        self.set_progress("Downloading", ratio)

    async def download_files(self):
        self.download_progress(0)

        async with AsyncDownloader() as downloader:
            downloader.set_progress_callback(self.download_progress)
            for version in self.versions:
                if version.url is None:
                    continue
                file = self.data_path / version.dat
                if not file.is_file():
                    downloader.add_entry(version.url, file)

    def decrypt_progress(self, file_ratio: float):
        self.set_progress("Decrypting", file_ratio / len(self.versions))

    def decrypt_files(self):
        self.decrypt_progress(0)

        boss_key = self.boot9.get_keys(0x38).normal_key

        for i, version in enumerate(self.versions, 1):
            if version.dat is None:
                continue

            infile = self.data_path / version.dat
            outfile = self.data_path / version.sarc

            if outfile.is_file():
                self.decrypt_progress(i)
                continue

            boss = BOSS.unpack(infile.read_bytes())
            outfile.write_bytes(boss.decrypt(boss_key))

            self.decrypt_progress(i)

    def unpack_progress(self, file_ratio: float):
        self.set_progress("Unpacking", file_ratio / len(self.versions))

    def unpack_files(self):
        self.unpack_progress(0)

        for i, version in enumerate(self.versions):
            infile = self.data_path / version.sarc
            outfile = self.data_path / version.zip

            if outfile.is_file():
                self.unpack_progress(i + 1)
                continue

            sarc = SARC.unpack(infile.read_bytes())

            with ZipFile(outfile, "w") as fp:
                for j, entry in enumerate(sarc.entries, 1):
                    if parsed := allbadge_factory(entry):
                        fp.writestr(parsed.path, parsed.data)
                    self.unpack_progress(i + j / len(sarc.nodes))


class Window(tk.Tk, Logic):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.name = "Allbadge Tool"

        self.title(self.name)
        self.geometry("500x300")

        self.columnconfigure(0, weight=1)

        self.version_frame = tk.Frame(self)
        self.version_frame.columnconfigure(1, weight=1)
        self.version_label = tk.Label(self.version_frame, text="Select versions")
        self.version_130_selection = CheckboxButtons(self.version_frame, options=VERSIONS_130)
        self.version_131_selection = CheckboxButtons(self.version_frame, options=VERSIONS_131)
        self.version_pc_selection = CheckboxButtons(self.version_frame, options=VERSIONS_PC)

        self.version_label.grid(row=0, column=0, rowspan=2, sticky="nsew")
        self.version_130_selection.grid(row=0, column=1, sticky="ew")
        self.version_131_selection.grid(row=1, column=1, sticky="ew")
        self.version_pc_selection.grid(row=2, column=1, sticky="ew")

        self.boot9_selection = FileSelect(self, title="Select boot9 file", is_dir=False, default=BASE_DIR / "boot9.bin")
        self.data_selection = FileSelect(self, title="Select data folder", is_dir=True, default=BASE_DIR / "data")
        self.begin_button = tk.Button(self, text="Begin", command=self.begin)
        self.progress_var = tk.DoubleVar(value=0.0)
        self.progress_text = tk.Label(self, text="")

        self.add_rows(
            tk.Label(self, text=self.name, font=("Arial", 15, "bold")),
            self.version_frame,
            self.boot9_selection,
            self.data_selection,
            self.begin_button,
            ttk.Progressbar(self, variable=self.progress_var, maximum=1.0),
            self.progress_text,
        )

    def add_rows(self, *widgets: tk.Widget):
        for i, widget in enumerate(widgets):
            widget.grid(row=i, column=0, padx=10, pady=(10, 0), sticky="ew")

    @property
    def versions(self) -> list[Version]:
        return [
            *self.version_130_selection.value(),
            *self.version_131_selection.value(),
            *self.version_pc_selection.value(),
        ]

    @property
    def boot9_path(self) -> Path:
        return Path(self.boot9_selection.var.get())

    @property
    def data_path(self) -> Path:
        return Path(self.data_selection.var.get())

    def set_progress(self, text: str, ratio: float):
        self.progress_var.set(ratio)
        self.progress_text.config(text=f"{text} [{ratio * 100:.2f}%]")
        self.update()

    def set_error(self, error: str):
        self.progress_var.set(0)
        self.progress_text.config(text=error)
        self.update()

    def begin(self):
        self.version_130_selection.disable()
        self.version_131_selection.disable()
        self.version_pc_selection.disable()
        self.boot9_selection.disable()
        self.data_selection.disable()
        self.begin_button.config(state="disabled")
        super().begin()
        self.version_130_selection.enable()
        self.version_131_selection.enable()
        self.version_pc_selection.enable()
        self.boot9_selection.enable()
        self.data_selection.enable()
        self.begin_button.config(state="normal")


def main():
    window = Window()
    window.mainloop()


if __name__ == "__main__":
    main()
