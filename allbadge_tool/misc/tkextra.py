import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from typing import Generic, Mapping, TypeVar


T = TypeVar("T")


class CheckboxButtons(tk.Frame, Generic[T]):
    def __init__(self, master, options: Mapping[str, T], **kwargs):
        super().__init__(master, **kwargs)

        self.columnconfigure(list(range(len(options))), weight=1)

        self.options = options
        self.vars = {option: tk.BooleanVar(value=False) for option in options}

        for i, (option, var) in enumerate(self.vars.items(), 0):
            button = tk.Checkbutton(self, text=option, variable=var)
            button.grid(row=0, column=i, sticky="ew")

    def value(self) -> list[T]:
        return [self.options[option] for option, var in self.vars.items() if var.get()]

    def disable(self):
        for child in self.winfo_children():
            child.config(state=tk.DISABLED)

    def enable(self):
        for child in self.winfo_children():
            child.config(state=tk.NORMAL)


class FileSelect(tk.Frame):
    def __init__(
        self,
        master: tk.Tk,
        title: str,
        default: Path,
        is_dir: bool = False,
        **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.columnconfigure(1, weight=1)

        self.is_dir = is_dir
        self.title = title
        self.default = default
        self.var = tk.StringVar(value=str(default))

        self.button = tk.Button(self, text=title, command=self.select_file)
        self.button.grid(row=0, column=0, sticky="ew")

        self.field = tk.Entry(self, textvariable=self.var)
        self.field.grid(row=0, column=1, padx=(10, 0), sticky="ew")

    def select_file(self):
        if self.is_dir:
            result = filedialog.askdirectory(initialdir=self.default, title=self.title)
        else:
            result = filedialog.askopenfilename(initialdir=self.default.parent, title=self.title)
        if result:
            self.var.set(str(Path(result)))

    def disable(self):
        for child in self.winfo_children():
            child.config(state=tk.DISABLED)

    def enable(self):
        for child in self.winfo_children():
            child.config(state=tk.NORMAL)
