from dataclasses import dataclass
import math
import time

from utils.geometry import Vec3
from objects.model_element import ModelElement
from wavefront.model import Model
from wavefront.model_reader import ModelReader


FREN_MODEL = ModelReader().load_model_from_file('models/fren.obj')

@dataclass
class Fren(ModelElement):
    ''' 
    A decorative element that represents a fren (Friend). 
    Note: you shouldn't do mean things to your frens, they are your frens.
    '''
    model: Model = FREN_MODEL

    def __post_init__(self):
        self._dying = False # Die animation
        return super().__post_init__()

    def update(self, delta_time: float):
        from app_vars import APP_VARS
        if self._dying: # If you killed the fren, then you shall enter an existencial crisis

            # Wibbly Wobbly Timey Wimey Stuff going on here:
            self.transform.scale.xyz = Vec3(math.sin(time.time()) * self.transform.scale.y,  self.transform.scale.y * ( 1- 0.01 * delta_time * 10) ,math.cos(time.time()) * self.transform.scale.y)
            self.transform.rotation.y = abs(math.sin(time.time() * self.transform.scale.y) * math.pi * 2)
            APP_VARS.camera.fov = self.transform.scale.y * 75
            if self.transform.scale.y < 0.01:
                # After a while of shrinking, actually destroy the fren and overcome the crisis
                APP_VARS.camera.fov = 75
                super().destroy()
                pass
        return super().update(delta_time)

    def destroy(self):
        from app_vars import APP_VARS

        # Only kill the fren if it's close enough to the player (avoid accidental kills)
        if (APP_VARS.camera.center - self.center).magnitude() > 6:
            return

        print('Destroy FREENNN!')
        self._dying = True