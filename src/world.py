from utils.geometry import Vec3
from utils.logger import LOGGER
from collision import CollisionSystem
from objects.element import Element

from objects.enemy import Enemy
from objects.lines import Lines

from objects.ship import Ship
from transformation_matrix import Transform

from input.input_system import INPUT_SYSTEM as IS

class World:
    '''
    Class responsible for describing the world.
    It holds all the elements in a list and updates them.
    When they are marked for removal, they are removed from the list in the next update.
    '''
    
    def __init__(self):
        self.elements: list[Element] = []
        self.collision_system = CollisionSystem(self)
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

        LOGGER.log_trace('Adding ship...', 'world:setup_scene')
        main_ship = Ship(world, Transform(Vec3((0, 0, 0))))
        LOGGER.log_trace('Enabling ship controls', 'world:setup_scene')
        main_ship.controller.enable()
        self.add_element(main_ship)
        LOGGER.log_trace(f'Ship added: {main_ship} ', 'world:setup_scene')
        
        LOGGER.log_trace('Adding enemies', 'world:setup_scene')
        enemies = [
            Enemy(world, Transform(Vec3(-0.9,    0.5,    0.0))),
            Enemy(world, Transform(Vec3( 0.0,    0.5,    0.0))),
            Enemy(world, Transform(Vec3( 0.9,    0.5,    0.0))),
            Enemy(world, Transform(Vec3( 0.0,    0.9,    0.0))),
        ]

        LOGGER.log_trace('Done setting up scene', 'world:setup_scene')
        
    def add_element(self, element: Element):
        self.elements.append(element)
 
    def remove_element(self, element: Element):
        if self._updating_inner:
            raise RuntimeError('Cannot remove element while updating world')

        self.elements.remove(element)

    def update(self):
        '''
        This function is called every frame.
        It updates the world and all the elements in it.
        '''

        self._updating_inner = True # Security measure to avoid removing elements while updating (it would break the iterator)

        # Update elements
        for element in self.elements:
            element.update() 
        
        self._updating_inner = False
        
        # Remove elements that are marked for removal
        self.elements[:] = [ element for element in self.elements if not element.destroyed ]

        # Special shortcut to reset scene
        if IS.is_pressed('r'):
            self.setup_scene()

WORLD = World()