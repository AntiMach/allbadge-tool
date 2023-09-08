from pathlib import Path
import dearpygui.dearpygui as dpg

from badge_utils.windows.file_selector import file_selector
from badge_utils.modules.downloader import AllbadgeDownloader


CWD = Path(".").resolve()


class setup:
    def __init__(self) -> None:
        self.downloader = AllbadgeDownloader()

        with dpg.window(
            label="Allbadge Downloader",
            width=600,
            no_close=True,
            no_resize=True,
            pos=(20, 20),
        ):
            self.directory = file_selector("Output folder", str(CWD), True)

            self.button = dpg.add_button(label="Download", width=-1, callback=self.start_download)
            self.text_box = dpg.add_input_text(width=-1, height=100, multiline=True, readonly=True)
            self.progress_bar = dpg.add_progress_bar(width=-1)

            self.downloader.set_message_callback(self.insert_text)
            self.downloader.set_progress_callback(self.update_progress)

    def start_download(self):
        dpg.disable_item(self.button)
        self.downloader.start(self.directory.get_path())
        dpg.enable_item(self.button)

    def insert_text(self, message: str):
        dpg.set_value(self.text_box, f"{message}\n{dpg.get_value(self.text_box)}")

    def update_progress(self, progress: int):
        dpg.set_value(self.progress_bar, progress)
