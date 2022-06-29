from dataclasses import dataclass, field
import time
from typing import TYPE_CHECKING, Union

from utils.geometry import Vec3

from camera import Camera
from objects.element import Element
from transform import Transform


def _create_world():
    ''' Creates a new world to be used in the application. '''
    from objects.world import World
    return World()

if TYPE_CHECKING:
    from objects.world import World
    from objects.bullet_ray import BulletRay

@dataclass
class DebugOptions:
    ''' Options for debugging '''
    show_bbox: bool = False # Show bounding boxes (hitboxes)

@dataclass
class Cursor:
    ''' Keeps track of the cursor position in the screen '''
    lastX: float = None
    lastY: float = None
    capturing: bool = True # If clicked outside the window, the cursor is not captured

@dataclass
class FpsTracker:
    ''' Keeps track of the frames per second of some thread. '''
    last_time: float = time.time()
    last_delta: float = 0

    @property
    def fps(self) -> int:
        ''' Returns the current frame's FPS (note: this does not update the FPS every frame) '''
        if self.last_delta == 0: return 0
        return 1/self.last_delta

    def update_calc_fps(self, time: float):
        ''' Updates the FPS calculation '''
        delta = time - self.last_time
        self.last_time = time
        self.last_delta = delta

@dataclass
class LightingConfig:
    ''' Configuration for the lighting. '''

    # Ambient light
    Ka_x: float = 0.8
    Ka_y: float = 0.8
    Ka_z: float = 0.8

    # Diffuse light
    Kd_x: float = 5
    Kd_y: float = 5
    Kd_z: float = 5

    # Specular light
    Ks_x: float = 0.1
    Ks_y: float = 0.1
    Ks_z: float = 0.1
    Ns: float = 10

    # Main light position    
    light_position: Vec3 = field(default_factory=lambda: Vec3(2,0.72,0))

    # Daylight cycle (ambient light change over time)
    do_daylight_cycle: bool = False

@dataclass
class AppVars:
    ''' Global variables, controlled by the game logic and the user interface. '''

    closing: bool = False # Used to sync the closing event between the main thread and the GUI thread.
    debug_options: DebugOptions = field(default_factory=DebugOptions)

    world: 'World' = field(default_factory=_create_world)
    cursor: Cursor = field(default_factory=Cursor)
    camera: Camera = None

    lighting_config: LightingConfig = field(default_factory=LightingConfig)
    selected_element: Union[Element, None] = None # An element can be selected by the user via the selection ray or the GUI
    last_bullet: Union['BulletRay', None] = None # Keeps track of the last shot bullet (to send its position to the light shader)

    game_fps: FpsTracker = field(default_factory=FpsTracker)
    gui_fps: FpsTracker = field(default_factory=FpsTracker)

    def __post_init__(self):
        if self.camera is None:
            # TODO: why initialize camera here? move it to world
            self.camera = Camera(
                name='Main Camera', 
                transform=Transform(translation=Vec3(-12, 1.7, -5)),
                ray_selectable=False,
                ray_destroyable=False,
            )

APP_VARS = AppVars()