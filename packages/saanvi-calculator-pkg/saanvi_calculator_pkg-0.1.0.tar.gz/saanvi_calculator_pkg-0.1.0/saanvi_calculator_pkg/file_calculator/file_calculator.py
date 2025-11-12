# built in
from pathlib import Path

# pip installed 

# our package
from saanvi_calculator_pkg.calculator import Calculator

class FileCalculator(Calculator):
	def sum_file(self, path=None):
		if path is None:
			path = Path(__file__).parent / "nums.csv"
		raise NotImplementedError
