import tkinter as tk
from tkinter import ttk
from pathlib import Path
from tkinter import filedialog
from typing import Generic, Mapping, TypeVar


T = TypeVar("T")


class CheckboxButtons(ttk.Frame, Generic[T]):
    def __init__(self, master, options: Mapping[str, T], **kwargs):
        super().__init__(master, **kwargs)

        for i, _ in enumerate(options, 0):
            self.columnconfigure(i, weight=1)

        self.options = options
        self.vars = {option: tk.BooleanVar(value=False) for option in options}

        for i, (option, var) in enumerate(self.vars.items(), 0):
            button = ttk.Checkbutton(self, text=option, variable=var)
            button.grid(row=0, column=i, sticky="ew")

    def value(self) -> list[T]:
        return [self.options[option] for option, var in self.vars.items() if var.get()]

    def disable(self):
        for child in self.winfo_children():
            child.config(state=tk.DISABLED)

    def enable(self):
        for child in self.winfo_children():
            child.config(state=tk.NORMAL)


class FileSelect(ttk.Frame):
    def __init__(
        self,
        master: tk.Tk,
        title: str,
        default: Path,
        is_dir: bool = False,
        **kwargs,
    ):
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=3)

        self.is_dir = is_dir
        self.title = title
        self.default = default
        self.var = tk.StringVar(value=str(default))

        self.button = ttk.Button(master, text=title, command=self.select_file)
        self.field = ttk.Entry(master, textvariable=self.var)

    def grid(self, row: int, column: int, **kwargs):
        self.button.grid(row=row, column=column, **kwargs)
        self.field.grid(row=row, column=column + 1, **kwargs)

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


class ScrolledTextLog(ttk.Frame):
    def __init__(self, master, **kwargs) -> None:
        super().__init__(master, **kwargs)

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(self, background="#ddd")
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)

        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)
        self.canvas.bind("<Button-5>", self.on_mousewheel)

        self.scroll_frame = ttk.Frame(self.canvas)
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.label = ttk.Label(self.scroll_frame, background="#ddd")
        self.label.pack(ipadx=20)

    def on_mousewheel(self, event):
        if self.canvas.yview() != (0.0, 1.0):
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def log_message(self, message: str):
        # self.configure(state=tk.NORMAL)
        text = "\n".join((*self.label.cget("text").splitlines()[-19:], message))
        self.label.configure(text=text)
        self.label.update()
        self.canvas.yview_moveto(1.0)
        # self.insert("end", f"{message}\n")
        # self.see("end")
        # self.configure(state=tk.DISABLED)
