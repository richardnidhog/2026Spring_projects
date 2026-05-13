"""Project-wide paths."""
from pathlib import Path

PROJECT_ROOT: Path = Path(__file__).resolve().parent.parent
OUTPUT_DIR:   Path = PROJECT_ROOT / "test_images"
OUTPUT_DIR.mkdir(exist_ok=True)
