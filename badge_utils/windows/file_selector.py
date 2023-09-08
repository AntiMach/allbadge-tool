import dearpygui.dearpygui as dpg


class FileSelector:
    def __init__(self, button: int | str, text_field: int | str, directory: bool = False) -> None:
        self.button = button
        self.text_field = text_field

        self.dir_dialog = dpg.add_file_dialog(
            directory_selector=directory,
            show=False,
            width=700,
            height=400,
            callback=self._make_changes,
            cancel_callback=dpg.hide_item,
        )

        dpg.set_item_callback(button, self._show_selector)

    def get_path(self) -> str:
        return dpg.get_value(self.text_field)

    def _show_selector(self):
        dpg.show_item(self.dir_dialog)

    def _make_changes(self, _, data):
        dpg.hide_item(self.dir_dialog)
        dpg.set_value(self.text_field, data["file_path_name"])


def file_selector(name: str, default: str, directory: bool = False) -> FileSelector:
    with dpg.group(horizontal=True):
        return FileSelector(
            button=dpg.add_button(
                label=name,
                width=120,
            ),
            text_field=dpg.add_input_text(
                default_value=default,
                width=-1,
            ),
            directory=directory,
        )
