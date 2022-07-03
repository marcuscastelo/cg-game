from dataclasses import dataclass, field
import random

from wavefront.face import Face
from wavefront.material import Material
from wavefront.vertex import RawVertex

@dataclass
class Object:
    name: str
    positions_ref: list[tuple]
    texture_coords_ref: list[tuple]
    normals_ref: list[tuple]
    material: Material = field(default_factory=lambda: Material(f'default-{random.random()}'))
    faces: list[Face] = field(default_factory=list)

    def expand_faces_to_unindexed_vertices(self) -> list[RawVertex]:
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
                    position=self.positions_ref[face.position_indices[i]-1],
                    texture_coords=self.texture_coords_ref[face.texture_indices[i]-1],
                    normal=self.normals_ref[face.normal_indices[i]-1]
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
                raise RuntimeError(f'Face has a weird number of vertices: {vertice_count}, expected {FACE_TRIANGLE} or {FACE_QUAD} or {FACE_PENTA} \n\t{face=}')
            

            all_vertices += face_vertices
            face_i += 1

        return all_vertices

@dataclass
class Model:
    name: str = 'Unnamed Model'
    objects: list[Object] = field(default_factory=list)
    positions: list[tuple] = field(default_factory=list)
    texture_coords: list[tuple] = field(default_factory=list)
    normals: list[tuple] = field(default_factory=list)