# built in
from pathlib import Path

# pip installed
from tqdm import tqdm

# our package
# from ..calculator import Calculator
from cse3150_jimmy_padilla_calculator.calculator import Calculator


class FileCalculator(Calculator):
    def sum_file(self, path=None) -> int:
        if path is None:
            # path = Path(__file__).resolve().parent / "nums.csv"
            import sys
            print(f"DEBUG: __file__ = {__file__}")
            print(f"DEBUG: Path(__file__) = {Path(__file__)}")
            print(f"DEBUG: Path(__file__).resolve() = {Path(__file__).resolve()}")
            print(f"DEBUG: Path(__file__).resolve().parent = {Path(__file__).resolve().parent}")
            print(f"DEBUG: sys.path = {sys.path}")
            
            module_dir = Path(__file__).resolve().parent
            path = module_dir / "nums.csv"
            print(f"DEBUG: final path = {path}")
            print(f"DEBUG: path.exists() = {path.exists()}")
            
            # Also check if CSV exists in alternate locations
            print(f"DEBUG: Contents of {module_dir}:")
        with tqdm(total=100_000_000, desc="summing file") as pbar:
            total = 0
            with path.open() as f:
                for line in f:
                    total += int(line)
                    pbar.update()
            return total
