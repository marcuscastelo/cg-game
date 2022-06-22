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