from curses import textpad
from typing import Text
from dpgext import gui
from dpgext.elements import elements as el
import dearpygui.dearpygui as dpg
from utils.sig import metsig
from utils.logger import LOGGER

from app_vars import APP_VARS
from camera import Camera
from constants import GUI_WIDTH
from objects.cube import Cube
from objects.element import Element

class MainWindow(gui.Window):
    @metsig(gui.Window.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_elements: dict[str, Element] = {}
        self.test_list = [1,2,3,4]

        self.translation_obj = None
        self.rotation_obj = None
        self.scale_obj = None

        self.translation_clients = []
        self.rotation_clients = []
        self.scale_clients = []

        self.game_fps_label = el.Text()
        self._last_selected_element = None
        self.mock_obj = Cube('mock_cube')

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

    def _on_list_click(self, *args, **kwargs):
        element_name = dpg.get_value('element-list')
        element = self.available_elements[element_name]
        assert isinstance(element, Element), f"Expected 'Element', found {type(element)=}"
        if self._last_selected_element == element:
            element = None
        self._update_selection(element)
        self._last_selected_element = element

    def _update_selection(self, element: Element):
        if not element:
            element = self.mock_obj
        assert isinstance(element, Element), f"Expected 'Element', found {type(element)=}"

        if APP_VARS.selected_element:
            APP_VARS.selected_element.unselect()

        APP_VARS.selected_element = element
        APP_VARS.selected_element.select()

        tranform = APP_VARS.selected_element.transform
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
            camera = APP_VARS.camera
            COORDS = ['x', 'y', 'z']

            dpg.add_listbox(list(self.available_elements.keys()), tag='element-list', callback=self._on_list_click)

            dpg.add_separator()

            self.translation_obj = self.mock_obj.transform.translation
            self.scale_obj = self.mock_obj.transform.scale
            self.rotation_obj = self.mock_obj.transform.rotation

            ## Translation ##

            el.Text().add(el.TextParams('Translation'))

            with dpg.group(horizontal=True):
                self.translation_clients = [ el.SliderFloat(self.translation_obj, coord) for coord in COORDS]
                for client in self.translation_clients:
                    client.add(params=el.SliderFloatParams(min_value=-10, max_value=10, width=100))
                    
            #################
            dpg.add_separator()
            
            ## Rotation ##

            el.Text().add(el.TextParams('Rotation'))

            with dpg.group(horizontal=True):
                self.rotation_clients = [ el.SliderFloat(self.rotation_obj, coord) for coord in  COORDS]
                for client in self.rotation_clients:
                    client.add(params=el.SliderFloatParams(min_value=0.0, max_value=10, width=100))

            ###########

            dpg.add_separator()

            ## Scale ##

            el.Text().add(el.TextParams('Scale'))

            with dpg.group(horizontal=True):
                self.scale_clients = [ el.SliderFloat(self.scale_obj, coord) for coord in  COORDS]
                for client in self.scale_clients:
                    client.add(params=el.SliderFloatParams(min_value=0.01, max_value=10, width=100))

            ###########


            ## Buttons ##

            def tp_to_element():
                camera.transform.translation.xyz = APP_VARS.selected_element.transform.translation.xyz
            def tp_element_to_me():
                APP_VARS.selected_element.transform.translation.xyz = camera.transform.translation.xyz
                APP_VARS.selected_element.transform.translation.y -= camera._ground_y

            el.Button().add(el.ButtonParams(label='Teleport to', callback=tp_to_element))
            el.Button().add(el.ButtonParams(label='Teleport to me', callback=tp_element_to_me))

            #############

            self.game_fps_label.add(el.TextParams('Game FPS: ?'))

            dpg.add_separator()
            dpg.add_spacer(height=10)

            el.Text().add(el.TextParams('Lighting Config:'))

            with dpg.group(horizontal=True):
                el.Text().add(el.TextParams('Ka_x'))
                el.SliderFloat(APP_VARS.lighting_config, 'Ka_x').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

                el.Text().add(el.TextParams('Ka_y'))
                el.SliderFloat(APP_VARS.lighting_config, 'Ka_y').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

                el.Text().add(el.TextParams('Ka_z'))
                el.SliderFloat(APP_VARS.lighting_config, 'Ka_z').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

            with dpg.group(horizontal=True):
                el.Text().add(el.TextParams('Kd_x'))
                el.SliderFloat(APP_VARS.lighting_config, 'Kd_x').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

                el.Text().add(el.TextParams('Kd_y'))
                el.SliderFloat(APP_VARS.lighting_config, 'Kd_y').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

                el.Text().add(el.TextParams('Kd_z'))
                el.SliderFloat(APP_VARS.lighting_config, 'Kd_z').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

            with dpg.group(horizontal=True):
                el.Text().add(el.TextParams('Ks_x'))
                el.SliderFloat(APP_VARS.lighting_config, 'Ks_x').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

                el.Text().add(el.TextParams('Ks_y'))
                el.SliderFloat(APP_VARS.lighting_config, 'Ks_y').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

                el.Text().add(el.TextParams('Ks_z'))
                el.SliderFloat(APP_VARS.lighting_config, 'Ks_z').add(el.SliderFloatParams(min_value=0, max_value=1, width=100))

            el.Text().add(el.TextParams('Ns'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ns').add(el.SliderFloatParams(min_value=0, max_value=1000, width=100))

            el.Text().add(el.TextParams('Do daylight cycle?'))
            el.CheckBox(APP_VARS.lighting_config, 'do_daylight_cycle').add(el.CheckboxParams())
            el.Text().add(el.TextParams('Light position'))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'x').add(el.SliderFloatParams(min_value=-10, max_value=10, width=100))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'y').add(el.SliderFloatParams(min_value=-10, max_value=10, width=100))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'z').add(el.SliderFloatParams(min_value=-10, max_value=10, width=100))



    def update(self):
        self._update_available_elements()
        dpg.configure_item('element-list', items=list(self.available_elements.keys()))

        dpg.set_value(self.game_fps_label.tag, APP_VARS.game_fps.fps)

        if self._last_selected_element is not APP_VARS.selected_element:
            self._update_selection(APP_VARS.selected_element)
            self._last_selected_element = APP_VARS.selected_element

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