import importlib
from pathlib import Path
import dearpygui.dearpygui as dpg


ROOT = Path(__file__).parent


def main():
    dpg.create_context()

    for file in (Path(__file__).parent / "modules").iterdir():
        if file.suffix != ".py":
            continue

        file = file.with_suffix("")

        module = importlib.import_module(".".join(file.relative_to(ROOT.parent).parts))
        module.setup()

    dpg.create_viewport(
        title="Nintendo Badge Arcade Utilities",
        clear_color=list(0x252526.to_bytes(3)),
    )

    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    main()
