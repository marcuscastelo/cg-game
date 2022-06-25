from dataclasses import dataclass


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

