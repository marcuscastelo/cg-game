from dataclasses import dataclass
from OpenGL import GL as gl
import numpy as np
from numpy import log

from utils.geometry import Vec2, Vec3
from utils.sig import metsig

from objects.element import Element, ElementSpecification, ShapeSpec
from objects._2d.projectile import Projectile
from transform import Transform
from gl_abstractions.shader import Shader, ShaderDB


@dataclass(init=False)
class Satellite(Element):
    # Basic variables that define the satellite's visible properties
    rotation_speed: float = 0.01


    @metsig(Element.__init__)
    def __init__(self, *args, **kwargs):
        self._render_primitive = gl.GL_TRIANGLES

        # Define color pallete to the object Star
        darker_silver: Vec3 = Vec3(110, 110, 110) / 255
        dark_silver: Vec3 = Vec3(121, 121, 121) / 255
        silver: Vec3 = Vec3(169,169,169) / 255
        light_silver: Vec3 = Vec3(192,192,192) / 255
        lighter_silver: Vec3 = Vec3(211,211,211) / 255
    
        kwargs['specs'] = ElementSpecification(
            initial_transform=Transform(
                translation=Vec3(0, 0, 0),
                rotation=Vec3(0, 0, 0),
                scale=Vec3(1, 1, 1),
            ), # TODO: allow world to set this
            shape_specs=[

                # Circle part of the satellite, summing up to 30 vertices
                ShapeSpec(
                    vertices=np.array([
                        [* ( 4.89084832e-02,  1.03903916e-02,  0.00000000e+00), *(darker_silver), ], 
                        [* ( 4.56815921e-02,  2.03271322e-02,  0.00000000e+00), *(darker_silver),],
                        [* ( 4.04602103e-02,  2.93763764e-02,  0.00000000e+00), *(darker_silver),],
                        [* ( 3.34723070e-02,  3.71430293e-02,  0.00000000e+00), *(darker_silver),],
                        [* ( 2.50229836e-02,  4.32879925e-02,  0.00000000e+00), *(darker_silver),],
                        [* ( 1.54811405e-02,  4.75429744e-02,  0.00000000e+00), *(darker_silver),],
                        [* ( 5.26338024e-03,  4.97221984e-02,  0.00000000e+00), *(darker_silver),],
                        [* (-5.18418336e-03,  4.97305170e-02,  0.00000000e+00), *(dark_silver),],
                        [* (-1.54054016e-02,  4.75675687e-02,  0.00000000e+00), *(dark_silver),],
                        [* (-2.49540098e-02,  4.33277898e-02,  0.00000000e+00), *(dark_silver),],
                        [* (-3.34131084e-02,  3.71962897e-02,  0.00000000e+00), *(dark_silver),],
                        [* (-4.04133722e-02,  2.94407774e-02,  0.00000000e+00), *(dark_silver),],
                        [* (-4.56491597e-02,  2.03998610e-02,  0.00000000e+00), *(dark_silver),],
                        [* (-4.88918722e-02,  1.04682725e-02,  0.00000000e+00), *(dark_silver),],
                        [* (-4.99999374e-02,  7.96326494e-05,  0.00000000e+00), *(dark_silver),],
                        [* (-4.89249714e-02, -1.03124846e-02,  0.00000000e+00), *(silver),],
                        [* (-4.57139052e-02, -2.02543512e-02,  0.00000000e+00), *(silver),],
                        [* (-4.05069441e-02, -2.93118991e-02,  0.00000000e+00), *(silver),],
                        [* (-3.35314199e-02, -3.70896719e-02,  0.00000000e+00), *(silver),],
                        [* (-2.50918958e-02, -4.32480834e-02,  0.00000000e+00), *(silver),],
                        [* (-1.55568402e-02, -4.75182571e-02,  0.00000000e+00), *(silver),],
                        [* (-5.34256361e-03, -4.97137494e-02,  0.00000000e+00), *(silver),],
                        [* ( 5.10497298e-03, -4.97387089e-02,  0.00000000e+00), *(silver),],
                        [* ( 1.53296236e-02, -4.75920439e-02,  0.00000000e+00), *(light_silver),],
                        [* ( 2.48849727e-02, -4.33674790e-02,  0.00000000e+00), *(light_silver),],
                        [* ( 3.33538279e-02, -3.72494608e-02,  0.00000000e+00), *(light_silver),],
                        [* ( 4.03664298e-02, -2.95051057e-02,  0.00000000e+00), *(light_silver),],
                        [* ( 4.56166118e-02, -2.04725377e-02,  0.00000000e+00), *(light_silver),],
                        [* ( 4.88751382e-02, -1.05461273e-02,  0.00000000e+00), *(light_silver),],
                        [* ( 4.99997474e-02, -1.59265095e-04,  0.00000000e+00), *(light_silver),],
                        [* ( 4.89084832e-02,  1.03903916e-02,  0.00000000e+00), *(darker_silver), ],
                    ], dtype=np.float32),
                    shader=ShaderDB.get_instance().get_shader('colored'),
                    render_mode=gl.GL_TRIANGLE_FAN,
                ), 

                # "Square" parts of the satellite
                ShapeSpec(
                    vertices=np.array([
                        [*(-0.051, 0.01, 0.0),        *(0.290, 0.290, 0.290)],
                        [*(-0.08, -0.01, 0.0),       *(0.290, 0.290, 0.290)],
                        [*(-0.08, 0.01, 0.0),        *(0.290, 0.290, 0.290)],

                        [*(-0.08, -0.01, 0.0),       *(0.290, 0.290, 0.290)],
                        [*(-0.051, 0.01, 0.0),        *(0.290, 0.290, 0.290)],
                        [*(-0.051, -0.01, 0.0),       *(0.290, 0.290, 0.290)],
             
                        [*(-0.08, 0.02, 0.0),        *(0.588, 0.588, 0.588)],
                        [*(-0.1, -0.02, 0.0),        *(0.588, 0.588, 0.588)],
                        [*(-0.1, 0.02, 0.0),         *(0.588, 0.588, 0.588)],
             
                        [*(-0.08, 0.02, 0.0),        *(0.588, 0.588, 0.588)],
                        [*(-0.08, -0.02, 0.0),       *(0.588, 0.588, 0.588)],
                        [*(-0.1, -0.02, 0.0),        *(0.588, 0.588, 0.588)],

                        ##

                        [*(0.051, 0.01, 0.0),     *(0.290, 0.290, 0.290)],
                        [*(0.08, -0.01, 0.0),    *(0.290, 0.290, 0.290)],
                        [*(0.08, 0.01, 0.0),     *(0.290, 0.290, 0.290)],
            
                        [*(0.08, -0.01, 0.0),    *(0.290, 0.290, 0.290)],
                        [*(0.051, 0.01, 0.0),     *(0.290, 0.290, 0.290)],
                        [*(0.051, -0.01, 0.0),    *(0.290, 0.290, 0.290)],
            
                        [*(0.08, 0.02, 0.0),     *(0.588, 0.588, 0.588)],
                        [*(0.1, -0.02, 0.0),     *(0.588, 0.588, 0.588)],
                        [*(0.1, 0.02, 0.0),      *(0.588, 0.588, 0.588)],
            
                        [*(0.08, 0.02, 0.0),     *(0.588, 0.588, 0.588)],
                        [*(0.08, -0.02, 0.0),     *(0.588, 0.588, 0.588)],
                        [*(0.1, -0.02, 0.0),     *(0.588, 0.588, 0.588)],
                     
                    ], dtype=np.float32),
                    render_mode=gl.GL_TRIANGLES,
                     shader=ShaderDB.get_instance().get_shader('colored'),
                )
            ]
        )

        super().__init__(*args, **kwargs)

    def _generate_bounding_box_2d_vertices(self) -> np.ndarray:
        circle_verts = self.shape_renderers[0].shape_spec.vertices[:, :2]
        stuff_verts = self.shape_renderers[1].shape_spec.vertices[:, :2]

        circle_min_x = np.min(circle_verts[:, 0])
        circle_max_x = np.max(circle_verts[:, 0])
        circle_min_y = np.min(circle_verts[:, 1])
        circle_max_y = np.max(circle_verts[:, 1])

        stuff_min_x = np.min(stuff_verts[:, 0])
        stuff_max_x = np.max(stuff_verts[:, 0])
        stuff_min_y = np.min(stuff_verts[:, 1])
        stuff_max_y = np.max(stuff_verts[:, 1])

        min_x = min(circle_min_x, stuff_min_x)
        max_x = max(circle_max_x, stuff_max_x)

        min_y = min(circle_min_y, stuff_min_y)
        max_y = max(circle_max_y, stuff_max_y)

        return np.array([
            [*(min_x, min_y, 0.0)],
            [*(max_x, min_y, 0.0)],
            [*(max_x, max_y, 0.0)],
            [*(min_x, max_y, 0.0)],
        ], dtype=np.float32)
        




    def _physics_update(self, delta_time: float):
        self.transform.rotation.z += self.rotation_speed

        # bbox = self.get_bounding_box_2d()
        # for projectile in (element for element in self.world.elements if isinstance(element, Projectile)):
        #     if not projectile.is_particle and bbox.contains(projectile.transform.translation.xy):
        #         projectile.destroy()

        super()._physics_update(delta_time)
