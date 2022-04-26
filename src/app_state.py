from dataclasses import dataclass

from world import World

@dataclass
class AppState:
    closing: bool = False
    # scene: OpenGLScene = None
    world: World = World()
    
APP_VARS = AppState()