from dpgext import gui
from dpgext.elements import elements as el
import dearpygui.dearpygui as dpg
from utils.sig import metsig
from utils.logger import LOGGER

from app_vars import APP_VARS
from constants import GUI_WIDTH
from objects.cube import Cube
from objects.element import Element as GameElement

COORDS = ['x', 'y', 'z']


class MainWindow(gui.Window):
    '''
    Main GUI Window

    See the describe() method for a description of the fields and UI elements.
    '''

    @metsig(gui.Window.__init__)
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.available_elements: dict[str, GameElement] = {}
        self.test_list = [1, 2, 3, 4]

        self.translation_obj = None
        self.rotation_obj = None
        self.scale_obj = None

        self.translation_clients = []
        self.rotation_clients = []
        self.scale_clients = []

        self.game_fps_label = el.Text()
        self._last_selected_element = None
        self.mock_obj = Cube('mock_cube')

        self.sync_Ka = True # Toggles whether to sync xyz of Ka or not (if False, Ka is always graylight, from black to white)
        self.sync_Kd = True # Toggles whether to sync xyz of Kd or not (if False, Kd is always graylight, from black to white)
        self.sync_Ks = True # Toggles whether to sync xyz of Ks or not (if False, Ks is always graylight, from black to white)

    def _describe_available_elements_list(self):
        dpg.add_listbox(list(self.available_elements.keys()),
                        tag='element-list', callback=self._on_list_click)

    def _describe_translation_controls(self):
        el.Text().add(el.TextParams('Translation'))

        with dpg.group(horizontal=True):
            self.translation_clients = [el.SliderFloat(
                self.translation_obj, coord) for coord in COORDS]
            for client in self.translation_clients:
                client.add(params=el.SliderFloatParams(
                    min_value=-10, max_value=10, width=100))

    def _describe_rotation_controls(self):
        el.Text().add(el.TextParams('Rotation'))

        with dpg.group(horizontal=True):
            self.rotation_clients = [el.SliderFloat(
                self.rotation_obj, coord) for coord in COORDS]
            for client in self.rotation_clients:
                client.add(params=el.SliderFloatParams(
                    min_value=0.0, max_value=10, width=100))


    def _describe_scale_controls(self):
        el.Text().add(el.TextParams('Scale'))

        with dpg.group(horizontal=True):
            self.scale_clients = [el.SliderFloat(
                self.scale_obj, coord) for coord in COORDS]
            for client in self.scale_clients:
                client.add(params=el.SliderFloatParams(
                    min_value=0.01, max_value=10, width=100))

    def _describe_tp_buttons(self):
        camera = APP_VARS.camera
        def tp_to_element():
            camera.transform.translation.xyz = APP_VARS.selected_element.transform.translation.xyz

        def tp_element_to_me():
            APP_VARS.selected_element.transform.translation.xyz = camera.transform.translation.xyz
            APP_VARS.selected_element.transform.translation.y -= camera._ground_y

        el.Button().add(el.ButtonParams(label='Teleport to', callback=tp_to_element))
        el.Button().add(el.ButtonParams(label='Teleport to me', callback=tp_element_to_me))

    def _describe_element_controls(self):
        self._describe_translation_controls()
        dpg.add_separator()
        self._describe_rotation_controls()
        dpg.add_separator()
        self._describe_scale_controls()
        dpg.add_separator()
        dpg.add_separator()
        self._describe_tp_buttons()

    def _describe_light_controls(self):
        el.Text().add(el.TextParams('Global Lighting Config:'))

        min_light = 0
        max_light = 100

        with dpg.group(horizontal=True):
            el.Text().add(el.TextParams('Ka_x'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ka_x').add(
                el.SliderFloatParams(min_value=0, max_value=1, width=100))

            el.Text().add(el.TextParams('Ka_y'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ka_y').add(
                el.SliderFloatParams(min_value=0, max_value=1, width=100))

            el.Text().add(el.TextParams('Ka_z'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ka_z').add(
                el.SliderFloatParams(min_value=0, max_value=1, width=100))

            el.CheckBox(self, 'sync_Ka').add(
                el.CheckboxParams(label='Sync'))

        with dpg.group(horizontal=True):
            el.Text().add(el.TextParams('Kd_x'))
            el.SliderFloat(APP_VARS.lighting_config, 'Kd_x').add(
                el.SliderFloatParams(min_value=min_light, max_value=max_light, width=100))

            el.Text().add(el.TextParams('Kd_y'))
            el.SliderFloat(APP_VARS.lighting_config, 'Kd_y').add(
                el.SliderFloatParams(min_value=min_light, max_value=max_light, width=100))

            el.Text().add(el.TextParams('Kd_z'))
            el.SliderFloat(APP_VARS.lighting_config, 'Kd_z').add(
                el.SliderFloatParams(min_value=min_light, max_value=max_light, width=100))

            el.CheckBox(self, 'sync_Kd').add(
                el.CheckboxParams(label='Sync'))

        with dpg.group(horizontal=True):
            el.Text().add(el.TextParams('Ks_x'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ks_x').add(
                el.SliderFloatParams(min_value=min_light, max_value=max_light, width=100))

            el.Text().add(el.TextParams('Ks_y'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ks_y').add(
                el.SliderFloatParams(min_value=min_light, max_value=max_light, width=100))

            el.Text().add(el.TextParams('Ks_z'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ks_z').add(
                el.SliderFloatParams(min_value=min_light, max_value=max_light, width=100))

            el.CheckBox(self, 'sync_Ks').add(
                el.CheckboxParams(label='Sync'))

        with dpg.group(horizontal=True):
            el.Text().add(el.TextParams('Ns'))
            el.SliderFloat(APP_VARS.lighting_config, 'Ns').add(el.SliderFloatParams(
                min_value=min_light, max_value=max_light * 10, width=100))

        with dpg.group(horizontal=True):
            el.Text().add(el.TextParams('Do daylight cycle?'))
            el.CheckBox(APP_VARS.lighting_config, 'do_daylight_cycle').add(
                el.CheckboxParams())

        with dpg.group(horizontal=True):
            el.Text().add(el.TextParams('Light position'))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'x').add(
                el.SliderFloatParams(min_value=-10, max_value=10, width=100))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'y').add(
                el.SliderFloatParams(min_value=-10, max_value=10, width=100))
            el.SliderFloat(APP_VARS.lighting_config.light_position, 'z').add(
                el.SliderFloatParams(min_value=-10, max_value=10, width=100))

    def describe(self):
        ''' Describe the GUI Layout '''
        self.translation_obj = self.mock_obj.transform.translation
        self.scale_obj = self.mock_obj.transform.scale
        self.rotation_obj = self.mock_obj.transform.rotation

        # Window context manager
        with self:
            # 1. At the top of the window, show a list of elements
            self._describe_available_elements_list()

            dpg.add_separator() # --------------------------------------------------

            # 2. Just below the list, show the selected element's controls
            # TODO: show selected object name
            self._describe_element_controls()

            dpg.add_separator() # --------------------------------------------------

            # 3. Show game FPS
            self.game_fps_label.add(el.TextParams('Game FPS: ?'))

            dpg.add_separator() # --------------------------------------------------
            dpg.add_spacer(height=10)

            # 4. Show the Lighting Controls
            self._describe_light_controls()
            

    def _update_available_elements(self):
        ''' Update the list of available elements '''
        id = 0
        self.available_elements.clear()
        for element in APP_VARS.world.elements:
            if hasattr(element, 'shape_renderers'):
                element_shape_names = [
                    renderer.shape_spec.name for renderer in element.shape_renderers]
                element_name = f"{id}: {element.name}({type(element)})[{'-'.join(element_shape_names)}]"
            else:
                element_name = f'{id}: {element.name}({type(element)})[MISSING RENDERER]'
            self.available_elements[element_name] = element
            id += 1

        dpg.configure_item(
            'element-list', items=list(self.available_elements.keys()))

    def _on_list_click(self, *args, **kwargs):
        ''' Called when the user clicks on an element in the list '''

        # Gets the selected element
        element_name = dpg.get_value('element-list')
        element = self.available_elements[element_name]
        
        assert isinstance(
            element, GameElement), f"Expected 'GameElement', found {type(element)=}"
        
        # Updates the element selection to the clicked element
        if self._last_selected_element == element:
            element = None
        self._update_selection(element)
        self._last_selected_element = element

    def _update_selection(self, element: GameElement):
        ''' When the selected element is changed, call this function to update the GUI and global variables '''
        if not element:
            element = self.mock_obj
        assert isinstance(
            element, GameElement), f"Expected 'GameElement', found {type(element)=}"

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

    def _sync_selected_element(self):
        ''' Synchronize the selected element's transform with the GUI '''
        if self._last_selected_element is not APP_VARS.selected_element:
            # Check if the selected element has changed by some other means (e.g. SelectionRay)
            self._update_selection(APP_VARS.selected_element)
            self._last_selected_element = APP_VARS.selected_element

    def _sync_locked_light_coefficients(self):
        ''' If lock is checked, sync the light components xyz for each coefficients '''
        config = APP_VARS.lighting_config
        if self.sync_Ka: config.Ka_y = config.Ka_z = config.Ka_x
        if self.sync_Kd: config.Kd_y = config.Kd_z = config.Kd_x
        if self.sync_Ks: config.Ks_y = config.Ks_z = config.Ks_x

    def update(self):
        ''' Update the GUI '''

        self._update_available_elements()

        dpg.set_value(self.game_fps_label.tag, APP_VARS.game_fps.fps)

        # Watch for changes and react accordingly
        self._sync_selected_element()
        self._sync_locked_light_coefficients()

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
