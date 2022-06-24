from dataclasses import dataclass, field
import time
from typing import TYPE_CHECKING

from camera import Camera


def _create_world():
    from objects.world import World
    return World()

    
if TYPE_CHECKING:
    from objects.world import World

@dataclass
class DebugOptions:
    show_bbox: bool = False

@dataclass
class Cursor:
    lastX: float = None
    lastY: float = None
    capturing: bool = True

@dataclass
class FpsTracker:
    last_time: float = time.time()
    last_delta: float = 0

    @property
    def fps(self) -> int:
        if self.last_delta == 0: return 0
        return 1/self.last_delta

    def update_calc_fps(self, time: float):
        delta = time - self.last_time
        self.last_time = time
        self.last_delta = delta

@dataclass
class AppVars:
    closing: bool = False
    # scene: OpenGLScene = None
    world: 'World' = field(default_factory=_create_world)
    debug: DebugOptions = field(default_factory=DebugOptions)
    cursor: Cursor = field(default_factory=Cursor)
    camera: Camera = None

    game_fps: FpsTracker = field(default_factory=FpsTracker)
    gui_fps: FpsTracker = field(default_factory=FpsTracker)

    def __post_init__(self):
        if self.camera is None:
            self.camera = Camera('Main Camera')
            self.world.spawn(self.camera)
APP_VARS = AppVars()