from dataclasses import dataclass
import numpy as np

from utils.geometry import Vec3, Vec2, VecN
from utils.logger import LOGGER

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

@dataclass
class MVPManager:
    mvp: np.ndarray = np.eye(4, dtype=np.float32)
    _scale: float = 1.0
    _rotation_angle: float = 0.0
    _translation_x: float = 0.0 
    _translation_y: float = 0.0

    _translation_mat = np.eye(4, dtype=np.float32)
    _rotation_mat = np.eye(4, dtype=np.float32)
    _scale_mat = np.eye(4, dtype=np.float32)

    def _on_scale_changed(self):
        # Recalculate MVP
        self._scale_mat = np.diag([self._scale, self._scale, 1, 1.0])
        self._update_mvp()
        pass

    def _on_translation_changed(self):
        # Recalculate MVP
        self._translation_mat = np.eye(4, dtype=np.float32)
        self._translation_mat[0, 3] = self._translation_x
        self._translation_mat[1, 3] = self._translation_y
        self._update_mvp()
        pass

    def _on_rotation_changed(self):
        # Recalculate MVP
        self._rotation_mat = np.eye(4, dtype=np.float32)
        self._rotation_mat[0, 0] = np.cos(self._rotation_angle)
        self._rotation_mat[0, 1] = -np.sin(self._rotation_angle)
        self._rotation_mat[1, 0] = np.sin(self._rotation_angle)
        self._rotation_mat[1, 1] = np.cos(self._rotation_angle)

        self._update_mvp()
        pass

    def isometric_view(self):
        # Recalculate MVP
        self._rotation_mat = np.eye(4, dtype=np.float32)
        # self._rotation_mat[0, 0] = np.cos(self._rotation_angle)
        # self._rotation_mat[0, 1] = -np.sin(self._rotation_angle)
        # self._rotation_mat[1, 0] = np.sin(self._rotation_angle)
        # self._rotation_mat[1, 1] = np.cos(self._rotation_angle)

        ISOMETRIC_ANGLE = np.radians(-45)
        x_rot_mat = np.eye(4, dtype=np.float32)
        x_rot_mat[1, 1] = np.cos(ISOMETRIC_ANGLE)
        x_rot_mat[1, 2] = -np.sin(ISOMETRIC_ANGLE)
        x_rot_mat[2, 1] = np.sin(ISOMETRIC_ANGLE)
        x_rot_mat[2, 2] = np.cos(ISOMETRIC_ANGLE)

        y_rot_mat = np.eye(4, dtype=np.float32)
        y_rot_mat[0, 0] = np.cos(ISOMETRIC_ANGLE)
        y_rot_mat[0, 2] = np.sin(ISOMETRIC_ANGLE)
        y_rot_mat[2, 0] = -np.sin(ISOMETRIC_ANGLE)
        y_rot_mat[2, 2] = np.cos(ISOMETRIC_ANGLE)

        self._rotation_mat = np.matmul(x_rot_mat, y_rot_mat)

        self._update_mvp()

    def _update_mvp(self):
        mvp = np.matmul(self._translation_mat, self._rotation_mat)
        mvp = np.matmul(mvp, self._scale_mat)
        self.mvp = mvp

    @property
    def scale(self):
        return self._scale

    @scale.setter
    def scale(self, value):
        self._scale = value
        self._on_scale_changed()

    @property
    def rotation_angle(self):
        return self._rotation_angle

    @rotation_angle.setter
    def rotation_angle(self, value):
        self._rotation_angle = value
        self._on_rotation_changed()

    @property
    def translation_x(self):
        return self._translation_x

    @translation_x.setter
    def translation_x(self, value):
        self._translation_x = value
        self._on_translation_changed()

    @property
    def translation_y(self):
        return self._translation_y

    @translation_y.setter
    def translation_y(self, value):
        self._translation_y = value
        self._on_translation_changed()

    @property
    def translation(self):
        return self._translation_x, self._translation_y

    @translation.setter
    def translation(self, value: tuple[float, float]):
        assert isinstance(value, tuple), "Translation must be a tuple of 2 floats"
        assert len(value) == 2, "Translation must be a tuple of 2 floats"
        self._translation_x, self._translation_y = value
        self._on_translation_changed()

    def translate(self, x, y):
        self._translation_x += x
        self._translation_y += y
        self._on_translation_changed()

    def rotate(self, angle):
        self._rotation_angle += angle
        self._on_rotation_changed()

    def scale_by(self, factor):
        self._scale *= factor
        self._on_scale_changed()
    
    def zoom(self, delta):
        self._scale += delta
        self._on_scale_changed()
    
    def reset(self):
        self._scale = 1.0
        self._rotation_angle = 0.0
        self._translation_x = 0.0
        self._translation_y = 0.0
        self._update_mvp()