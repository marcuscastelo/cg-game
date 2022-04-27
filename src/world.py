from utils.geometry import Vec2, Vec3
from utils.logger import LOGGER
from objects.star import Stars
from objects.element import Element, ElementSpecification

from objects.enemy import Enemy
from objects.garbage import Garbage
from objects.garbage_elipse import Garbage_Elipse
from objects.satellite import Satellite

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
        Stars(world).transform = Transform(Vec3(-1, 0.8, 0.0)) # TODO: change
        
        LOGGER.log_trace('Adding ship...', 'world:setup_scene')
        main_ship = Ship(world)
        LOGGER.log_trace('Enabling ship controls', 'world:setup_scene')
        main_ship.controller.enable()
        # self.spawn(main_ship)
        # LOGGER.log_trace(f'Ship added: {main_ship} ', 'world:setup_scene')
        
        LOGGER.log_trace('Adding enemies', 'world:setup_scene')

        e1 = Enemy(world)
        e1.transform.translation.xy = Vec2(0, 0)

        # e2 = Enemy(world)
        # e2.transform.translation.xy = Vec2(0, 0)

        # e3 = Enemy(world)
        # e3.transform.translation.xy = Vec2(0, 0)
        
        # e4 = Enemy(world)
        # e4.transform.translation.xy = Vec2(0, 0)
        # e4.speed = -1

        LOGGER.log_trace('Adding garbage...', 'world:setup_scene')
        Garbage(world).transform = Transform(Vec3(0.45, 0.45, 0.0)) # TODO: change
        Garbage_Elipse(world).transform = Transform(Vec3(0.45, 0.45, 0.0)) # TODO: change
        
        Garbage(world).transform = Transform(Vec3(-0.35, 0.45, 0.0))
        Garbage_Elipse(world).transform = Transform(Vec3(-0.35, 0.45, 0.0)) # TODO: change
        
        Garbage(world).transform = Transform(Vec3(0.0, 0.75, 0.0))
        Garbage_Elipse(world).transform = Transform(Vec3(0.0, 0.75, 0.0)) # TODO: change
        
        Garbage(world).transform = Transform(Vec3(0.45, -0.45, 0.0))
        Garbage_Elipse(world).transform = Transform(Vec3(0.45, -0.45, 0.0)) # TODO: change
        
        Garbage(world).transform = Transform(Vec3(-0.35, -0.45, 0.0))
        Garbage_Elipse(world).transform = Transform(Vec3(-0.35, -0.45, 0.0)) # TODO: change
        
        Garbage(world).transform = Transform(Vec3(0.0, -0.75, 0.0))
        Garbage_Elipse(world).transform = Transform(Vec3(0.0, -0.75, 0.0)) # TODO: change


        LOGGER.log_trace('Adding satellite...', 'world:setup_scene')
        Satellite(world).transform = Transform(Vec3(0,0,0)) # TODO: change

        LOGGER.log_trace('Done setting up scene', 'world:setup_scene')
        
    def spawn(self, element: Element):
        if not element in self.elements:
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

        


WORLD = World()