from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from world import World

@dataclass
class AppState:
    closing: bool = False
    # scene: OpenGLScene = None
    world: World = World()
    
APP_VARS = AppState()