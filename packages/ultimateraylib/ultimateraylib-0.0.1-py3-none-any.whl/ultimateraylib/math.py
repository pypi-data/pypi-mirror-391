from ._classes import *
# raymath

lib.Clamp.argtypes = [ctypes.c_float, ctypes.c_float, ctypes.c_float]
lib.Clamp.restype = ctypes.c_float
def clamp(value,min,max):
    return lib.Clamp(value, min, max)
