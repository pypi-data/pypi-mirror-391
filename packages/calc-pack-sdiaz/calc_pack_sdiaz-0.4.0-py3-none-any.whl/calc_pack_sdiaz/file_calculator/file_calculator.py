from pathlib import Path #built in imports at the top

#section for pip install

#section for our package
#from ..calculator import Calculator this is relative path
from calc_pack_sdiaz.calculator import Calculator #this is absolute path

class FileCalculator(Calculator):
    def sum_file(self, path):
        if path is None:
            path = Path(__file__).parent / "nums.csv" #critical that when we have a package, all file paths are relative to the package itself, generally pathlib is the way we want to work with paths in Python
        raise NotImplementedError

