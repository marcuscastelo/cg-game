from utils.geometry import Vec2, Vec3
from utils.logger import LOGGER
from objects._2d.garbage import Garbage
from objects._2d.little_star import LittleStar
from objects._2d.satellite import Satellite
from objects._2d.star import Star
from objects.element import Element

from objects._2d.enemy import Enemy

from objects._2d.ship import Ship
from objects.world import World

class _2DWorld(World):
    '''
    Class responsible for describing the world.
    It holds all the elements in a list and updates them.
    When they are marked for removal, they are removed from the list in the next update.
    '''
    
    def setup(self):
        '''
        This function is called when the user presses the 'r' key and when the application starts.
        It populates the world with the elements that are needed to play the game.

        Objects declared at the "bottom" of the code (last line) as rendered behind the upper ones.
        '''
        LOGGER.log_trace('Setting up scene', 'world:setup_scene')
        world = self

        LOGGER.log_trace('Emptying scene', 'world:setup_scene')
        self.elements.clear()


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
        Satellite(world).transform.translation.xy = Vec2(0.6, -0.6)
        LOGGER.log_trace('Satellite added', 'world:setup_scene')

        LOGGER.log_trace('Adding star ', 'world:setup_scene')
        Star(world).transform.translation.xy = Vec2(-1, 0.8) # TODO: change

        LOGGER.log_trace('Adding little stars ', 'world:setup_scene')
        LittleStar(world).transform.translation.xy = Vec2(0, 0.8)
        LittleStar(world).transform.translation.xy = Vec2(0.9, 0.2)
        LittleStar(world).transform.translation.xy = Vec2(0.2, 0.1)
        LittleStar(world).transform.translation.xy = Vec2(0.5, 0.5)
        LittleStar(world).transform.translation.xy = Vec2(0.7, 0.8)

        LittleStar(world).transform.translation.xy = Vec2(-1, 0.8)
        LittleStar(world).transform.translation.xy = Vec2(-0.6, 0.5)
        LittleStar(world).transform.translation.xy = Vec2(-0.7, 0.8)

        LittleStar(world).transform.translation.xy = Vec2(0.5, -0.8)
        LittleStar(world).transform.translation.xy = Vec2(0.3, -0.7)
        LittleStar(world).transform.translation.xy = Vec2(0.1, -0.4)

        LittleStar(world).transform.translation.xy = Vec2(-0.2, 0)
        LittleStar(world).transform.translation.xy = Vec2(-0.3, -0.7)
        LittleStar(world).transform.translation.xy = Vec2(-0.4, -0.2)
        LittleStar(world).transform.translation.xy = Vec2(-0.8, -0.9)


        LOGGER.log_info('Done setting up scene', 'world:setup_scene')
        
    def spawn(self, element: Element):
        self.elements.append(element)

    def destroy(self, element: Element):
        element.destroy()
        
    def is_player_victory(self) -> bool:
        '''
        If no more enemies or garbage is left, the player has won.
        '''
        return len(list(element for element in self.elements if isinstance(element, (Enemy, Garbage)))) == 0

    def is_player_defeat(self) -> bool:
        '''
        If the player has been destroyed, he has lost.
        '''
        return len(list(element for element in self.elements if isinstance(element, (Ship)))) == 0