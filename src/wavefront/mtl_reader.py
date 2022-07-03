from utils.geometry import Vec2, Vec3, VecN
from utils.logger import LOGGER

from wavefront.material import Material


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