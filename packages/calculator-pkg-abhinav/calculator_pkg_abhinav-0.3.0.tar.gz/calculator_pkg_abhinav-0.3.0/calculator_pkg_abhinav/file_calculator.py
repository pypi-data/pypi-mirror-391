#built in
from pathlib import Path
#pip installed

#our package
from calculator_pkg_ex.calculator import Calculator
class FileCalculator(Calculator):
    def sum_file(self, path=none):
        if path is none:
            path = Path(__file__).parent/"nums.csv"
        raise NotImplementedError
