# conftest.py — garante que o diretório tests/ é um pacote Python reconhecido pelo pytest-cov
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "tests"))
