from pathlib import Path
import dearpygui.dearpygui as dpg

from badge_utils.windows.file_selector import file_selector


CWD = Path(".").resolve()


def setup():
    with dpg.window(
        label="Allbadge Decrypter",
        width=600,
        no_close=True,
        no_resize=True,
        pos=(640, 20),
    ):
        file_selector("boot9.firm", str(CWD / "boot9.bin"), False)
        file_selector("Input folder", str(CWD), True)
        file_selector("Output folder", str(CWD), True)

        dpg.add_button(label="Decrypt", width=-1)
        dpg.add_input_text(width=-1, height=100, multiline=True, readonly=True)
        dpg.add_progress_bar(width=-1)
