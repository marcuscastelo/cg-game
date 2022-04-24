from collision import CollisionLayer, CollisionSystem
from objects.element import Element

class World:
    def __init__(self):
        self.elements: list[Element] = []
        self.collision_system = CollisionSystem(self)
        self._updating_inner = False

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
        
        self.elements = [ element for element in self.elements if not element.destroyed ]


WORLD = World()