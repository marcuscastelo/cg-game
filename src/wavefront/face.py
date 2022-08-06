from dataclasses import dataclass, field

@dataclass
class Face:
    position_indices: list[int] = field(default_factory=list)
    texture_indices: list[int] = field(default_factory=list)
    normal_indices: list[int] = field(default_factory=list)
