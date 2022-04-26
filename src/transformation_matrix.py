from dataclasses import dataclass
import numpy as np

from utils.geometry import Vec3, VecN

@dataclass
class MatrixCache:
    translation_matrix: np.ndarray = None
    rotation_matrix: np.ndarray = None
    scale_matrix: np.ndarray = None
    model_matrix: np.ndarray = None

    last_translation: Vec3 = None
    last_rotation: Vec3 = None
    last_scale: Vec3 = None

@dataclass
class Transform:
    translation: Vec3 = Vec3(0, 0, 0)
    rotation: Vec3 = Vec3(0, 0, 0)
    scale: Vec3 = Vec3(1, 1, 1)

    ### Enforce Types ###

    def __post_init__(self):
        self.translation = Vec3(self.translation)
        self.rotation = Vec3(self.rotation)
        self.scale = Vec3(self.scale)
        self._matrix_cache = MatrixCache()

    @property
    def model_matrix(self):
        return self.calc_model_matrix() # Cached if none of the properties are changed

    ### Matrix calculation ###

    def calc_model_matrix(self) -> np.ndarray:
        # Scale
        scale_cache_valid = self._matrix_cache.last_scale == self.scale
        if not scale_cache_valid:
            diag = VecN([*self.scale, 1])
            scale_matrix = np.diag(diag.values)
            self._matrix_cache.scale_matrix = scale_matrix
            self._matrix_cache.last_scale = Vec3(self.scale)
        
        scale_matrix = self._matrix_cache.scale_matrix

        # Rotation
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

            rotation_matrix = x_rotation_matrix @ y_rotation_matrix @ z_rotation_matrix
            self._matrix_cache.rotation_matrix = rotation_matrix
            self._matrix_cache.last_rotation = Vec3(self.rotation)
            
        rotation_matrix = self._matrix_cache.rotation_matrix
            
        # Translation
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

        if scale_cache_valid and rotation_cache_valid and translation_cache_valid:
            model_matrix = self._matrix_cache.model_matrix

        else:
            model_matrix = translation_matrix @ rotation_matrix @ scale_matrix
            self._matrix_cache.model_matrix = model_matrix

        return model_matrix