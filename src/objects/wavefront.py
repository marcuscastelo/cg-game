from ast import arg
from dataclasses import dataclass, field
from enum import Enum, auto
import numpy as np
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
    normal: list[float]

    def __repr__(self) -> str:
        return f'RawVertex <pos=({self.position}), tex={self.texture_coords}, normals={self.normal}>'

    def to_tuple(self, with_position: bool, with_texture_coords: bool, with_normals: bool) -> tuple:
        return (
            * (self.position if with_position else []),
            * (self.texture_coords if with_texture_coords else []),
            * (self.normal if with_normals else []),
        )

@dataclass
class Model:
    name: str = 'Unnamed Model'
    positions: list[tuple] = field(default_factory=list)
    texture_coords: list[tuple] = field(default_factory=list)
    normals: list[tuple] = field(default_factory=list)
    faces: list[Face] = field(default_factory=list)

    def to_unindexed_vertices(self) -> list[RawVertex]:
        all_vertices: list[RawVertex] = []

        FACE_PENTA = 5
        FACE_QUAD = 4
        FACE_TRIANGLE = 3

        face_i = 1
        for face in self.faces:
            assert len(face.position_indices) == len(face.texture_indices) == len(face.normal_indices), f'Mismatch between {len(face.position_indices)=}, {len(face.texture_indices)=}, {len(face.normal_indices)=}'
            vertice_count = len(face.position_indices)
 
            indices = face.position_indices 
            # print(f'Face {face_i} indices: \n {indices=}')
            face_vertices = [
                RawVertex(
                    position=self.positions[face.position_indices[i]-1],
                    texture_coords=self.texture_coords[face.texture_indices[i]-1],
                    normal=self.normals[face.normal_indices[i]-1]
                ) for i in range(len(indices))
            ]

            if vertice_count == FACE_PENTA:
                q1s, q2s, q3s, q4s, q5s = [ face_vertices[i::5] for i in range(0,5) ]
                lens = list(map(len, [q1s, q2s, q3s, q4s, q5s]))
                assert min(lens) == max(lens), f'Division face_vertices[::5] has returned incosistent sized lists! (This face is probably not a quad)'

                face_vertices.clear()
                for i in range(len(q1s)):
                    face_vertices += [q1s[i],q2s[i],q3s[i],q3s[i],q4s[i],q5s[i],q5s[i],q1s[i],q3s[i]]
            elif vertice_count == FACE_QUAD:
                q1s, q2s, q3s, q4s = [ face_vertices[i::4] for i in range(0,4) ]
                lens = list(map(len, [q1s, q2s, q3s, q4s]))
                assert min(lens) == max(lens), f'Division face_vertices[::4] has returned incosistent sized lists! (This face is probably not a quad)'

                face_vertices.clear()
                for i in range(len(q1s)):
                    face_vertices += [q1s[i], q2s[i], q3s[i], q3s[i], q4s[i], q1s[i]]

            elif vertice_count == FACE_TRIANGLE:
                pass
            else:
                raise RuntimeError(f'Face has a weird number of vertices: {vertice_count}, expected {FACE_TRIANGLE} or {FACE_QUAD}\n\t{face=}')
            

            # print(f'Face {face_i} vertices: \n {face_vertices=}')
            all_vertices += face_vertices
            face_i += 1

        # # LOGGER.log_trace('Model convetted to raw vertices list!', 'WaveFront - Model')
        assert face_vertices
        # print(f'All vertices:\n {face_vertices=}')
        return all_vertices

@dataclass
class WaveFrontReader:
    model: Model = field(default_factory=Model)
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
            if vertex_count > 4:
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
