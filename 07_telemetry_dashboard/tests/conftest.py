import sys
from pathlib import Path

# Put the project root on sys.path so "import src" works under pytest.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
