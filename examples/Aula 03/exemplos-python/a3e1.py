"""Cor dinâmica"""
import glfw
from OpenGL.GL import glClear, glClearColor, GL_COLOR_BUFFER_BIT
# %%
glfw.init()
glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
window = glfw.create_window(720, 600, "Minha Primeira Janela", None, None)
glfw.make_context_current(window)
glfw.show_window(window)
R = 0.2
G = 1.0
B = 0.5
RM = GM = BM = .01
while not glfw.window_should_close(window):
    glfw.poll_events()
    glClear(GL_COLOR_BUFFER_BIT)
    if R >= 1 or R <= 0:
        RM *= -1
    if G >= 1 or G <= 0:
        GM *= -1
    if B >= 1 or B <= 0:
        BM *= -1
    R += RM
    G += GM
    B += BM
    glClearColor(R, G, B, 1.0)
    glfw.swap_buffers(window)
glfw.terminate()
