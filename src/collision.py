from dataclasses import dataclass
from typing import TYPE_CHECKING, Callable, Type
from objects.element import Element

from objects.enemy import Enemy

if TYPE_CHECKING:
    from world import World

@dataclass
class CollisionLayer:
    name: str
    trigger_classes: list[Type]


class CollisionSystem:
    def __init__(self, world: 'World'):
        self.layers: list[CollisionLayer] = []
        self.subscribers: dict[CollisionLayer, dict[Element, Callable]] = {}
        self.world = world

    def on_collision(self, element: Element, other: Element):
        for collision_layer in self.layers:
            if isinstance(other, collision_layer.trigger_classes):
                if element in self.subscribers[collision_layer]:
                    callback = self.subscribers[collision_layer][element]
                    callback(other)

    def subscribe(self, layer: CollisionLayer, subscriber: Element, callback: Callable):
        if layer not in self.subscribers:
            self.subscribers[layer] = {}
        self.subscribers[layer][subscriber] = callback       

        pass

    def _physic_update(self):
        elements = self.world.elements
        for element in elements:
            for other in elements:
                if element is not other:
                    if element.collides_with(other):
                        print(f'Collision between {element} and {other}')
                        self.on_collision(element, other)