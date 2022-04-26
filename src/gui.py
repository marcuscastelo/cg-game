from dpgext import gui
from dpgext import elements as el
from utils.sig import metsig
from utils.logger import LOGGER

from app_state import APP_VARS

class MainWindow(gui.Window):
    @metsig(gui.Window.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def describe(self):
        with self:
            el.Text("Hello World!").construct()

class AppGui(gui.Gui):
    def _init_windows(self):
        self.windows['main'] = MainWindow()
        return super()._init_windows()

    def _before_exit(self):
        LOGGER.log_info("Gui is closing", 'AppGui')
        APP_VARS.closing = True
        super()._before_exit()

    def _tick(self):
        if APP_VARS.closing:
            self._running = False

        return super()._tick() 