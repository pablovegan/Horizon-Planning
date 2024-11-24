"""Script to copy the examples folder into the docs.
"""

import shutil
from pathlib import Path

spain_path = Path("examples", "Spain", "spain.ipynb")
sweden_path = Path("examples", "Sweden", "sweden.ipynb")

docs_path = Path("docs", "examples")

shutil.copy(spain_path, docs_path)
shutil.copy(sweden_path, docs_path)
