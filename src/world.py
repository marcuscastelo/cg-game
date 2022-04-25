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
    def __init__(self):
        self.elements: list[Element] = []
        self.collision_system = CollisionSystem(self)
        self._updating_inner = False

    def setup_scene(self):
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

        # LOGGER.log_trace(f'Adding {len(enemies)} enemies to scene', 'world:setup_scene')
        # for enemy in enemies:
        #     LOGGER.log_trace(f'Adding enemy(id={id(enemy)}) to scene', 'world:setup_scene')
        #     self.add_element(enemy)


        # test_lines = Lines(world, points=[
        #     Vec3(-0.5, -0.5, 0),
        #     Vec3(0.5, -0.5, 0),
        #     Vec3(0.5, 0.5, 0),
        #     Vec3(-0.5, 0.5, 0),
        #     Vec3(-0.5, -0.5, 0),
        # ])

        # self.add_element(test_lines)

        LOGGER.log_trace('Done setting up scene', 'world:setup_scene')
        
    def add_element(self, element: Element):
        self.elements.append(element)
 
    def remove_element(self, element: Element):
        if self._updating_inner:
            print('Cannot remove element while updating')
            return
        self.elements.remove(element)

    def update(self):
        self._updating_inner = True
        for element in self.elements:
            element.update()
        self._updating_inner = False
        
        self.elements[:] = [ element for element in self.elements if not element.destroyed ]

        if IS.is_pressed('r'):
            self.setup_scene()

WORLD = World()