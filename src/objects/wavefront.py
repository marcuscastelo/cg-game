from ast import arguments
from cgitb import text
from dataclasses import dataclass, field
from enum import Enum, auto
from multiprocessing.dummy import current_process
from operator import le
import os
from xml.etree.ElementTree import Comment
from glm import pos

from utils.logger import LOGGER


@dataclass
class Face:
    position_indices: list[int] = field(default_factory=list)
    texture_indices: list[int] = field(default_factory=list)
    normal_indices: list[int] = field(default_factory=list)
    material_index = None

@dataclass
# TODO: convert to numpy
class RawVertex:
    position: list[float]
    texture_coords: list[float]
    normals: list[float]

    def __repr__(self) -> str:
        return f'RawVertex <pos=({self.position}), tex={self.texture_coords}, normals={self.normals}>'

@dataclass
class Model:
    positions: list[tuple] = field(default_factory=list)
    texture_coords: list[tuple] = field(default_factory=list)
    normals: list[tuple] = field(default_factory=list)
    faces: list[Face] = field(default_factory=list)

    def to_unindexed_vertices(self) -> list[RawVertex]:
        LOGGER.log_trace('Converting model to raw vertices list', 'WaveFront - Model')
        raw_vertices: list[RawVertex] = []
        # f = 1
        for face in self.faces:
            # print(f'--- Face {f} ---')
            # print(f'Face: {face}')
            # f+=1

            assert len(face.position_indices) == len(face.texture_indices) == len(face.normal_indices), f'Mismatch between {len(face.position_indices)=}, {len(face.texture_indices)=}, {len(face.normal_indices)=}'

            face_vertices = []
            for vertex_index in range(len(face.position_indices)):
                vertex = RawVertex(
                    position=self.positions[face.position_indices[vertex_index]-1],
                    texture_coords=self.texture_coords[face.texture_indices[vertex_index]-1],
                    normals=self.normals[face.normal_indices[vertex_index]-1]
                )
                raw_vertices.append(vertex)
                face_vertices.append(vertex) # Debug purposes TODO: remove
            # print(f'\t--- Vertices ---')
            # for vertex in face_vertices:
            #     print(f'\t{vertex}')

        LOGGER.log_trace('Model convetted to raw vertices list!', 'WaveFront - Model')
        return raw_vertices

@dataclass
class WaveFrontReader:
    model: Model = field(default_factory=Model)
    current_material: int = None

    # objects: dict = field(default_factory=dict)
    # positions: list = field(default_factory=list)
    # normals: list = field(default_factory=list)
    # texture_coords: list = field(default_factory=list)
    # faces: list[Face] = field(default_factory=list)
    # material = None

    def load_model_from_file(self, filename: str) -> Model:
        self.model = Model()

        with open(filename, 'r') as file:
            for line in file.readlines():
                self._process_line(line)

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

        # Process face declarations
        if command == 'f':
            # To be stored below (TODO: refactor into dataclass?)

            face = Face()

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
