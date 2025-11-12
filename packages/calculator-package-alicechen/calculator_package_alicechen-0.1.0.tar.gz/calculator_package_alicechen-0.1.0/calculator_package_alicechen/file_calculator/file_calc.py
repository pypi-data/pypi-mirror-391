# our package
from calculator_package_alicechen.calc_class import Calculator

# built in
from pathlib import Path

class FileCalculator(Calculator):
    def sum_file(self, path=None):
        if path is None:
            path = Path(__file__).parent / "nums.csv"
        raise NotImplementedError
