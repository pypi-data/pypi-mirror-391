#built-in
from pathlib import Path

#pip-install

#our package
from ..calculator import Calculator

class FileCalculator(Calculator):
    def sum_file(self, path):
        if path is None:
            path = Path(__file__).parent / "nums.csv"
        raise NotImplementedError
