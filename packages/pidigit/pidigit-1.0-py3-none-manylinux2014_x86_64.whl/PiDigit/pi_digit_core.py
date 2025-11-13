import ctypes
import sys

class PiDigitCore:
    def __init__(self, lib_path):
        self.lib = None
        self.path = lib_path
        self.load_library(self.path)
        self.prepare_methods()

    def load_library(self, lib_path):
        if sys.platform.startswith("linux"):
            libname = self.path + ".so"
        elif sys.platform == "win32":
            libname = self.path + ".dll"
        self.lib = ctypes.CDLL(libname)

    def prepare_methods(self):
        self.lib.get_nth_pi_digit.argtypes = (ctypes.c_uint,)
        self.lib.get_nth_pi_digit.restype = ctypes.c_int

    
