from utils.geometry import Vec3
from collision import CollisionSystem
from objects.element import Element

import keyboard
from objects.enemy import Enemy

from objects.ship import Ship
from transformation_matrix import Transform

class World:
    def __init__(self):
        self.elements: list[Element] = []
        self.collision_system = CollisionSystem(self)
        self._updating_inner = False

    def setup_scene(self):
        world = self

        self.elements.clear()
        main_ship = Ship(world, Transform(Vec3((0, 0, 0))))
        main_ship.controller.enable()

        self.add_element(main_ship)
        
        enemies = [
            Enemy(world, Transform(Vec3(-0.9,    0.5,    0.0))),
            Enemy(world, Transform(Vec3( 0.0,    0.5,    0.0))),
            Enemy(world, Transform(Vec3( 0.9,    0.5,    0.0))),
            Enemy(world, Transform(Vec3( 0.0,    0.9,    0.0))),
        ]

        for enemy in enemies:
            self.add_element(enemy)

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

        if keyboard.is_pressed('r'):
            self.setup_scene()

WORLD = World()