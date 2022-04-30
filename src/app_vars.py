from dataclasses import dataclass, field
from typing import TYPE_CHECKING


def _create_world():
    '''Hack to create the world without importing the world module (circular dependency)'''
    from world import World
    return World()
    
if TYPE_CHECKING:
    from world import World

@dataclass
class DebugOptions:
    show_bbox: bool = False

@dataclass
class AppVars:
    '''
    Global variables for the application.
    Can be controlled from the GUI and keyboard.
    '''
    
    closing: bool = False
    # scene: OpenGLScene = None
    world: 'World' = field(default_factory=_create_world)
    debug: DebugOptions = field(default_factory=DebugOptions)
    
APP_VARS = AppVars()