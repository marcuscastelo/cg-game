from dataclasses import dataclass
import glm

from utils.geometry import Vec3
from gl_abstractions.texture import Texture, Texture2D
from objects.cube import Cube

from wavefront.model_reader import ModelReader

@dataclass
class Sky(Cube):
    ''' Skybox of the world '''
    model = ModelReader().load_model_from_file('models/cube.obj')
    texture: Texture = None
    ray_selectable: bool = False
    ray_destroyable: bool = False

    def __post_init__(self):
        if self.texture is None:
            # Load it after instantiation because Texture2D needs an OpenGL context to be created
            self.texture = Texture2D.from_image_path('textures/sky_wave.png')
        
        super().__post_init__()

    def update(self, delta_time: float):
        ''' Overrides Element method '''

        self._balance_sky_ambient_light()
        
        # Temporarily disable all diffuse lighting, so the sky is not affected by any other lighting (it would look unnatural)
        from app_vars import APP_VARS
        GKd_bkp = APP_VARS.lighting_config.Kd_x, APP_VARS.lighting_config.Kd_y, APP_VARS.lighting_config.Kd_z
        APP_VARS.lighting_config.Kd_x, APP_VARS.lighting_config.Kd_y, APP_VARS.lighting_config.Kd_z = 0, 0, 0

        super().update(delta_time)

        # Restore diffuse lighting
        APP_VARS.lighting_config.Kd_x, APP_VARS.lighting_config.Kd_y, APP_VARS.lighting_config.Kd_z = GKd_bkp

    def _balance_sky_ambient_light(self):
        '''
        Balance the ambient light of the sky.
        This is done by changing the ambient light of the sky based on the ambient light of the sun.
        '''
        # TODO: Sky class that does that
        from app_vars import APP_VARS
        global_Ka = Vec3(APP_VARS.lighting_config.Ka_x, APP_VARS.lighting_config.Ka_y, APP_VARS.lighting_config.Ka_z)
        global_Ka.x = glm.clamp(global_Ka.x, 0, 1)
        global_Ka.y = glm.clamp(global_Ka.y, 0, 1)
        global_Ka.z = glm.clamp(global_Ka.z, 0, 1)
        inv_global_Ka = Vec3(1/(global_Ka.x+0.01), 1/(global_Ka.y+0.01), 1/(global_Ka.z+0.01),) 
        

        # TODO: remove unused method
        # self.shape_specs[0].material.Kd = (inv_global_Ka * global_Ka**2)
        