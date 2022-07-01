from dataclasses import dataclass, field
import numpy as np

from utils.geometry import Vec3, VecN

@dataclass
class MatrixCache:
    ''' A cache for the transformation matrices. '''
    # Cache for the transformation matrices.
    translation_matrix: np.ndarray = None
    rotation_matrix: np.ndarray = None
    scale_matrix: np.ndarray = None
    model_matrix: np.ndarray = None

    # Store transformation parameters for each cache, i.e. translation, rotation, scale.
    # if some of them have been changed, the corresponding matrix cache is not valid anymore.
    last_translation: Vec3 = None
    last_rotation: Vec3 = None
    last_scale: Vec3 = None

    # TODO: CachedMatrix[Vec3] object = tuple[Vec3, np.ndarray] instead of 2 fields for each matrix

@dataclass
class Transform:
    ''' The translation, rotation, and scale of the object. '''
    translation: Vec3 = field(default_factory=lambda: Vec3(0, 0, 0))
    rotation: Vec3 = field(default_factory=lambda: Vec3(0, 0, 0))
    scale: Vec3 = field(default_factory=lambda: Vec3(1, 1, 1))


    def __post_init__(self):
        # Enforce Types
        self.translation.xyz = Vec3(self.translation)
        self.rotation.xyz = Vec3(self.rotation)
        self.scale.xyz = Vec3(self.scale)
        self._matrix_cache = MatrixCache()

    @property
    def model_matrix(self):
        ''' Get the model matrix. '''
        return self.calc_model_matrix() # Cached if none of the properties are changed

    def calc_model_matrix(self) -> np.ndarray:
        ''' Calculate the model matrix. '''

        # 1. Scale
        scale_cache_valid = self._matrix_cache.last_scale == self.scale
        if not scale_cache_valid:
            diag = VecN([*self.scale, 1])
            scale_matrix = np.diag(diag.values)
            self._matrix_cache.scale_matrix = scale_matrix
            self._matrix_cache.last_scale = Vec3(self.scale)
        
        scale_matrix = self._matrix_cache.scale_matrix

        # 2. Rotation
        rotation_cache_valid = self._matrix_cache.last_rotation == self.rotation
        if not rotation_cache_valid:
            rx, ry, rz = self.rotation
            x_rotation_matrix = np.array([
                [1, 0, 0, 0],
                [0, np.cos(rx), -np.sin(rx), 0],
                [0, np.sin(rx), np.cos(rx), 0],
                [0, 0, 0, 1]
            ])

            y_rotation_matrix = np.array([
                [np.cos(ry), 0, np.sin(ry), 0],
                [0, 1, 0, 0],
                [-np.sin(ry), 0, np.cos(ry), 0],
                [0, 0, 0, 1]
            ])

            z_rotation_matrix = np.array([
                [np.cos(rz), -np.sin(rz), 0, 0],
                [np.sin(rz), np.cos(rz), 0, 0],
                [0, 0, 1, 0],
                [0, 0, 0, 1]
            ])


            # TODO: Understand how the order of the rotations matters
            rotation_matrix = x_rotation_matrix @ z_rotation_matrix @ y_rotation_matrix
            self._matrix_cache.rotation_matrix = rotation_matrix
            self._matrix_cache.last_rotation = Vec3(self.rotation)
            
        rotation_matrix = self._matrix_cache.rotation_matrix
            
        # 3. Translation
        translation_cache_valid = self._matrix_cache.last_translation == self.translation
        if not translation_cache_valid:
            x, y, z = self.translation
            translation_matrix = np.array([
                [1, 0, 0, x],
                [0, 1, 0, y],
                [0, 0, 1, z],
                [0, 0, 0, 1]
            ])
            self._matrix_cache.translation_matrix = translation_matrix
            self._matrix_cache.last_translation = Vec3(self.translation)
        
        translation_matrix = self._matrix_cache.translation_matrix

        # 4. Check if cache is valid for model matrix
        if scale_cache_valid and rotation_cache_valid and translation_cache_valid:
            # Cache is valid, return cached model matrix
            model_matrix = self._matrix_cache.model_matrix
        else:
            # Cache is not valid, calculate model matrix
            # and cache it
            model_matrix = translation_matrix @ rotation_matrix @ scale_matrix
            self._matrix_cache.model_matrix = model_matrix

        return model_matrix