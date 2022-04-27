import ctypes
from utils.geometry import Rect2


WINDOW_SIZE = (800, 800)
GL_DIM = 4 # OpenGL works in 4D space
SCREEN_RECT = Rect2(-1, -1, 1, 1)
FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)