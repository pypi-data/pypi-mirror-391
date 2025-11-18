from ._classes import *

# complete!

lib.InitWindow.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_char_p]
lib.InitWindow.restype = None
def init_window(width = 800, height = 600, title = "Raylib in Python"):
    lib.InitWindow(width, height, title.encode())

#bool WindowShouldClose()
lib.WindowShouldClose.argtypes = []
lib.WindowShouldClose.restype = ctypes.c_int
def window_should_close():
    return bool(lib.WindowShouldClose())

# void CloseWindow()
def close_window():
    lib.CloseWindow()

lib.IsWindowReady.restype = ctypes.c_bool
def is_window_ready():
    return lib.IsWindowReady()

lib.IsWindowFullscreen.restype = ctypes.c_bool
is_window_fullscreen = lib.IsWindowFullscreen
lib.IsWindowHidden.restype = ctypes.c_bool
is_window_hidden = lib.IsWindowHidden
lib.IsWindowMinimized.restype = ctypes.c_bool
is_window_minimized = lib.IsWindowMinimized
lib.IsWindowMaximized.restype = ctypes.c_bool
is_window_maximized = lib.IsWindowMaximized
lib.IsWindowState.restype = ctypes.c_bool
is_window_state = lib.IsWindowState
lib.IsWindowResized.restype = ctypes.c_bool
is_window_resized = lib.IsWindowResized

lib.SetWindowState.argtypes = [ctypes.c_uint]
def set_window_state(flags):
    lib.SetWindowState(flags)

lib.ClearWindowState.argtypes = [ctypes.c_uint]
def clear_window_state(flags):
    lib.ClearWindowState(flags)
# draw




toggle_fullscreen = lib.ToggleFullscreen
toggle_borderless_windowed = lib.ToggleBorderlessWindowed
maximize_window = lib.MaximizeWindow
minimize_window = lib.MinimizeWindow
restore_window = lib.RestoreWindow

lib.SetWindowIcon.argtypes = [Image]
def set_window_icon(img):
    lib.SetWindowIcon(img)

lib.SetWindowIcons.argtypes = [rl_imgp, ctypes.c_int]
def set_window_icons(images):
    """
    images: list of Image structs
    """
    count = len(images)
    # Convert list to ctypes array
    ImageArrayType = Image * count
    c_array = ImageArrayType(*images)
    # Call the C function
    lib.SetWindowIcons(c_array, count)

lib.SetWindowTitle.argtypes = [ctypes.c_char_p]
def set_window_title(title:str):
    lib.SetWindowTitle(title.encode())
lib.SetWindowPosition.argtypes = [ctypes.c_int, ctypes.c_int]
def set_window_position(x,y):
    lib.SetWindowPosition(x,y)
lib.SetWindowMonitor.argtypes = [ctypes.c_int]
def set_window_monitor(monitor):
    lib.SetWindowMonitor(monitor)
lib.SetWindowMinSize.argtypes = [ctypes.c_int, ctypes.c_int]
def set_window_min_size(w,h):
    lib.SetWindowMinSize(w,h)
lib.SetWindowMaxSize.argtypes = [ctypes.c_int, ctypes.c_int]
def set_window_max_size(w,h):
    lib.SetWindowMaxSize(w,h)
lib.SetWindowSize.argtypes = [ctypes.c_int, ctypes.c_int]
def set_window_size(w,h):
    lib.SetWindowSize(w,h)
lib.SetWindowOpacity.argtypes = [ctypes.c_float]
def set_window_opacity(op:float):
    lib.SetWindowOpacity(op)
set_window_focused = lib.SetWindowFocused

lib.GetWindowHandle.restype = ctypes.c_void_p
def get_window_handle():
    return lib.GetWindowHandle()

lib.GetScreenWidth.restype = ctypes.c_int
def get_screen_width():
    return lib.GetScreenWidth()

lib.GetScreenHeight.restype = ctypes.c_int
def get_screen_height():
    return lib.GetScreenHeight()

lib.GetRenderWidth.restype = ctypes.c_int
def get_render_width():
    return lib.GetRenderWidth()

lib.GetRenderHeight.restype = ctypes.c_int
def get_render_height():
    return lib.GetRenderHeight()
lib.GetMonitorCount.restype = ctypes.c_int
def get_monitor_count():
    return lib.GetMonitorCount()

lib.GetCurrentMonitor.restype = ctypes.c_int
def get_current_monitor():
    return lib.GetCurrentMonitor()

lib.GetMonitorPosition.restype = Vector2
lib.GetMonitorPosition.argtypes = [ctypes.c_int]
def get_monitor_position(monitor):
    return lib.GetMonitorPosition(monitor)

lib.GetMonitorWidth.restype = ctypes.c_int
lib.GetMonitorWidth.argtypes = [ctypes.c_int]
def get_monitor_width(monitor):
    return lib.GetMonitorWidth(monitor)

lib.GetMonitorHeight.restype = ctypes.c_int
lib.GetMonitorHeight.argtypes = [ctypes.c_int]
def get_monitor_height(monitor):
    return lib.GetMonitorHeight(monitor)

#physical_ Physical
lib.GetMonitorPhysicalWidth.restype = ctypes.c_int
lib.GetMonitorPhysicalWidth.argtypes = [ctypes.c_int]
def get_monitor_physical_width(monitor):
    return lib.GetMonitorPhysicalWidth(monitor)

lib.GetMonitorPhysicalHeight.restype = ctypes.c_int
lib.GetMonitorPhysicalHeight.argtypes = [ctypes.c_int]
def get_monitor_physical_height(monitor):
    return lib.GetMonitorPhysicalHeight(monitor)

lib.GetMonitorRefreshRate.restype = ctypes.c_int
lib.GetMonitorRefreshRate.argtypes = [ctypes.c_int]
def get_monitor_refresh_rate(monitor):
    return lib.GetMonitorRefreshRate(monitor)

lib.GetWindowPosition.restype = Vector2
def get_window_position():
    return lib.GetWindowPosition()

lib.GetWindowScaleDPI.restype = Vector2
def get_window_scale_dpi():
    return lib.GetWindowScaleDPI()

lib.GetMonitorName.restype = ctypes.c_char_p
lib.GetMonitorName.argtypes = [ctypes.c_int]
def get_monitor_name(id):
    return lib.GetMonitorName(id)
lib.SetClipboardText.argtypes = [ctypes.c_char_p]
def set_clipboard_text(text:str):
    lib.SetClipboardText(text.encode())

lib.GetClipboardText.restype = ctypes.c_char_p
def get_clipboard_text():
    return lib.GetClipboardText()

lib.GetClipboardImage.restype = Image
def get_clipboard_image():
    return lib.GetClipboardImage()
enable_event_waiting = lib.EnableEventWaiting
disable_event_waiting = lib.DisableEventWaiting