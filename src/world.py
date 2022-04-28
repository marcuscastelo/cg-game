from utils.geometry import Vec2, Vec3
from utils.logger import LOGGER
from objects.garbage import Garbage
from objects.satellite import Satellite
from objects.star import Stars
from objects.element import Element

from objects.enemy import Enemy

from objects.ship import Ship

class World:
    '''
    Class responsible for describing the world.
    It holds all the elements in a list and updates them.
    When they are marked for removal, they are removed from the list in the next update.
    '''
    
    def __init__(self):
        self.elements: list[Element] = []
        self._updating_inner = False

    def setup_scene(self):
        '''
        This function is called when the user presses the 'r' key and when the application starts.
        It populates the world with the elements that are needed to play the game.
        '''
        LOGGER.log_trace('Setting up scene', 'world:setup_scene')
        world = self

        LOGGER.log_trace('Emptying scene', 'world:setup_scene')
        self.elements.clear()

        LOGGER.log_trace('Adding star ', 'world:setup_scene')
        Stars(world).transform.translation.xy = Vec2(-1, 0.8) # TODO: change
        
        LOGGER.log_trace('Adding ship...', 'world:setup_scene')
        main_ship = Ship(world)
        LOGGER.log_trace('Enabling ship controls', 'world:setup_scene')
        main_ship.controller.enable()
        LOGGER.log_trace(f'Ship added: {main_ship} ', 'world:setup_scene')
        
        LOGGER.log_trace('Adding enemies', 'world:setup_scene')

        Enemy(world).transform.translation.xy = Vec2(-0.8,    0.5)
        Enemy(world).transform.translation.xy = Vec2( 0.0,    0.5)
        Enemy(world).transform.translation.xy = Vec2( 0.8,    0.5)
        (e4:=Enemy(world)).transform.translation.xy = Vec2( 0.0,    0.9)
        e4.speed = -1

        LOGGER.log_trace('Adding garbage...', 'world:setup_scene')
        Garbage(world).transform.translation.xy = Vec2(0.45, 0.45)
        Garbage(world).transform.translation.xy = Vec2(-0.45, 0.45)
        Garbage(world).transform.translation.xy = Vec2(0.0, 0.75)
        Garbage(world).transform.translation.xy = Vec2(0.45, -0.45)
        Garbage(world).transform.translation.xy = Vec2(-0.45, -0.45)
        Garbage(world).transform.translation.xy = Vec2(0.0, -0.75)
        LOGGER.log_trace('Garbage added', 'world:setup_scene')

        LOGGER.log_trace('Adding satellite...', 'world:setup_scene')
        Satellite(world).transform.translation.xy = Vec2(0.7, -0.7)
        LOGGER.log_trace('Satellite added', 'world:setup_scene')


        LOGGER.log_info('Done setting up scene', 'world:setup_scene')
        
    def spawn(self, element: Element):
        self.elements.append(element)
 
    def destroy(self, element: Element):
        element.destroy()

    def game_ended(self) -> bool:
        return len(list(enemy for enemy in self.elements if isinstance(enemy, Enemy))) == 0

    def update(self):
        '''
        This function is called every frame.
        It updates the world and all the elements in it.
        '''

        # Update elements
        for element in self.elements:
            if not element.destroyed: # In case the element was destroyed while updating
                element.update() 
        
        # Remove elements that are marked for removal
        self.elements[:] = [ element for element in self.elements if not element.destroyed ]

        
    def is_player_victory(self) -> bool:
        return len(list(enemy for enemy in self.elements if isinstance(enemy, Enemy))) == 0


WORLD = World()