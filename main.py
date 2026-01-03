from control.MouseListener import MouseListener
from control.commands.PickColorCommand import PickColorCommand
from control.commands.ToggleMenuCommand import ToggleMenuCommand
from control.commands.CanvasColorPickerCommand import CanvasColorPickerCommand
from control.commands.ExitCommand import ExitCommand
from control.commands.NoneCommand import NoneCommand
from control.commands.UndoCommand import UndoCommand
from control.commands.RedoCommand import RedoCommand
from view.MenuToggleable import MenuToggleable
from view.ColorPickerToggleable import ColorPickerToggleable
from view.ToggleableUI import ToggleableUI
from control.handlers.KeyHandler import KeyHandler
from definitions.Key import Key
from view.Canvas import Canvas
from model.Color import COLOR_TRANSPARENT, COLOR_WHITE, Color, COLOR_DEFAULT_COLOR
from view.MainFrame import MainFrame
from control.MousePublisher import MousePublisher
from model.Event import Event
from model.ActionType import ActionType
from control.handlers.CanvasHandler import CanvasHandler
from control.handlers.ToggleableUIHandler import ToggleableUIHandler
from control.commands.Command import Command
from model.Point import Point
from view.ColorPicker import ColorPicker
from screeninfo import get_monitors
import cv2
from model.SmallClassifier import SmallClassifier
import torch
from model.HandDetectorWrapper import HandDetectorWrapper
import queue
from control.threads.HandTrackerThread import HandTrackerThread
from view.Menu import Menu
from view.MenuIcon import MenuIcon
from definitions.Tools import Tools
from control.ToolStatus import ToolStatus
from definitions.HandsGestures import HandsGestures

vid = cv2.VideoCapture(0)

monitors = get_monitors()
event_queue = queue.Queue()

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

timer = cv2.getTickCount()
pointing_timer = cv2.getTickCount()
start_timer = True
USE_HAND_TRACKING = True

if USE_HAND_TRACKING:
    hand_thread = HandTrackerThread(
        event_queue,
        vid,
        hand_detector,
        model,
        mainFrame
    )
    hand_thread.start()

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
    global color, color_picker # No me gusta usar global, pero no se me ocurre otra forma
    redo_history.clear()

    UIElement = mainFrame.get_element_selected(event.position)
    print(f"UI Element clicked: {UIElement}")

    toggleable_element = None
    if isinstance(UIElement, ToggleableUI):
        toggleable_element = UIElement
    desactivate_all_toggleable_ui_unless(toggleable_element)
    

    if isinstance(UIElement, Canvas):
        redo_history.clear()
        event = Event(event.position, event.action_type, event.flags, mainFrame.get_rotation_level(), mainFrame.get_window_size(), mainFrame.get_zoom_level())
        canvas_handler = CanvasHandler(UIElement, event, color, draw_size,
                                       tool_status.get_tool())
        command = canvas_handler.get_command()
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
        toggle_menu_command: ToggleMenuCommand = ToggleableUIHandler(UIElement, event).get_command()
        toggle_menu_command.set_cursor(event.position)
        toggle_menu_command.execute()
        menu_icon = toggle_menu_command.get_tool_selected()
        if menu_icon is not None:
            tool_type = menu_icon.get_type()
            if tool_type is not None:
                tool_status.set_tool(tool_type)

def handle_scroll(event: Event):
    UIElement = mainFrame.get_element_selected(event.position)
    if isinstance(UIElement, ColorPickerToggleable):
        UIElement.handle_scroll(event)
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
        handle_scroll(Event(Point(x, y), ActionType.SCROLL, flags, mainFrame.get_rotation_level(), mainFrame.get_window_size(), mainFrame.get_zoom_level()))

def handle_gesture(gesture: HandsGestures, menu: MenuToggleable = None):
    global prev_hand_size
    
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

    print(f"Gesture detected: {gesture}, changing tool to {gesture_tool}")

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
            pass
        case HandsGestures.SCROLL:
            pass
        case HandsGestures.IDLE:
            prev_hand_size = None
        case _:
            print("No recognized gesture")

prev_hand_size = None

mainFrame.add_cursor_listener(control_mouse_event)

canvas_size_ratio = 0.6
mainFrame.set_rotation_level = 0.0
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

vertical_menu.add_element(pencil_icon)
vertical_menu.add_element(borrador_icon)
vertical_menu.add_element(cubeta_de_color_icon)
vertical_menu.add_element(selector_de_color_icon)
vertical_menu.add_element(texto_ocr_icon)
vertical_menu.add_element(dibujo_asistido_yolo_icon)
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

