# TODO: reader mtllib

from dataclasses import dataclass, field
from enum import Enum
from typing import Union

from utils.geometry import Vec3

'''
This file contains all properties of a material.
As specified in: https://en.wikipedia.org/wiki/Wavefront_.obj_file#Basic_materials
'''

class Illum(Enum):
    ''' Types of illumination '''
    COLOR_ON_AMBIENT_OFF = 0
    COLOR_ON_AMBIENT_ON = 1
    HIGHLIGHT_ON = 2
    REFLECTION_ON_RAYTRACE_ON = 3
    TRANSPARENCY_GLASS_ON_REFLECTION_RAYTRACE_ON = 4
    REFLECTION_FRESNEL_RAYTRACE_ON = 5
    TRANSPARENCY_REFRACTION_ON_REFLECTION_FRESNEL_OFF_RAY_TRACE_ON = 6
    REFLECTION_ON_RAY_TRACE_OFF = 8
    TRANSPARENCY_GLASS_ON_REFLECTION_RAYTRACE_OFF = 9
    CASTS_SHADOWS_ONTO_INVISIBLE_SURFACES = 10

@dataclass
class Material:
    ''' Properties of a material '''
    name: str
    Ns: float = 1000
    Ka: Vec3 = field(default_factory=lambda: Vec3(1,1,1))
    Kd: Vec3 = field(default_factory=lambda: Vec3(1,1,1))
    Ks: Vec3 = field(default_factory=lambda: Vec3(1,1,1))
    Ke: Vec3 = field(default_factory=lambda: Vec3(1,1,1))
    Ni: float = 1000
    d: float = 1.0 # Also Tr
    illum: Illum = Illum.REFLECTION_ON_RAYTRACE_ON
    Tf: Union[Vec3, None] = None
    map_Ka: Union[str, None] = None
    map_Kd: Union[str, None] = None
    map_Ks: Union[str, None] = None
    map_Ns: Union[str, None] = None
    map_d: Union[str, None] = None

    # TODO: Also bump instead of map_bump
    map_bump: Union[str, None] = None

    disp: Union[str, None] = None
    decal: Union[str, None] = None
