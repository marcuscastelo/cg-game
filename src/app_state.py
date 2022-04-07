from dataclasses import dataclass
import numpy as np

@dataclass
class MVPState:
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
    def translation(self, value):
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
        
@dataclass
class AppState:
    texture: int = 0
    closing: bool = False
    mvp_manager: MVPState = MVPState()
  
STATE = AppState()