from dataclasses import dataclass, field
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
class AppVars:
    closing: bool = False
    # scene: OpenGLScene = None
    world: 'World' = field(default_factory=_create_world)
    debug: DebugOptions = field(default_factory=DebugOptions)
    cursor: Cursor = field(default_factory=Cursor)
    camera: Camera = None

    def __post_init__(self):
        if self.camera is None:
            self.camera = Camera(self.world)
APP_VARS = AppVars()