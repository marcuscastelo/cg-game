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

class InputSystem:
    _instance = None
    def __init__(self):
        self.input_events = []
        self.key_states = {}
        self.mouse_states = {}

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
        if action == glfw.PRESS:
            self.key_states[key] = True
        elif action == glfw.RELEASE:
            self.key_states[key] = False

    def mouse_button_callback(self, window, button, action, mods):
        if action == glfw.PRESS:
            self.mouse_states[button] = True
        elif action == glfw.RELEASE:
            self.mouse_states[button] = False

    def cursor_pos_callback(self, window, xpos, ypos):
        self.mouse_states['xpos'] = xpos
        self.mouse_states['ypos'] = ypos

    def is_pressed(self, key: str):
        key = key.upper()

        if key in ALIASES:
            key = ALIASES[key]

        keys = []
        if key in LEFT_OR_RIGHT:
            lkey, rkey = f'LEFT_{key}', f'RIGHT_{key}'
            keys.extend([lkey, rkey])
        else:
            keys.append(key)

        keycodes = (self.keycodes[k] for k in keys)
        return any(self.key_states.get(keycode, False) for keycode in keycodes)

INPUT_SYSTEM = InputSystem.get_instance()


def set_glfw_callbacks(window):
    IS = INPUT_SYSTEM
    glfw.set_key_callback(window, IS.key_callback)
    glfw.set_mouse_button_callback(window, IS.mouse_button_callback)
    glfw.set_cursor_pos_callback(window, IS.cursor_pos_callback)