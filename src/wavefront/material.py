# TODO: reader mtllib

from ast import arg
from dataclasses import dataclass, field
#https://en.wikipedia.org/wiki/Wavefront_.obj_file#Basic_materials
from enum import Enum
from modulefinder import LOAD_CONST
from typing import Union

from utils.geometry import Vec2, Vec3, VecN
from utils.logger import LOGGER

class Illum(Enum):
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

    # Also bump instead of map_bump
    map_bump: Union[str, None] = None

    disp: Union[str, None] = None
    decal: Union[str, None] = None


class MtlReader:
    def __init__(self, filename: str) -> None:
        self.last_declared_material_name = None
        self.materials: dict[str, Material] = {}
        self.filename = filename
    @property
    def current_material(self):
        return self.materials[self.last_declared_material_name]

    def read_materials(self) -> dict[str, Material]:
        with open(self.filename, 'r') as f:
            for line in f.readlines():
                self._process_line(line)

        return self.materials

    def _process_line(self, line: str) -> None:
        if line.startswith('#'):
            return

        # Split on spaces to a list of values
        values = line.split()
        
        # Ignore empty lines
        if not values:
            return

        command, *arguments = values
        
        if command == 'newmtl':
            material_name = ' '.join(arguments)
            newmtl = Material(name=material_name)
            self.materials[material_name] = newmtl
            self.last_declared_material_name = material_name
            return


        ASSIGN_COMMANDS = [ 'Ns', 'Ka', 'Kd', 'Ks', 'Ke', 'Ni', 'd', 'illum', 'Tf', 'map_Ka', 'map_Kd', 'map_Ks', 'map_Ns', 'map_d', 'map_bump', 'disp', 'decal']
        if command not in ASSIGN_COMMANDS:
            LOGGER.log_error(f'Unknown command "{command}" at line "{line}" in file {self.filename}, ignoring', 'MtlReader')
            return

        if len(arguments) == 1: # float
            attribute_value = float(arguments[0])
        elif len(arguments) == 2: # Vec2
            attribute_value = Vec2(float(arguments[0]), float(arguments[1]))
        elif len(arguments) == 3: # Vec3
            attribute_value = Vec3(float(arguments[0]), float(arguments[1]), float(arguments[2]))
        else: # VecN
            attribute_value = VecN(*list(map(float, arguments)))

        setattr(self.current_material, command, attribute_value)