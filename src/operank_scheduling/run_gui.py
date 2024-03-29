import os
from nicegui import ui
from operank_scheduling.gui.ui_models import StateManager
from operank_scheduling.gui.static_ui_elements import OperankHeader, OperankFooter
from operank_scheduling.models.io_utilities import find_project_root

assets_dir = find_project_root() / "assets"
os.environ["MATPLOTLIB"] = "false"
OperankHeader()
StateManager()
OperankFooter()

# Set reload to `False` in production / demo
ui.run(title="Operank", favicon=str(assets_dir / "operank_favicon.jpg"), reload=False)
