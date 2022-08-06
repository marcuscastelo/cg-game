from dataclasses import dataclass
from enum import Enum, auto
import random
from typing import Union
from utils.logger import LOGGER
from wavefront.face import Face
from wavefront.model import Model, Object
from wavefront.material import Material
from wavefront.mtl_reader import MtlReader

@dataclass
class ModelReader:
    ''' A Wavefront .obj reader 
    Usage:
        reader = ModelReader()
        model = reader.load_model_from_file('models/cube.obj')
    '''
    # TODO: make it be ModelReader(filename: str).load_model()

    def __post_init__(self):
        self.model = Model() # Creates an empty model to be filled in later
        self.materials: dict[str, Material] = {} # Maps material names to materials
        self.current_object: Object = None
        self.current_material: Union[Material, None] = Material(f'default-{random.random()}') # TODO: change all occurences of Material(something) to a global default

    def load_model_from_file(self, filename: str) -> Model:
        ''' Loads a model from a .obj file '''

        LOGGER.log_trace(f'Loading model {filename}...')
        self.model = Model(filename.split('/')[-1])

        with open(filename, 'r') as file:
            for line in file.readlines():
                self._process_line(line)

        LOGGER.log_trace(f'Model {filename} Loaded!')
        return self.model

    def _process_line(self, line: str) -> None:
        ''' Internal function for processing a line from a .obj file (changes the state of self) '''
        # Ignore comment lines
        if line.startswith('#'):
            return

        # Split on spaces to a list of values
        values = line.split()

        # Ignore empty lines
        if not values:
            return

        # Example: v 1.0 2.0 3.0
        # command = 'v'
        # arguments = [1.0, 2.0, 3.0]
        command, *arguments = values

        VERTEX_COMMANDS_TO_LIST = {
            'v': self.model.positions,          # Vertex position
            'vn': self.model.normals,           # Vertex normal
            'vt': self.model.texture_coords     # Vertex texture coordinate
        }

        # Process vertex data commands (positions, normals and texture coords)
        if command in VERTEX_COMMANDS_TO_LIST:
            vertex_data_list = VERTEX_COMMANDS_TO_LIST[command]
            vertex_data_list.append(tuple(map(float, arguments)))
            return


        # Process object/group commands
        if command in ['o', 'g']:
            self.current_object = Object(
                name=' '.join(arguments),
                positions_ref=self.model.positions,
                texture_coords_ref=self.model.texture_coords,
                normals_ref=self.model.normals,
            )
            self.current_object.material = self.current_material
            LOGGER.log_trace(f'Object name: {self.current_object.name}', 'Wavefront')
            self.model.objects.append(self.current_object)

            return


        # Process face declarations
        if command == 'f':
            # A face is declared as a list of items separated by spaces
            # Each item is in the form '<pos>/<tex>/<normal>'
            # Ex.: 'f 1/1/1 2/2/1 3/3/1'
            face = Face()

            vertex_count = len(arguments)
            if vertex_count > 5:
                LOGGER.log_warning(f'Face has {vertex_count} vertices')
                # LOGGER.log_trace(f'Face vertices: {arguments}')

            class FaceDeclType(Enum):
                ''' It is possible to have a .obj that omits the texture coordinates in the face declaration.
                Example: f 1//1 2//2 3//3'''
                POS_TEX_NORMAL = auto()
                POS_NORMAL = auto()

            # Process face declarations
            for item in arguments:
                values = item.split('/')
                values = [int(v) for v in values if v != '']

                # Determine type of line
                if len(values) == 3:
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
                    texture = 0 # Random texture coordinate (it's not used anyway)
                else:
                    raise RuntimeError(f"Couldn't read line {line}, face decl_type: {decl_type}")

                face.position_indices.append(position)
                face.normal_indices.append(normal)
                face.texture_indices.append(texture)

                self.current_object.faces.append(face)

            return

        # Process material commands (ex.: 'usemtl material_name')
        if command in ('usemtl', 'usemat'):
            assert len(
                arguments) >= 1, f'Command {command} should be followed with material, but found arguments = {arguments}'

            material_name = arguments[0]
            if material_name.lower() == 'none':
                # Generate a new unique material name to avoid conflicts between models
                material = Material(f'default-{random.random()}') 
            else:
                # Use previously loaded material (from .mtl file in mtllib command)
                material = self.materials[material_name]
                
            self.current_material = material
            self.current_object.material = material
            return

        # Process material library commands (ex.: 'mtllib material_library.mtl')
        if command == 'mtllib':
            filename = arguments[0]
            MATERIAL_FOLDER = 'models'
            try:
                materials = MtlReader(filename=f'{MATERIAL_FOLDER}/{filename}').read_materials()
            except Exception as e:
                LOGGER.log_error(f'Failed to import {filename}!\nline: {line}')
                raise e
            else:
                for material_name, material in materials.items():
                    assert material_name not in self.materials, f'Trying to redeclare a material'
                    self.materials[material_name] = material
            return
