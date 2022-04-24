from dataclasses import dataclass
import numpy as np

from utils.geometry import Vec3, Vec2

@dataclass
class Transform:
    translation: Vec3
    rotation: Vec3
    scale: Vec3

    def __post_init__(self):
        self.translation = Vec3(self.translation)
        self.rotation = Vec3(self.rotation)
        self.scale = Vec3(self.scale)
        
    @property
    def x(self) -> float:
        return self.translation.x
    
    @property
    def y(self) -> float:
        return self.translation.y
    
    @property
    def z(self) -> float:
        return self.translation.z

    @property
    def xy(self) -> Vec2:
        return self.translation.xy
    
    @property
    def xyz(self) -> Vec3:
        return self.translation

    @property
    def rx(self) -> float:
        return self.rotation.x

    @property
    def ry(self) -> float:
        return self.rotation.y
    
    @property
    def rz(self) -> float:
        return self.rotation.z

    @property
    def rxyz(self) -> Vec3:
        return self.rotation

    # @property
    # def model_matrix(self):
    #     # glm identity matrix
    #     model_matrix = glm.mat4(1.0)

    #     # translate
    #     model_matrix = glm.translate(model_matrix, self.translation)

    #     # rotate
    #     model_matrix = glm.rotate(model_matrix, self.rotation.x, vec3(1, 0, 0))



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