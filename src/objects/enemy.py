from objects.element import Element

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
        pass