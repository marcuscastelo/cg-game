import numpy as np
from OpenGL import GL as gl 
from utils.geometry import Vec3
from gl_abstractions.shader import ShaderDB
from objects.element import Element, ElementSpecification, ShapeSpec
from utils.sig import metsig

from transform import Transform

class Cube(Element):
    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        specification = ElementSpecification (
            initial_transform=Transform (
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(1, 1, 1),
            ),
            shape_specs=[
                # TODO: read from Wavefront file
                ShapeSpec(vertices=np.array([
                    ### CUBO 1
                    # Face 1 do Cubo 1 (vértices do quadrado)
                    (-0.2, -0.2, +0.2),
                    (+0.2, -0.2, +0.2),
                    (-0.2, +0.2, +0.2),
                    (+0.2, +0.2, +0.2),

                    # Face 2 do Cubo 1
                    (+0.2, -0.2, +0.2),
                    (+0.2, -0.2, -0.2),         
                    (+0.2, +0.2, +0.2),
                    (+0.2, +0.2, -0.2),
                    
                    # Face 3 do Cubo 1
                    (+0.2, -0.2, -0.2),
                    (-0.2, -0.2, -0.2),            
                    (+0.2, +0.2, -0.2),
                    (-0.2, +0.2, -0.2),

                    # Face 4 do Cubo 1
                    (-0.2, -0.2, -0.2),
                    (-0.2, -0.2, +0.2),         
                    (-0.2, +0.2, -0.2),
                    (-0.2, +0.2, +0.2),

                    # Face 5 do Cubo 1
                    (-0.2, -0.2, -0.2),
                    (+0.2, -0.2, -0.2),         
                    (-0.2, -0.2, +0.2),
                    (+0.2, -0.2, +0.2),
                    
                    # Face 6 do Cubo 1
                    (-0.2, +0.2, +0.2),
                    (+0.2, +0.2, +0.2),           
                    (-0.2, +0.2, -0.2),
                    (+0.2, +0.2, -0.2),

                ], dtype=np.float32),
                shader=ShaderDB.get_instance().get_shader('simple_red'),
                render_mode=gl.GL_TRIANGLE_STRIP,
                name='Cube'
            ),
            ]
        )
        kwargs['specs'] = specification
        super().__init__(*args, **kwargs)