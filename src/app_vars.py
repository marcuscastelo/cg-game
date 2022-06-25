from dataclasses import dataclass, field
import time
from typing import TYPE_CHECKING, Union

from utils.geometry import Vec3

from camera import Camera
from objects.element import Element
from transform import Transform


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
class LightingConfig:
    Ka: float = 1
    Kd: float = 1
    Ks: float = 1
    Ns: float = 1000.0
    light_position: Vec3 = field(default_factory=lambda: Vec3(2,0.72,0))
    do_daylight_cycle: bool = False

@dataclass
class AppVars:
    closing: bool = False
    # scene: OpenGLScene = None
    world: 'World' = field(default_factory=_create_world)
    debug: DebugOptions = field(default_factory=DebugOptions)
    cursor: Cursor = field(default_factory=Cursor)
    camera: Camera = None
    lighting_config: LightingConfig = field(default_factory=LightingConfig)
    selected_element: Union[Element, None] = None

    game_fps: FpsTracker = field(default_factory=FpsTracker)
    gui_fps: FpsTracker = field(default_factory=FpsTracker)

    def __post_init__(self):
        if self.camera is None:
            self.camera = Camera('Main Camera', transform=Transform(translation=Vec3(0, 1.7, 0)))
APP_VARS = AppVars()