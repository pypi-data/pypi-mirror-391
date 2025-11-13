from ._classes import *
# gui

# int GuiButton(Rectangle bounds, const char *text)
lib.GuiButton.argtypes = [Rectangle, ctypes.c_char_p]
lib.GuiButton.restype = ctypes.c_int
def gui_button(bounds, text:str):
    return bool(lib.GuiButton(bounds, text.encode()))

# int GuiMessageBox(Rectangle bounds, const char *title, const char *message, const char *buttons)
makeconnect("GuiMessageBox", [Rectangle, c_char_p, c_char_p, c_char_p], c_int)
def gui_message_box(bounds, title, message, buttons):
    return lib.GuiMessageBox(bounds, title, message, buttons)

