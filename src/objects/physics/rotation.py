import math
from typing import NamedTuple
from glm import pitch
import glm
from utils.geometry import Vec3

def front_to_rotation(front_vec: Vec3) -> Vec3:
    '''Converts (front, up) to rotation Vec3'''
    assert isinstance(front_vec, Vec3)
    yaw, pitch = front_to_yaw_pitch(front_vec)
    pitch_x = -pitch * (glm.cos(-math.pi/2+yaw))
    pitch_z = -pitch * (glm.sin(-math.pi/2+yaw))

    return Vec3(pitch_x, math.pi/2-yaw, pitch_z)


def yaw_pitch_to_front(yaw: float, pitch: float, normalized: bool = True) -> Vec3:
    '''Pitch: look up or down, Yaw: rotate left-right'''
    front = Vec3(
        math.cos(yaw) * math.cos(pitch),
        math.sin(pitch),
        math.sin(yaw) * math.cos(pitch),
    )

    return front.normalized() if normalized else front

YawPitchTuple = NamedTuple('YawPitchTuple', [('yaw', float), ('pitch', float)])
def front_to_yaw_pitch(front: Vec3) -> YawPitchTuple:
    '''Converts front vector to (yaw, pitch) tuple'''
    front = front.normalized()

    sin_pitch = front.y
    pitch = math.asin(sin_pitch)

    cos_yaw_cos_pitch = front.x
    sin_yaw_cos_pitch = front.z
    yaw_atan2 = math.atan2(sin_yaw_cos_pitch, cos_yaw_cos_pitch)
    
    return yaw_atan2, pitch

    