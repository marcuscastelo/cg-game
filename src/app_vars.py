from dataclasses import dataclass, field
from typing import TYPE_CHECKING


def _create_world():
    from objects.world import World
    return World()
    
if TYPE_CHECKING:
    from objects.world import World

@dataclass
class DebugOptions:
    show_bbox: bool = False

@dataclass
class AppVars:
    closing: bool = False
    # scene: OpenGLScene = None
    world: 'World' = field(default_factory=_create_world)
    debug: DebugOptions = field(default_factory=DebugOptions)
    
APP_VARS = AppVars()