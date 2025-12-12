from control.MouseListener import MouseListener
from control.commands.ExitCommand import ExitCommand
from control.commands.NoneCommand import NoneCommand
from control.commands.UndoCommand import UndoCommand
from control.commands.RedoCommand import RedoCommand
from view.ColorPickerToggleable import ColorPickerToggleable
from view.ToggleableUI import ToggleableUI
from control.handlers.KeyHandler import KeyHandler
from definitions.key import Key
from view.Canvas import Canvas
from model.Color import Color, DEFAULT_COLOR
from view.MainFrame import MainFrame
from control.MousePublisher import MousePublisher
from model.Event import Event
from model.ActionType import ActionType
from control.handlers.CanvasHandler import CanvasHandler
from control.handlers.ToggleableUIHandler import ToggleableUIHandler
from control.Command import Command
from model.Point import Point
from view.ColorPicker import ColorPicker
from screeninfo import get_monitors
import cv2
from model.SmallClassifier import SmallClassifier
import torch
from model.HandDetectorWrapper import HandDetectorWrapper
import queue
from control.HandTrackerThread import HandTrackerThread

vid = cv2.VideoCapture(1)

monitors = get_monitors()
event_queue = queue.Queue()

mainFrame = MainFrame(monitors[0].width, monitors[0].height)
model = SmallClassifier()
model.load_state_dict(torch.load("modelo_pointing1.pth"))
model.eval()

hand_detector = HandDetectorWrapper(maxHands=1, detectionCon=0.2, minTrackCon=0.1)
mouse_publisher = MousePublisher()
undo_history: list[Command] = []
redo_history: list[Command] = []
toggleable_ui_elements: list[ToggleableUI] = []
color = DEFAULT_COLOR  # Default color set to black
draw_size = 10  # Default draw size

timer = cv2.getTickCount()
pointing_timer = cv2.getTickCount()
start_timer = True

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
    global color # No me gusta usar global, pero no se me ocurre otra forma
    redo_history.clear()

    UIElement = mainFrame.get_element_clicked(event.position)

    if isinstance(UIElement, Canvas):
        desactivate_all_toggleable_ui()
        canvas_handler = CanvasHandler(UIElement, event, color, draw_size)
        command = canvas_handler.get_command()
        start_command(command)
    elif isinstance(UIElement, ColorPickerToggleable):
        toggle_color_command = ToggleableUIHandler(UIElement, event).get_command()
        toggle_color_command.set_cursor(event.position)
        toggle_color_command.execute()
        new_color = toggle_color_command.get_color_selected()
        if new_color is not None:
            color = new_color

def desactivate_all_toggleable_ui():
    for toggleable in toggleable_ui_elements:
        toggleable.set_toggle(False)

def control_mouse_event(event, x, y, flags, param):
    # TODO: Put this in new class MouseHandler
    if event == cv2.EVENT_LBUTTONDOWN:
        handle_button_down(Event(Point(x, y), ActionType.LEFT_BUTTON_DOWN))

    if event == cv2.EVENT_RBUTTONDOWN:
        handle_button_down(Event(Point(x, y), ActionType.RIGHT_BUTTON_DOWN))

    if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_LBUTTON:
        mouse_publisher.notify_click(Event(Point(x, y), ActionType.LEFT_DRAG))

    if event == cv2.EVENT_MOUSEMOVE and flags == cv2.EVENT_FLAG_RBUTTON:
        mouse_publisher.notify_click(Event(Point(x, y), ActionType.RIGHT_DRAG))
    
    if event == cv2.EVENT_LBUTTONUP or event == cv2.EVENT_RBUTTONUP:
        mouse_publisher.clear_subscriber()
        redo_history.clear()

    if event == cv2.EVENT_MOUSEWHEEL:
        change_draw_size(flags)

mainFrame.add_cursor_listener(control_mouse_event)
mainFrame.add_layer(Canvas(monitors[0].width, monitors[0].height))
color_picker = ColorPickerToggleable(Point(50, monitors[0].height - 200), 100, 100, ColorPicker(Point(50, monitors[0].height - 200), 400, 200), color=color, toggled_on=False)
toggleable_ui_elements.append(color_picker)
mainFrame.add_UI_element(color_picker)

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

        if ev["type"] == "cursor_update":
            mainFrame.set_hand(ev["points"].values())
        
        elif ev["type"] == "cursor_type":
            mainFrame.set_cursor_type(ev["cursor"])

        elif ev["type"] == "cursor_position":
            mainFrame.set_cursor_position(ev["point"])

        elif ev["type"] == "left_down":
            handle_button_down(Event(ev["point"], ActionType.LEFT_BUTTON_DOWN))

        elif ev["type"] == "left_drag":
            mouse_publisher.notify_click(Event(ev["point"], ActionType.LEFT_DRAG))

        elif ev["type"] == "reset_drag":
            mouse_publisher.clear_subscriber()
            redo_history.clear()

    # =========== REDIBUJAR ===========
    mainFrame.redraw()

    key = cv2.waitKey(1)
    if not mouse_publisher.has_subscriber() or key == Key.ESC:
        key_listener.get_command(key).execute()

