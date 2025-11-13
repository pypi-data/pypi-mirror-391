from .pi_digit_core import PiDigitCore
import os

class PiDigitFinder:
    def __init__(self, lib_path=None):
        if lib_path is None:
            lib_path = os.path.dirname(os.path.abspath(__file__)) + "/PiBin/pi_digit"
        self.lib_path = lib_path
        self.lib = None
        self.core = PiDigitCore(lib_path=self.lib_path)
        self.lib = self.core.lib

    def get_nth_digit(self, n):
        res = self.lib.get_nth_pi_digit(n)
        return res
