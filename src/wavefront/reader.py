from ast import arg
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
from utils.logger import LOGGER
from wavefront.face import Face
from wavefront.model import Model
from wavefront.material import Material, MtlReader

@dataclass
class ModelReader:
    model: Model = field(default_factory=Model)
    materials: list[Material] = field(default_factory=list)
    current_material: int = None

    def load_model_from_file(self, filename: str) -> Model:
        LOGGER.log_trace(f'Loading model {filename}...')
        self.model = Model()

        with open(filename, 'r') as file:
            for line in file.readlines():
                self._process_line(line)

        LOGGER.log_trace(f'Model {filename} Loaded!')
        return self.model

    def _process_line(self, line: str) -> None:
        # Ignore comment lines
        # (TODO: are there comments after the first character?)
        if line.startswith('#'):
            return

        # Split on spaces to a list of values
        values = line.split()

        # Ignore empty lines
        if not values:
            return

        command, *arguments = values

        VERTEX_COMMANDS = {
            'v': self.model.positions,
            'vn': self.model.normals,
            'vt': self.model.texture_coords
        }

        # Process vertex data commands (positions, normals and texture coords)
        if command in VERTEX_COMMANDS:
            vertex_data_list = VERTEX_COMMANDS[command]
            vertex_data_list.append(tuple(arguments))
            return

        class FaceDeclType(Enum):
            POS_TEX_NORMAL = auto()
            POS_NORMAL = auto()

        if command == 'o':
            self.model.name = ' '.join(arguments)
            LOGGER.log_trace(f'Object name: {self.model.name}', 'Wavefront')

        # Process face declarations
        if command == 'f':
            # To be stored below (TODO: refactor into dataclass?)

            face = Face()

            vertex_count = len(arguments)
            if vertex_count > 5:
                LOGGER.log_warning(f'Face has {vertex_count} vertices')
                LOGGER.log_trace(f'Face vertices: {arguments}')

            # A face is declared as a list of items separated by spaces
            # Each item is in the form '<pos>/<tex>/<normal>'
            # Ex.: 'f 1/1/1 2/2/1 3/3/1'
            for item in arguments:
                # Determine type of line
                values = item.split('/')
                values = [int(v) for v in values if v != '']

                if len(values) > 2:
                    decl_type = FaceDeclType.POS_TEX_NORMAL
                elif len(values) == 2:
                    # In this case, Texture was omitted in the .obj file
                    decl_type = FaceDeclType.POS_NORMAL
                else:
                    LOGGER.log_error(f'Unexpected format for line: {line}')
                    raise RuntimeError(f"Couldn't read line {line}")

                if decl_type == FaceDeclType.POS_TEX_NORMAL:
                    position, texture, normal = values
                elif decl_type == FaceDeclType.POS_NORMAL:
                    position, normal = values
                    texture = 0

                face.position_indices.append(position)
                face.normal_indices.append(normal)
                face.texture_indices.append(texture)
                face.material_index = self.current_material

                if self.current_material is None:
                    LOGGER.log_warning(f'Assigning "None" as material for line {line}, since no material is bound')

                self.model.faces.append(face)

            return

        if command in ('usemtl', 'usemat'):
            assert len(
                arguments) >= 1, f'Command {command} should be followed with material, but found arguments = {arguments}'
            self.current_material = arguments[0]

        if command == 'mtllib':
            filename = arguments[0]
            # TODO: append this files' folder before filename programatically
            try:
                materials = MtlReader(filename=f'models/{filename}').read_materials()
            except Exception as e:
                LOGGER.log_error(f'Failed to import {filename}!\nline: {line}')
                raise e
            self.materials += materials
