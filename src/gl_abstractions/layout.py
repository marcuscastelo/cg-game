import ctypes
from dataclasses import dataclass

import numpy as np
from utils.logger import LOGGER

from constants import FLOAT_SIZE
    
@dataclass
class Layout:
    '''
    Class responsible for describing the layout of the vertex array (each geometry object is a vertex array).
    Currently only supports floats.
    '''
    attributes: list[tuple[str, int]] # Example: [('position', 3), ('tex_coord', '2')]

    def __post_init__(self):
        '''
        Type checking.
        '''
        for name, count in self.attributes:
            if not isinstance(name, str):
                raise TypeError(f'Attribute name must be a string, got {type(name)}')
            if not isinstance(count, int):
                raise TypeError(f'Attribute count must be an integer, got {type(count)}')

    def assert_data_ok(self, data: np.ndarray) -> bool:
        '''
        Checks if the data is compatible with the layout.
        '''
        # LOGGER.log_trace(f'Checking data compatibility with layout: {self}')

        SUPPORTED_DTYPES = [np.float32, np.float64]

        assert isinstance(data, np.ndarray), f'Only numpy arrays are supported, got {type(data)}'
        assert data.dtype in SUPPORTED_DTYPES, f'Only {SUPPORTED_DTYPES=} data types are supported, got {data.dtype}'
        assert len(data.shape) == 2, f'Data must be 2D (series of attributes), got {len(data.shape)}D'
        assert data.shape[1] * FLOAT_SIZE == self.calc_stride(), f'Data must have a stride of {self.calc_stride()}, got {data.shape[1]}'

        # In case it has been sent with other types such as float64
        data = data.astype(np.float32) 

        for vertex in range(data.shape[0]):
            offset = 0
            for name, count in self.attributes:
                vertex_attrib_values = data[vertex, offset:offset+count]

                # print(f'{name}: {vertex_attrib_values}')
                assert len(vertex_attrib_values.shape) == 1, f'Attribute values must be 1D, got {len(vertex_attrib_values.shape)}D'
                assert vertex_attrib_values.shape[0] == count, f'Attribute values must have a length of {count}, got {vertex_attrib_values.shape[0]}'

                offset += count

        return True

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

    def __repr__(self) -> str:
        return f'Layout(attributes={self.attributes})'