from ast import arg
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Union
from unittest import mock
import numpy as np
from utils.logger import LOGGER
from wavefront.face import Face
from wavefront.model import Model, Object
from wavefront.material import Material, MtlReader

@dataclass
class ModelReader:
    def __post_init__(self):
        self.object: Object = None
        self.model = Model()
        self.materials: dict[str, Material] = {}
        self.current_material: Union[Material, None] = Material('default') # TODO: change all occurences of Material(something) to a global default

    def load_model_from_file(self, filename: str) -> Model:
        LOGGER.log_trace(f'Loading model {filename}...')
        self.model = Model(filename.split('/')[-1])

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

        VERTEX_COMMAND_RETRIEVER = {
            'v': lambda: self.model.positions,
            'vn': lambda: self.model.normals,
            'vt': lambda: self.model.texture_coords
        }

        # Process vertex data commands (positions, normals and texture coords)
        if command in VERTEX_COMMAND_RETRIEVER:
            vertex_data_list = VERTEX_COMMAND_RETRIEVER[command]()
            vertex_data_list.append(tuple(arguments))
            return

        class FaceDeclType(Enum):
            POS_TEX_NORMAL = auto()
            POS_NORMAL = auto()

        if command == 'o':
            self.object = Object(
                name=' '.join(arguments),
                positions_ref=self.model.positions,
                texture_coords_ref=self.model.texture_coords,
                normals_ref=self.model.normals,
            )
            self.object.material = self.current_material
            LOGGER.log_trace(f'Object name: {self.model.name}', 'Wavefront')
            self.model.objects.append(self.object)

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

                self.object.faces.append(face)

            return

        if command in ('usemtl', 'usemat'):
            assert len(
                arguments) >= 1, f'Command {command} should be followed with material, but found arguments = {arguments}'

            material_name = arguments[0]
            if material_name.lower() == 'none':
                return

            LOGGER.log_warning(f'{line=}')
            material = self.materials[material_name]
                
            self.current_material = material
            self.object.material = material
            return

        if command == 'mtllib':
            filename = arguments[0]
            # TODO: append this files' folder before filename programatically
            try:
                materials = MtlReader(filename=f'models/{filename}').read_materials()
            except Exception as e:
                LOGGER.log_error(f'Failed to import {filename}!\nline: {line}')
                raise e
            else:
                for material_name, material in materials.items():
                    assert material_name not in self.materials, f'Trying to redeclare a material'
                    self.materials[material_name] = material
            return
