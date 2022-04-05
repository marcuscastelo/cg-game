import dearpygui.dearpygui as dpg

from dpgext import gui
from dpgext import elements as el
from dpgext.utils.sig import metsig
from dpgext.utils.logger import LOGGER

import numpy as np
from app_state import STATE

class MainWindow(gui.Window):
    @metsig(gui.Window.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scale = 1.0
        self.rotation_angle = 0.0
        self.translation_x = 0.0
        self.translation_y = 0.0

        self.scale_mat = np.eye(4, dtype=np.float32)
        self.rotation_mat = np.eye(4, dtype=np.float32)
        self.translation_mat = np.eye(4, dtype=np.float32)

    def _on_scale_changed(self):
        # Recalculate MVP
        self.scale_mat = np.diag([self.scale, self.scale, 1, 1.0])
        self._update_mvp()
        pass

    def _on_translation_changed(self):
        # Recalculate MVP
        self.translation_mat = np.diag([1, 1, 1, 1.0])
        self.translation_mat[0, 3] = self.translation_x
        self.translation_mat[1, 3] = self.translation_y
        self._update_mvp()
        pass

    def _on_rotation_changed(self):
        # Recalculate MVP
        self.rotation_mat = np.eye(4, dtype=np.float32)
        self.rotation_mat[0, 0] = np.cos(self.rotation_angle)
        self.rotation_mat[0, 1] = -np.sin(self.rotation_angle)
        self.rotation_mat[1, 0] = np.sin(self.rotation_angle)
        self.rotation_mat[1, 1] = np.cos(self.rotation_angle)
        self._update_mvp()
        pass

    def _update_mvp(self):
        mvp = np.matmul(self.scale_mat, self.rotation_mat) 
        mvp = np.matmul(mvp, self.translation_mat)
        STATE.mvp_manager = mvp

    def describe(self):
        with self:
            el.Text("Hello World!").construct()
            el.Slider(self, 'scale').construct(width=200, height=20, callback=self._on_scale_changed, min_value=0.1, max_value=10.0)
            el.Slider(self, 'rotation_angle').construct(width=200, height=20, callback=self._on_rotation_changed, min_value=0.0, max_value=2*np.pi)
            el.Slider(self, 'translation_x').construct(width=200, height=20, callback=self._on_translation_changed, min_value=-1.0, max_value=1.0)
            el.Slider(self, 'translation_y').construct(width=200, height=20, callback=self._on_translation_changed, min_value=-1.0, max_value=1.0)

class AppGui(gui.Gui):
    def _init_windows(self):
        self.windows['main'] = MainWindow()
        return super()._init_windows()

    def _before_exit(self):
        LOGGER.log_info("Gui is closing", 'AppGui')
        STATE.closing = True
        super()._before_exit()

    def _tick(self):
        if STATE.closing:
            self._running = False

        # dpg.draw_image()

        return super()._tick() 