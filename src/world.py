from collision import CollisionLayer, CollisionSystem
from objects.element import Element

class World:
    def __init__(self):
        self.elements: list[Element] = []
        self.collision_system = CollisionSystem(self)

    def add_element(self, element: Element):
        self.elements.append(element)

WORLD = World()