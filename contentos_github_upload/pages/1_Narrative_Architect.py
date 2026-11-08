"""Launch the standalone Narrative Architect inside the public Content Studio app."""
from pathlib import Path
import runpy

app = Path(__file__).resolve().parents[2] / "projects" / "narrative-architect" / "app.py"
runpy.run_path(str(app), run_name="__main__")
