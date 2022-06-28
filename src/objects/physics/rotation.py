import math
from glm import pitch
from utils.geometry import Vec3

def front_to_rotation(front_vec: Vec3, up: Vec3) -> Vec3:
    '''Converts (front, up) to rotation Vec3'''
    yaw, pitch = front_to_yaw_pitch(front_vec, up)

    # return Vec3(
    #     x=
    # )


def yaw_pitch_to_front(yaw: float, pitch: float, normalized: bool = True) -> Vec3:
    '''Pitch: look up or down, Yaw: rotate left-right'''
    front = Vec3(
        math.cos(yaw) * math.cos(pitch),
        math.sin(pitch),
        math.sin(yaw) * math.cos(pitch),
    )

    return front.normalized() if normalized else front

def front_to_yaw_pitch(front: Vec3):
    # TODO: implement (precisa do up?)

    sin_pitch = front.y
    pitch = math.asin(sin_pitch)
    cos_pitch = math.cos(pitch)

    cos_yaw_cos_pitch = front.x
    sin_yaw_cos_pitch = front.z
    # tan_yaw = sin_yaw_cos_pitch/cos_yaw_cos_pitch
    yaw_atan2 = math.atan2(sin_yaw_cos_pitch, cos_yaw_cos_pitch)
    
    return yaw_atan2, pitch

    raise NotImplementedError()

    