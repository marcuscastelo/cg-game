from numpy import random
from utils.sig import metsig
from objects.element import Element
from objects.projectile import Projectile

class Enemy(Element):
    def _init_vertices(self):
        self._vertices = [
            *(-0.1, 0.6-0.5, 0.0),
            *(-0.1, 0.4-0.5, 0.0),
            *(0.1, 0.4-0.5, 0.0),

            *(0.1, 0.4-0.5, 0.0),
            *(0.1, 0.6-0.5, 0.0),
            *(-0.1, 0.6-0.5, 0.0),
        ]
    
    def _physic_update(self):
        from world import WORLD
        min_x, min_y, max_x, max_y = Element.get_bounding_box(self)
        # print(f'Enemy(id={id(self)}) bbox: {min_x}, {min_y}, {max_x}, {max_y}; x={self.x}, y={self.y}')
        projectiles = ( element for element in WORLD.elements if isinstance(element, Projectile) )

        for projectile in projectiles:
            # print('Projectile:', projectile)
            if projectile.x < min_x or projectile.x > max_x:
                continue
            if projectile.y < min_y or projectile.y > max_y:
                continue

            print("Enemy hit by projectile")
            self.destroy()
            projectile.destroy()

        pass