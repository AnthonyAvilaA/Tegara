import math
import cv2
import torch
import queue
from screeninfo import get_monitors

from control.MouseListener import MouseListener
from control.commands.CanvasEnchancedPencilCommand import CanvasEnchancedPencilCommand
from control.commands.CanvasTextDetectionComand import CanvasTextDetectionCommand
from control.commands.CanvasTextDetectionComand import CanvasTxtCommand
from control.commands.CanvasTextCommand import CanvasTextCommand
from control.commands.PickColorCommand import PickColorCommand
from control.commands.ToggleMenuCommand import ToggleMenuCommand
from control.commands.CanvasColorPickerCommand import CanvasColorPickerCommand
from control.commands.ExitCommand import ExitCommand
from control.commands.NoneCommand import NoneCommand
from control.commands.UndoCommand import UndoCommand
from control.commands.Command import Command
from control.commands.RedoCommand import RedoCommand
from control.handlers.CanvasHandler import CanvasHandler
from control.handlers.ToggleableUIHandler import ToggleableUIHandler
from control.handlers.KeyHandler import KeyHandler
from control.threads.HandTrackerThread import HandTrackerThread
from control.ToolStatus import ToolStatus
from control.MousePublisher import MousePublisher

from view.ToggleableUI import ToggleableUI
from view.ColorPickerToggleable import ColorPickerToggleable
from view.ColorPicker import ColorPicker
from view.MenuToggleable import MenuToggleable
from view.Menu import Menu
from view.MenuIcon import MenuIcon
from view.Canvas import Canvas
from view.MainFrame import MainFrame

from model.Color import COLOR_TRANSPARENT, COLOR_WHITE, Color, COLOR_DEFAULT_COLOR
from model.Event import Event
from model.ActionType import ActionType
from model.Point import Point
from model.SmallClassifier import SmallClassifier
from model.HandDetectorWrapper import HandDetectorWrapper

from definitions.HandsGestures import HandsGestures
from definitions.Tools import Tools
from definitions.Key import Key
from paddleocr import PaddleOCR
import numpy as np
import time
'''
_PADDLE_OCR = None
def rgba_to_white_bg(rgbA_img: np.ndarray) -> np.ndarray:
    """
    Convierte una imagen RGBA con transparencia
    a RGB con fondo blanco.
    """
    # Separar canales
    rgb = rgbA_img[..., :3].astype(np.float32)
    alpha = rgbA_img[..., 3].astype(np.float32) / 255.0  # [0,1]

    # Fondo blanco
    white_bg = np.ones_like(rgb) * 255

    # Alpha blending: out = fg * a + bg * (1 - a)
    out = rgb * alpha[..., None] + white_bg * (1 - alpha[..., None])

    return out.astype(np.uint8)

def get_paddle_ocr():
    global _PADDLE_OCR
    if _PADDLE_OCR is None:
        print("Initializing PaddleOCR ONCE...")
        _PADDLE_OCR = PaddleOCR(
            lang='ch',
            ocr_version='PP-OCRv4'
        )
    return _PADDLE_OCR

def detect_text_with_paddle(image):
    start = time.time()
    reader = get_paddle_ocr()
    image = rgba_to_white_bg(image)

    results = reader.predict(image)

    print(results)
    print(f"PaddleOCR detection time: {time.time() - start} seconds")
    '''
vid = cv2.VideoCapture(0)
monitors = get_monitors()
event_queue = queue.Queue()
ocr_cmd = CanvasTextDetectionCommand()
mainFrame = MainFrame(monitors[0].width, monitors[0].height)
model = SmallClassifier()
model.load_state_dict(torch.load("modelo_pointing_v2.pth"))
model.eval()

hand_detector = HandDetectorWrapper(maxHands=1, detectionCon=0.2, minTrackCon=0.1)
mouse_publisher = MousePublisher()
undo_history: list[Command] = []
redo_history: list[Command] = []
toggleable_ui_elements: list[ToggleableUI] = []
color = COLOR_DEFAULT_COLOR  # Default color set to black
draw_size = 10  # Default draw size
tool_status = ToolStatus(Tools.PENCIL)
previous_tool = None
current_comand = None
timer = cv2.getTickCount()
pointing_timer = cv2.getTickCount()
start_timer = True
USE_HAND_TRACKING = False

if USE_HAND_TRACKING:
    hand_thread = HandTrackerThread(
        event_queue,
        vid,
        hand_detector,
        model,
        mainFrame
    )
    hand_thread.start()

TEMP_LAYER_TOOLS = {
    Tools.ENCHANCED_PENCIL,
    Tools.TEXT
}

# temporal
def change_draw_size(flags: int):
    global draw_size
    if flags > 0:
        draw_size = min(draw_size + 1, 100)
    else:
        draw_size = max(draw_size - 1, 1)

def start_command(command: Command):
    if command:
        command.execute()
        undo_history.append(command)
        if isinstance(command, MouseListener):
            mouse_publisher.set_subscriber(command)



def handle_button_down(event: Event):
    global color, color_picker, current_comand # No me gusta usar global, pero no se me ocurre otra forma
    redo_history.clear()

    UIElement = mainFrame.get_element_selected(event.position)
    print(f"UI Element clicked: {UIElement}")

    if tool_status.get_tool() != Tools.NONE:
        if isinstance(UIElement, ToggleableUI):
            desactivate_all_toggleable_ui_unless(UIElement)
        else:
            desactivate_all_toggleable_ui_unless(None)
    

    if isinstance(UIElement, Canvas):
        redo_history.clear()
        event = Event(event.position, event.action_type, event.flags, mainFrame.get_rotation_level(), mainFrame.get_window_size(), mainFrame.get_zoom_level())
        canvas_handler = CanvasHandler(UIElement, event, color, draw_size,
                                       tool_status.get_tool())
        command = canvas_handler.get_command()
        current_comand = command
        start_command(command)

        print(f"Tool used: {tool_status.get_tool()}")
        if isinstance(command, CanvasColorPickerCommand):
            new_color = command.get_color_selected()
            if new_color is not None:
                if new_color == COLOR_TRANSPARENT:
                    new_color = COLOR_WHITE
                color = new_color
                color_picker.update_color(color)
                color_picker.set_dirty()
                
    elif isinstance(UIElement, ColorPickerToggleable):
        toggle_color_command: PickColorCommand = ToggleableUIHandler(UIElement, event).get_command()
        toggle_color_command.set_cursor(event.position)
        toggle_color_command.execute()
        new_color = toggle_color_command.get_color_selected()
        if new_color is not None:
            color = new_color
    
    elif isinstance(UIElement, MenuToggleable):
        toggle_menu_command = ToggleableUIHandler(UIElement, event).get_command()
        toggle_menu_command.set_cursor(event.position)
        toggle_menu_command.execute()
        menu_icon = toggle_menu_command.get_tool_selected()
        
        if menu_icon is None:
            return

        new_tool = menu_icon.get_type()
        if new_tool is None:
            return

        switch_tool(new_tool, vertical_menu)
        return

def run_detection_from_canvas():
    print("Running sketch detection...")
    if current_comand and isinstance(current_comand, CanvasEnchancedPencilCommand):
        current_comand.draw_sketch_on_canvas()
        mainFrame.merge_temp_layer()
        switch_back_to_pencil(vertical_menu)

def run_detect_text_from_canvas():
    print("running text detection...")
    texts_detected, bbox = ocr_cmd.detect(mainFrame.get_temp_layer().get_image())
    if not texts_detected or bbox is None:
        return
    if current_comand and isinstance(current_comand, CanvasTxtCommand):
        current_comand.draw_text_fit_bbox_pil(texts_detected, bbox)
        mainFrame.merge_temp_layer()
        switch_back_to_pencil(vertical_menu)

def switch_back_to_pencil(menu: MenuToggleable | None = None):
    global current_comand, previous_tool

    tool_status.set_tool(Tools.PENCIL)
    previous_tool = Tools.PENCIL
    current_comand = None

    if menu is not None:
        menu.set_tool(Tools.PENCIL)
def switch_tool(new_tool: Tools, menu=None):
    print(f"Switching tool to: {new_tool}")
    global previous_tool, current_comand

    old_tool = tool_status.get_tool()

    if new_tool == old_tool and old_tool in TEMP_LAYER_TOOLS:
        if old_tool == Tools.ENCHANCED_PENCIL:
            run_detection_from_canvas()
        elif old_tool == Tools.TEXT:
            run_detect_text_from_canvas()

        mainFrame.merge_temp_layer()

        # volver a pencil
        tool_status.set_tool(Tools.PENCIL)
        if menu:
            menu.set_tool(Tools.PENCIL)
        return


    if old_tool in TEMP_LAYER_TOOLS and new_tool != old_tool:
        mainFrame.remove_temp_layer()
        mainFrame.set_actual_layer(0)

    if new_tool in TEMP_LAYER_TOOLS:
        mainFrame.create_temp_layer(
            int(monitors[0].width * canvas_size_ratio),
            int(monitors[0].height * canvas_size_ratio),
            COLOR_TRANSPARENT
        )
        mainFrame.set_actual_layer(1)

    tool_status.set_tool(new_tool)
    if menu:
        menu.set_tool(new_tool)

def handle_scroll(event: Event):
    global color_picker
    if color_picker.is_toggled_on():
        color_picker.handle_scroll(event)
    else:
        change_draw_size(event.flags)

def desactivate_all_toggleable_ui_unless(unless: ToggleableUI = None):
    for toggleable in toggleable_ui_elements:
        if toggleable != unless:
            toggleable.set_toggle(False)

def control_mouse_event(event, x, y, flags, param):
    point = Point(x, y)
    # TODO: Put this in new class MouseHandler
    if event == cv2.EVENT_LBUTTONDOWN:
        event_queue.put({"type": "left_down", "point": Point(x, y)})
        # handle_button_down(Event(Point(x, y), ActionType.LEFT_BUTTON_DOWN, flags, mainFrame.get_rotation_level(), mainFrame.get_window_size()))

    if event == cv2.EVENT_RBUTTONDOWN:
        event_queue.put({"type": "right_down", "point": Point(x, y)})
        # handle_button_down(Event(Point(x, y), ActionType.RIGHT_BUTTON_DOWN, flags, mainFrame.get_rotation_level(), mainFrame.get_window_size()))

    if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        event_queue.put({"type": "left_drag", "point": Point(x, y)})
        # mouse_publisher.notify_click(Event(Point(x, y), ActionType.LEFT_DRAG, flags, mainFrame.get_rotation_level(), mainFrame.get_window_size()))

    if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON:
        event_queue.put({"type": "right_drag", "point": Point(x, y)})
        # mouse_publisher.notify_click(Event(Point(x, y), ActionType.RIGHT_DRAG, flags, mainFrame.get_rotation_level(), mainFrame.get_window_size()))
    
    if event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_RBUTTONUP:
        event_queue.put({"type": "reset_drag", "point": point})
        # mouse_publisher.clear_subscriber()
        # redo_history.clear()

    if event == cv2.EVENT_MOUSEWHEEL:
        event_queue.put({"type": "scroll", "point": Point(x, y), "flags": flags})

def handle_gesture(gesture: HandsGestures, menu: MenuToggleable = None):
    global prev_hand_size, prev_hand_center_y
    
    gesture_tool = None
    match gesture:
        case HandsGestures.POINTING:
            gesture_tool = Tools.PENCIL
        case HandsGestures.ERASE:
            gesture_tool = Tools.ERASER
        case HandsGestures.FILL:
            gesture_tool = Tools.FILL
        case _:
            gesture_tool = Tools.NONE

    if gesture_tool == tool_status.get_tool() and gesture_tool != Tools.NONE:
        return

    match gesture:
        case HandsGestures.POINTING:
            tool_status.set_tool(Tools.PENCIL)
            menu.set_tool(Tools.PENCIL)
        case HandsGestures.ERASE:
            tool_status.set_tool(Tools.ERASER)
            menu.set_tool(Tools.ERASER)
        case HandsGestures.ZOOM:
            tool_status.set_tool(Tools.NONE)
            hand = mainFrame.get_hand_points()
            # conseguir el recuadro de la mano
            point = hand.pop()
            x_left, x_right, y_top, y_bottom = point.get_x(), point.get_x(), point.get_y(), point.get_y()
            for p in hand:
                if p.get_x() < x_left:
                    x_left = p.get_x()
                if p.get_x() > x_right:
                    x_right = p.get_x()
                if p.get_y() < y_top:
                    y_top = p.get_y()
                if p.get_y() > y_bottom:
                    y_bottom = p.get_y()
            
            hand_size = (x_right - x_left) * (y_bottom - y_top)
            if prev_hand_size is not None:
                if hand_size > prev_hand_size * 1.1:
                    mainFrame.zoom_in()
                elif hand_size < prev_hand_size * 0.9:
                    mainFrame.zoom_out()
            prev_hand_size = hand_size
            
        case HandsGestures.FILL:
            tool_status.set_tool(Tools.FILL)
            menu.set_tool(Tools.FILL)
        case HandsGestures.ROTATE:
            tool_status.set_tool(Tools.NONE)
            hand = mainFrame.get_hand_points()
            index_finger = hand[8]
            middle_finger = hand[12]
            angle = math.degrees(math.atan2(middle_finger.get_y() - index_finger.get_y(),
                                            middle_finger.get_x() - index_finger.get_x()))
            if 85 <= angle <= 95:
                angle = 90.0
            
            angle = (angle + 360) % 360  # Normalize angle to [0, 360)
            mainFrame.set_rotation_level(360 - angle)
        case HandsGestures.SCROLL:
            tool_status.set_tool(Tools.NONE)
            hand = mainFrame.get_hand_points()
            center = hand[9] # Approximate center of the hand
            if prev_hand_center_y is not None:
                if center.get_y() < prev_hand_center_y - 20:
                    for _ in range(20):
                        event_queue.put({"type": "scroll", "point": hand[8], "flags": 1})
                elif center.get_y() > prev_hand_center_y + 20:
                    for _ in range(20):
                        event_queue.put({"type": "scroll", "point": hand[8], "flags": -1})            
            prev_hand_center_y = center.get_y()
        case HandsGestures.IDLE:
            tool_status.set_tool(Tools.NONE)
            prev_hand_size = None
            prev_hand_center_y = None
        case _:
            print("No recognized gesture")


prev_hand_size = None
prev_hand_center_y = None

mainFrame.add_cursor_listener(control_mouse_event)

canvas_size_ratio = 0.6
mainFrame.add_layer(Canvas(int(monitors[0].width * canvas_size_ratio), int(monitors[0].height * canvas_size_ratio), COLOR_WHITE))

color_picker = ColorPickerToggleable(Point(50, monitors[0].height - 200), 100, 100, ColorPicker(Point(50, monitors[0].height - 300), 400, 200), color=color, toggled_on=False)
toggleable_ui_elements.append(color_picker)
mainFrame.add_UI_element(color_picker)
vertical_menu = MenuToggleable(
    Point(60, monitors[0].height // 2 - 25),
    80, 80,
    Menu(Point(40, 30),
         Color(200, 200, 200, 200),
         border_width=2,
         is_vertical=True,
         vertical_padding=30,
         horizontal_padding=20),
    toggled_on=False)

toggleable_ui_elements.append(vertical_menu)
    
icon_w, icon_h = 100, 100
pencil_icon = MenuIcon(Point(0, 0), Tools.PENCIL, icon_w, icon_h, "./assets/lapiz.webp")
borrador_icon = MenuIcon(Point(0, 0), Tools.ERASER, icon_w, icon_h, "./assets/borrador.png")
cubeta_de_color_icon = MenuIcon(Point(0, 0), Tools.FILL, icon_w, icon_h, "./assets/cubeta_de_color.png")
selector_de_color_icon = MenuIcon(Point(0, 0), Tools.COLOR_PICKER, icon_w, icon_h, "./assets/selector_de_color.png")
texto_ocr_icon = MenuIcon(Point(0, 0), Tools.TEXT, icon_w, icon_h, "./assets/texto_ocr.png")
dibujo_asistido_yolo_icon = MenuIcon(Point(0, 0), Tools.ENCHANCED_PENCIL, icon_w, icon_h, "./assets/dibujo_asistido_yolo.png")
clear_canvas_icon = MenuIcon(Point(0, 0), Tools.CLEAR_CANVAS, icon_w, icon_h, "./assets/clear.png")
vertical_menu.add_element(pencil_icon)
vertical_menu.add_element(borrador_icon)
vertical_menu.add_element(cubeta_de_color_icon)
vertical_menu.add_element(selector_de_color_icon)
vertical_menu.add_element(texto_ocr_icon)
vertical_menu.add_element(dibujo_asistido_yolo_icon)
vertical_menu.add_element(clear_canvas_icon)
mainFrame.add_UI_element(vertical_menu)

key_listener = KeyHandler()
key_listener.add_command_for_key(ExitCommand(), Key.ESC)
key_listener.add_command_for_key(UndoCommand(undo_history, redo_history), Key.CTRL_Z, Key.U)
key_listener.add_command_for_key(RedoCommand(redo_history, undo_history), Key.CTRL_Y, Key.R)
key_listener.add_command_for_key(NoneCommand(), Key.NONE)

first_click = True

prev_index_finger_point: dict[str, Point] = {i: Point(400, 300) for i in range(21)}


while True:

    # =========== PROCESAR EVENTOS DEL HILO ===========
    while not event_queue.empty():
        ev = event_queue.get()

        if ev["type"] == "hand_gesture":
            handle_gesture(ev["gesture"], vertical_menu)
            print(f"Gesture detected: {ev['gesture']}")
        
        elif ev["type"] == "cursor_update":
            mainFrame.set_hand(ev["points"].values())
        
        elif ev["type"] == "cursor_type":
            mainFrame.set_cursor_type(ev["cursor"])

        elif ev["type"] == "cursor_position":
            mainFrame.set_cursor_position(ev["point"])

        elif ev["type"] == "left_down":
            handle_button_down(Event(ev["point"], ActionType.LEFT_BUTTON_DOWN, 0, mainFrame.get_rotation_level(), mainFrame.get_window_size(), mainFrame.get_zoom_level()))

        elif ev["type"] == "left_drag":
            mouse_publisher.notify_click(Event(ev["point"], ActionType.LEFT_DRAG, 0, mainFrame.get_rotation_level(), mainFrame.get_window_size(), mainFrame.get_zoom_level()))

        elif ev["type"] == "scroll":
            handle_scroll(Event(ev["point"], ActionType.SCROLL, ev["flags"], mainFrame.get_rotation_level(), mainFrame.get_window_size(), mainFrame.get_zoom_level()))

        elif ev["type"] == "reset_drag":
            mouse_publisher.clear_subscriber()

    # =========== REDIBUJAR ===========
    mainFrame.redraw()

    key = cv2.waitKey(1)
    if not mouse_publisher.has_subscriber() or key == Key.ESC:
        key_listener.get_command(key).execute()

