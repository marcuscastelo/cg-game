from dataclasses import dataclass

from transformation_matrix import MVPManager
from world import World

@dataclass
class OpenGLScene:
    fbo: int
    texture: int

@dataclass
class AppState:
    closing: bool = False
    scene: OpenGLScene = None
    world: World = World()
    
APP_VARS = AppState()