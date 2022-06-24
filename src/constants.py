import ctypes
from utils.geometry import Rect2, Vec2

MOCK_RESOLUTION = Vec2(1920, 1080-300)
ASPECT_RATIO = MOCK_RESOLUTION.x / MOCK_RESOLUTION.y
GUI_WIDTH = 550
WINDOW_SIZE = (
    int(MOCK_RESOLUTION.x-GUI_WIDTH), 
    int(MOCK_RESOLUTION.y)
)
GL_DIM = 4 # OpenGL works in 4D space
SCREEN_RECT = Rect2(-1, -1, 1, 1)
FLOAT_SIZE = ctypes.sizeof(ctypes.c_float)

WORLD_SIZE = 40 # 40x40