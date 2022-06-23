from curses import textpad
from typing import Text
from dpgext import gui
from dpgext.elements import elements as el
import dearpygui.dearpygui as dpg
from utils.sig import metsig
from utils.logger import LOGGER

from app_vars import APP_VARS
from constants import GUI_WIDTH

class MainWindow(gui.Window):
    @metsig(gui.Window.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def describe(self):
        with self:
            el.Text("Hello World!").add()
            cube = APP_VARS.world.elements[1]
            camera = APP_VARS.camera

            el.Text().add(el.TextParams('Translation'))
            el.SliderFloat(cube.transform.translation, 'x').add(el.SliderFloatParams(min_value=0.2, max_value=10))
            el.SliderFloat(cube.transform.translation, 'y').add(el.SliderFloatParams(min_value=0.2, max_value=10))
            el.SliderFloat(cube.transform.translation, 'z').add(el.SliderFloatParams(min_value=0.2, max_value=10))

            dpg.add_separator()

            el.Text().add(el.TextParams('Scale'))
            el.SliderFloat(cube.transform.scale, 'x').add(el.SliderFloatParams(min_value=0.2, max_value=10))
            el.SliderFloat(cube.transform.scale, 'y').add(el.SliderFloatParams(min_value=0.2, max_value=10))
            el.SliderFloat(cube.transform.scale, 'z').add(el.SliderFloatParams(min_value=0.2, max_value=10))

            def tp_to_element():
                camera.transform.translation = cube.transform.translation.xyz

            el.Button().add(el.ButtonParams(callback=tp_to_element))


class AppGui(gui.Gui):
    def _init_windows(self):
        self.windows['main'] = MainWindow()

        dpg.set_viewport_pos([0, 0])
        dpg.set_viewport_width(GUI_WIDTH)
        dpg.set_viewport_height(1080)

        return super()._init_windows()

    def _before_exit(self):
        LOGGER.log_info("Gui is closing", 'AppGui')
        APP_VARS.closing = True
        super()._before_exit()

    def _tick(self):
        if APP_VARS.closing:
            self._running = False

        return super()._tick() 