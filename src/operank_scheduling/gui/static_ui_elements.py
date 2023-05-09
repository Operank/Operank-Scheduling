from nicegui import ui, app
from operank_scheduling.models.io_utilities import find_project_root


class OperankHeader:
    def __init__(self) -> None:
        app.add_static_files("/images", str(find_project_root() / "assets"))
        self.header = ui.header().classes("justify-between")
        with self.header:
            ui.label("Operank").style('font-size: 2em')
            ui.image("/images/operank_logo.jpg").style("height: 40px; width: 40px")


class OperankFooter:
    def __init__(self) -> None:
        ui.footer()
