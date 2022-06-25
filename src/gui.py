from curses import textpad
from typing import Text
from dpgext import gui
from dpgext.elements import elements as el
import dearpygui.dearpygui as dpg
from utils.sig import metsig
from utils.logger import LOGGER

from app_vars import APP_VARS
from constants import GUI_WIDTH
from objects.element import Element

class MainWindow(gui.Window):
    @metsig(gui.Window.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_elements: dict[str, Element] = {}
        self.test_list = [1,2,3,4]

        self.target_element = None
        self.translation_obj = None
        self.rotation_obj = None
        self.scale_obj = None

        self.translation_clients = []
        self.rotation_clients = []
        self.scale_clients = []

        self.game_fps_label = el.Text()


    def _update_available_elements(self):
        id = 0
        self.available_elements.clear()
        for element in APP_VARS.world.elements:
            if hasattr(element, 'shape_renderers'):
                element_shape_names = [ renderer.shape_spec.name for renderer in element.shape_renderers ]
                element_name = f"{id}: {element.name}({type(element)})[{'-'.join(element_shape_names)}]"
            else:
                element_name = f'{id}: {element.name}({type(element)})[MISSING RENDERER]'
            self.available_elements[element_name] = element
            id += 1

    def _update_by_list_selection(self, *args, **kwargs):
        self.target_element.unselect()

        element_name = dpg.get_value('element-list')
        element = self.available_elements[element_name]

        self.target_element = element

        self.target_element.select()

        tranform = self.target_element.transform
        self.translation_obj = tranform.translation
        self.scale_obj = tranform.scale
        self.rotation_obj = tranform.rotation

        for client in self.translation_clients:
            client.object = self.translation_obj
        for client in self.rotation_clients:
            client.object = self.rotation_obj
        for client in self.scale_clients:
            client.object = self.scale_obj
        

    def describe(self):
        with self:
            el.Text("Hello World!").add()
            cube = APP_VARS.world.elements[1]
            camera = APP_VARS.camera
            COORDS = ['x', 'y', 'z']

            dpg.add_listbox(list(self.available_elements.keys()), tag='element-list', callback=self._update_by_list_selection)

            dpg.add_separator()

            self.target_element = cube
            self.translation_obj = cube.transform.translation
            self.scale_obj = cube.transform.scale
            self.rotation_obj = cube.transform.rotation

            ## Translation ##

            el.Text().add(el.TextParams('Translation'))

            self.translation_clients = [ el.SliderFloat(self.translation_obj, coord) for coord in COORDS]
            for client in self.translation_clients:
                client.add(params=el.SliderFloatParams(min_value=-10, max_value=10) )
                
            #################
            dpg.add_separator()

            ## Rotation ##

            el.Text().add(el.TextParams('Rotation'))

            self.rotation_clients = [ el.SliderFloat(self.rotation_obj, coord) for coord in  COORDS]
            for client in self.rotation_clients:
                client.add(params=el.SliderFloatParams(min_value=-10, max_value=10))

            ###########


            dpg.add_separator()
            
            ## Rotation ##

            el.Text().add(el.TextParams('Rotation'))

            self.rotation_clients = [ el.SliderFloat(self.rotation_obj, coord) for coord in  COORDS]
            for client in self.rotation_clients:
                client.add(params=el.SliderFloatParams(min_value=0.0, max_value=10))

            ###########

            dpg.add_separator()

            ## Scale ##

            el.Text().add(el.TextParams('Scale'))

            self.scale_clients = [ el.SliderFloat(self.scale_obj, coord) for coord in  COORDS]
            for client in self.scale_clients:
                client.add(params=el.SliderFloatParams(min_value=0.01, max_value=10))

            ###########


            ## Buttons ##

            def tp_to_element():
                camera.transform.translation.xyz = self.target_element.transform.translation.xyz

            el.Button().add(el.ButtonParams(label='Teleport to', callback=tp_to_element))
            el.Button().add(el.ButtonParams(label='Select', callback=lambda: self.target_element.select()))
            el.Button().add(el.ButtonParams(label='Unselect', callback=lambda: self.target_element.unselect()))

            #############

            self.game_fps_label.add(el.TextParams('Game FPS: ?'))

            dpg.add_separator()
            dpg.add_spacer(height=10)

            el.Text().add(el.TextParams('Lighting Config:'))
            el.Text().add(el.TextParams('Ka'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ka').add(el.SliderFloatParams(min_value=0, max_value=1))
            el.Text().add(el.TextParams('Kd'))
            el.SliderFloat(APP_VARS.lighting_config, 'Kd').add(el.SliderFloatParams(min_value=0, max_value=1))
            el.Text().add(el.TextParams('Ks'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ks').add(el.SliderFloatParams(min_value=0, max_value=1))
            el.Text().add(el.TextParams('Ns'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ns').add(el.SliderFloatParams(min_value=0, max_value=1000))

            el.Text().add(el.TextParams('Do daylight cycle?'))
            el.CheckBox(APP_VARS.lighting_config, 'do_daylight_cycle').add(el.CheckboxParams())
            el.Text().add(el.TextParams('Light position'))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'x').add(el.SliderFloatParams(min_value=-10, max_value=10))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'y').add(el.SliderFloatParams(min_value=-10, max_value=10))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'z').add(el.SliderFloatParams(min_value=-10, max_value=10))



    def update(self):
        self._update_available_elements()
        dpg.configure_item('element-list', items=list(self.available_elements.keys()))

        dpg.set_value(self.game_fps_label.tag, APP_VARS.game_fps.fps)

        return super().update()

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