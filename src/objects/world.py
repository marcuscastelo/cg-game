import time
from utils.geometry import Vec2, Vec3
from utils.logger import LOGGER
from objects.cube import Cube
from objects.element import Element

class World:
    '''
    Class responsible for describing the world.
    It holds all the elements in a list and updates them.
    When they are marked for removal, they are removed from the list in the next update.
    '''
    
    def __init__(self):
        self.elements: list[Element] = []
        self._updating_inner = False
        self._last_update_time = time.time()

    def setup_scene(self):
        '''
        This function is called when the user presses the 'r' key and when the application starts.
        It populates the world with the elements that are needed to play the game.

        Objects declared at the "bottom" of the code (last line) as rendered behind the upper ones.
        '''
        LOGGER.log_trace('Setting up scene', 'world:setup_scene')
        world = self

        # LOGGER.log_trace('Emptying scene', 'world:setup_scene')
        # self.elements.clear()

        # ... #
        cube1 = Cube(world)
        cube1.transform.scale = Vec3(0.2, 0.2, 0.2)
        cube1.transform.translation = Vec3(10, 10, 10)
        cube2 = Cube(world)
        cube2.transform.translation = Vec3(1,1,1)
        cube2.transform.scale = Vec3(-0.2, 0.2, 0.2)

        LOGGER.log_info('Done setting up scene', 'world:setup_scene')
        
    def spawn(self, element: Element):
        self.elements.append(element)

    def destroy(self, element: Element):
        element.destroy()

    def update(self):
        '''
        This function is called every frame.
        It updates the world and all the elements in it.
        '''
        t = time.time()
        delta_time = t - self._last_update_time

        # Update elements
        for element in self.elements[::-1]:
            if not element.destroyed: # In case the element was destroyed while updating
                element.update(delta_time)

        # Remove elements that are marked for removal
        self.elements[:] = [ element for element in self.elements if not element.destroyed ]


        self._last_update_time = t
        
    def is_player_victory(self) -> bool:
        '''
        If no more enemies or garbage is left, the player has won.
        '''
        return False

    def is_player_defeat(self) -> bool:
        '''
        If the player has been destroyed, he has lost.
        '''
        return False

WORLD = World()