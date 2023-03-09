from nicegui import ui, app
from operank_scheduling.models.io_utilities import find_project_root


class OperankHeader:
    def __init__(self) -> None:
        app.add_static_files('/images', str(find_project_root() / "assets"))
        self.header = ui.header()
        with self.header.classes():
            ui.label("Operank")