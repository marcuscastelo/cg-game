import ctypes
from dataclasses import dataclass

@dataclass
class Layout:
    '''
    Class responsible for describing the layout of the vertex array (each geometry object is a vertex array).
    Currently only supports floats.
    '''
    attributes: tuple[str, float] # Example: [('position', 3), ('tex_coord', '2')]

    def calc_stride(self) -> int:
        '''
        Calculates the stride of the vertex array.
        '''
        stride = 0
        for name, count in self.attributes:
            stride += count * ctypes.sizeof(ctypes.c_float)

        return stride

    def get_offset(self, name: str) -> int:
        '''
        Returns the offset of the attribute with the given name.
        '''
        offset = 0
        for name_, count in self.attributes:
            if name == name_:
                return ctypes.cast(offset, ctypes.c_void_p)
            offset += count * ctypes.sizeof(ctypes.c_float)

        return ctypes.cast(offset, ctypes.c_void_p)