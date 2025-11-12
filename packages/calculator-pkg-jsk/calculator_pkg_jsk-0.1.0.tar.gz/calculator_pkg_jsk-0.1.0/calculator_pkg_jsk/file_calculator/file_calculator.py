#built in
from pathlib import Path
#pip installed

#our package
from calculator_pkg_jsk.calc import Calculator

class FileCalculator(Calculator):
    def sum_file(self, path=None):
        if path is None:
            path = Path(__file__).parent / "nums.csv"
        raise NotImplementedError

