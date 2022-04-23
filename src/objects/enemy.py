from objects.element import Element

class Enemy(Element):
    def _init_vertices(self):
        self._vertices = [
            (-0.1,  +0,1)
            (-0.1,  -0.1)
            (+0.1,  -0.1)
        ]
    
    