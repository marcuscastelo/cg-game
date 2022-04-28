from dataclasses import dataclass, field
from typing import Any
import glfw

LEFT_OR_RIGHT = ['SHIFT', 'ALT', 'CONTROL', 'SUPER']
ALIASES = {
    'CTRL': 'CONTROL',
    'LCTRL': 'CONTROL',
    'RCTRL': 'CONTROL',
    'LALT': 'ALT',
    'RALT': 'ALT',
    'LWIN': 'SUPER',
    'RWIN': 'SUPER',
    'LSHIFT': 'SHIFT',
    'RSHIFT': 'SHIFT',
}

@dataclass
class States:
    key_states: dict[int, Any] = field(default_factory=dict)
    mouse_states: dict[str, Any] = field(default_factory=dict)

class InputSystem:
    _instance = None
    def __init__(self):
        self.input_events = []
        self.current_states = States()
        self.last_states = States()

        self.keycodes = {
            k[4:]: i for k, i in glfw.__dict__.items() if k.startswith('KEY_')
        }
        self.mousecodes = {
            k[12:]: i for k, i in glfw.__dict__.items() if k.startswith('MOUSE_BUTTON')
        }

        print(f'keycodes: {self.keycodes}')
        
        print(f'mousecodes: {self.mousecodes}')

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = InputSystem()
        return cls._instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def key_callback(self, window, key, scancode, action, mods):
        self.last_states.key_states[key] = self.current_states.key_states.get(key, False)

        if action == glfw.PRESS:
            self.current_states.key_states[key] = True
        elif action == glfw.RELEASE:
            self.current_states.key_states[key] = False
        elif action == glfw.REPEAT:
            self.current_states.key_states[key] = True

    def mouse_button_callback(self, window, button, action, mods):
        self.last_states.mouse_states[button] = self.current_states.mouse_states.get(button, False)

        if action == glfw.PRESS:
            self.current_states.mouse_states[button] = True
        elif action == glfw.RELEASE:
            self.current_states.mouse_states[button] = False
        elif action == glfw.REPEAT:
            self.current_states.mouse_states[button] = True

    def cursor_pos_callback(self, window, xpos, ypos):
        self.last_states.mouse_states['xpos'] = self.current_states.mouse_states.get('xpos', 0)
        self.last_states.mouse_states['ypos'] = self.current_states.mouse_states.get('ypos', 0)

        self.current_states.mouse_states['xpos'] = xpos
        self.current_states.mouse_states['ypos'] = ypos


    def _convert_key_to_keycode(self, key: str) -> list[int]:
        key = key.upper()

        if key in ALIASES:
            key = ALIASES[key]

        keys = []
        if key in LEFT_OR_RIGHT:
            lkey, rkey = f'LEFT_{key}', f'RIGHT_{key}'
            keys.extend([lkey, rkey])
        else:
            keys.append(key)

        keycodes = [self.keycodes[k] for k in keys]
        return keycodes

    def is_pressed(self, key: str):
        keycodes = self._convert_key_to_keycode(key)
        return any(self.current_states.key_states.get(keycode, False) for keycode in keycodes)

    def just_pressed(self, key: str):
        keycodes = self._convert_key_to_keycode(key)
        return any(self.current_states.key_states.get(keycode, False) and not self.last_states.key_states.get(keycode, False) for keycode in keycodes)

    def just_released(self, key: str):
        keycodes = self._convert_key_to_keycode(key)
        return any(self.last_states.key_states.get(keycode, False) and not self.current_states.key_states.get(keycode, False) for keycode in keycodes)

INPUT_SYSTEM = InputSystem.get_instance()


def set_glfw_callbacks(window):
    IS = INPUT_SYSTEM
    glfw.set_key_callback(window, IS.key_callback)
    glfw.set_mouse_button_callback(window, IS.mouse_button_callback)
    glfw.set_cursor_pos_callback(window, IS.cursor_pos_callback)