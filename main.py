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
from model.Color import Color
from view.MainFrame import MainFrame
from control.MousePublisher import MousePublisher
from model.Event import Event
from model.ActionType import ActionType
from control.handlers.CanvasHandler import CanvasHandler
from control.handlers.ToggleableUIHandler import ToggleableUIHandler
from control.Command import Command
from model.Point import Point
from view.ColorPicker import ColorPicker
import cv2
from model.SmallClassifier import SmallClassifier
import torch
from model.HandDetectorWrapper import HandDetectorWrapper 
import numpy as np

vid = cv2.VideoCapture(1)

model = SmallClassifier()
model.load_state_dict(torch.load("modelo_pointing2.pth"))
model.eval()

hand_detector = HandDetectorWrapper(maxHands=1, detectionCon=0.2, minTrackCon=0.1)
mainFrame = MainFrame()
mouse_publisher = MousePublisher()
undo_history: list[Command] = []
redo_history: list[Command] = []
toggleable_ui_elements: list[ToggleableUI] = []
color = Color(50, 50, 255)  # Default color set to black
draw_size = 10  # Default draw size

timer = cv2.getTickCount()
pointing_timer = cv2.getTickCount()
start_timer = True

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
mainFrame.add_layer(Canvas(800, 600))
color_picker = ColorPickerToggleable(Point(0, 550), 50, 50, ColorPicker(Point(0, 500), 200, 100), color=color, toggled_on=False)
toggleable_ui_elements.append(color_picker)
mainFrame.add_UI_element(color_picker)

key_listener = KeyHandler()
key_listener.add_command_for_key(ExitCommand(), Key.ESC)
key_listener.add_command_for_key(UndoCommand(undo_history, redo_history), Key.CTRL_Z, Key.U)
key_listener.add_command_for_key(RedoCommand(redo_history, undo_history), Key.CTRL_Y, Key.R)
key_listener.add_command_for_key(NoneCommand(), Key.NONE)

first_click = True


prev_index_finger_point: dict[str, Point] = {i: Point(400, 300) for i in range(21)}
def normalize_finger_position(point: Point, prev_point: Point, img_width, img_height, canvas_width, canvas_height) -> Point:         
    if point is None:
        return None, prev_point
    point = point.scale_axes(1/img_width, 1/img_height)
    point = point.scale_axes(canvas_width, canvas_height)
    point = point.lerp(prev_point, 0.3)    
    point = point.scale(1.1)
    point = point.to_int()

    return point

while True:
    frame = vid.read()[1]
    frame = cv2.flip(frame, 1)  # Espejo para selfie view
    
    hand_detector.setImage(frame)
    # hands = hand_detector.findHands(draw=True)
    hands = hand_detector.findHands(draw=False)

    if hands:
        hand = hands[0]
        lmList = hand['lmList']
        x = list()
        for i in model.normalize_sample(lmList):
            if i is not None:
                x.append(i)
        x = np.array(x).flatten().astype(np.float32)
        x = torch.tensor(x, dtype=torch.float32).unsqueeze(0)  # batch=1
        with torch.no_grad():
            pred = model(x)

        hand_points = hand_detector.get_hand_points(hands, 0)
        for i in range(len(hand_points)):
            hand_points[i] = normalize_finger_position(hand_points[i], prev_index_finger_point[i],
                                                      frame.shape[1], frame.shape[0],
                                                      mainFrame.get_window_size()[0], mainFrame.get_window_size()[1])
            prev_index_finger_point[i] = hand_points[i] if hand_points[i] is not None else prev_index_finger_point[i]
        mainFrame.set_hand(hand_points.values())
        index_finger_point = hand_points[8]
        
        if index_finger_point is not None:
            if pred.item() > 0.8:
                if start_timer:
                    pointing_timer = cv2.getTickCount() + 0.3 * cv2.getTickFrequency()
                    start_timer = False
                elif cv2.getTickCount() > pointing_timer:
                    if first_click:
                        handle_button_down(Event(index_finger_point, ActionType.LEFT_BUTTON_DOWN))
                        first_click = False
                    mouse_publisher.notify_click(Event(index_finger_point, ActionType.LEFT_DRAG))
                    # cv2.putText(frame, "Dibujando", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                    mainFrame.set_cursor_type(0)
            else:
                start_timer = True
                first_click = True
                mouse_publisher.clear_subscriber()
                redo_history.clear()
                # cv2.putText(frame, "No dibujando", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                mainFrame.set_cursor_type(1)
            
            # dibujar posición del dedo índice
            mainFrame.set_cursor_position(index_finger_point)

    # cv2.imshow("Hand Tracking", frame)

    mainFrame.redraw()
    key  = cv2.waitKey(10) # No meter dentro del if porque condiciona el refresco de la ventana

    if not mouse_publisher.has_subscriber() or key == Key.ESC:
        key_listener.get_command(key).execute()


