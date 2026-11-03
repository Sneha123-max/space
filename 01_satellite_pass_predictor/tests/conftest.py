import sys
from pathlib import Path

# Put the project root on sys.path so `import src` works.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
