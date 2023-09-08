from tkinter import filedialog
from pathlib import Path
import customtkinter as ctk


CWD = Path(".").resolve()


class FileSelect(ctk.CTkFrame):
    def __init__(self, master: ctk.CTk, button_text: str, default: str, *args, directory: bool = False, **kwargs):
        super().__init__(master, *args, **kwargs)

        self.directory = directory

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.button = ctk.CTkButton(self, text=button_text, command=self._on_click)
        self.button.grid(row=0, column=0, padx=(0, 10), sticky="nsew")

        self.text = ctk.CTkTextbox(self, height=1)
        self.text.insert("1.0", default)
        self.text.grid(row=0, column=1, sticky="nsew")

        self.text.bind("<Return>", lambda _: "break")

    def _on_click(self):
        if self.directory:
            filename = Path(filedialog.askdirectory())
        else:
            filename = Path(filedialog.askopenfilename())

        self.text.delete("1.0", "end")
        self.text.insert("1.0", str(filename))


class DownloadSection(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        self.label = ctk.CTkLabel(self, text="Downloader")
        self.label.grid(row=0, padx=10, pady=(10, 0), sticky="ew")

        self.fs_dir = FileSelect(self, "Output files", str(CWD), directory=True)
        self.fs_dir.grid(row=1, padx=10, pady=(10, 0), sticky="ew")

        self.dl_button = ctk.CTkButton(self, text="Download")
        self.dl_button.grid(row=2, padx=10, pady=(10, 0), sticky="ew")

        self.text_box = ctk.CTkTextbox(self, state="disabled", height=1000)
        self.text_box.grid(row=3, padx=10, pady=(10, 0), sticky="ew")

        self.progress = ctk.CTkProgressBar(self, mode="determinate")
        self.progress.grid(row=4, padx=10, pady=10, sticky="ew")
        self.progress.set(0)


class DecryptSection(ctk.CTkFrame):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)

        self.label = ctk.CTkLabel(self, text="Decrypter")
        self.label.grid(row=0, padx=10, pady=(10, 0), sticky="ew")

        self.fs_boot9 = FileSelect(self, "boot9.firm", str(CWD / "boot9.firm"))
        self.fs_boot9.grid(row=1, padx=10, pady=(10, 0), stick="ew")

        self.fs_input = FileSelect(self, "Input folder", str(CWD), directory=True)
        self.fs_input.grid(row=2, padx=10, pady=(10, 0), stick="ew")

        self.fs_output = FileSelect(self, "Output folder", str(CWD), directory=True)
        self.fs_output.grid(row=3, padx=10, pady=(10, 0), stick="ew")

        self.dl_button = ctk.CTkButton(self, text="Decrypt")
        self.dl_button.grid(row=4, padx=10, pady=(10, 0), sticky="ew")

        self.text_box = ctk.CTkTextbox(self, state="disabled", height=1000)
        self.text_box.grid(row=5, padx=10, pady=(10, 0), sticky="ew")

        self.progress = ctk.CTkProgressBar(self, mode="determinate")
        self.progress.grid(row=6, padx=10, pady=10, sticky="ew")
        self.progress.set(0)


def main():
    app = ctk.CTk()
    app.title("allbadge Downloader and Decrypter")
    app.geometry("1000x600")

    app.grid_columnconfigure(0, weight=1)
    app.grid_columnconfigure(1, weight=1)
    app.grid_rowconfigure(0, weight=1)

    dl_frame = DownloadSection(app)
    dl_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    dc_frame = DecryptSection(app)
    dc_frame.grid(row=0, column=1, padx=(0, 10), pady=10, sticky="nsew")

    app.mainloop()


if __name__ == "__main__":
    main()
