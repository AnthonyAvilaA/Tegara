from control.MouseListener import MouseListener
from control.commands.ExitCommand import ExitCommand
from control.commands.NoneCommand import NoneCommand
from control.commands.UndoCommand import UndoCommand
from control.commands.RedoCommand import RedoCommand
from control.handlers.KeyHandler import KeyHandler
from definitions.key import Key
from view.Canvas import Canvas
from model.Color import Color
from view.MainFrame import MainFrame
from control.MousePublisher import MousePublisher
from model.Event import Event
from model.ActionType import ActionType
from control.handlers.CanvasHandler import CanvasHandler
from control.Command import Command
from model.Point import Point
from view.ColorPicker import ColorPicker
import cv2
from model.SmallClassifier import SmallClassifier
import torch
from model.HandDetectorWrapper import HandDetectorWrapper 
import numpy as np

vid = cv2.VideoCapture(0)
model = SmallClassifier()         # misma arquitectura
model.load_state_dict(torch.load("modelo_pointing.pth"))
model.eval()                      # modo inferencia

mainFrame = MainFrame()
mouse_publisher = MousePublisher()
undo_history = []
redo_history = []
color = Color(50, 50, 255)  # Default color set to black
draw_size = 10  # Default draw size

# temporal
def set_color(new_color: Color):
    global color
    color = new_color

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
    redo_history.clear()
    x = event.position.get_x()
    y = event.position.get_y()
    UIElement = mainFrame.get_element_clicked(x, y)
    if isinstance(UIElement, Canvas):
        # No sé si lo correcto es pasar el Canvas o la imagen del Canvas y subscribir a un update de cnavas
        canvas_handler = CanvasHandler(UIElement, event, color, draw_size)
        command = canvas_handler.get_command()
        start_command(command)
    elif isinstance(UIElement, ColorPicker):
        picked_color = UIElement.get_color_at(x, y)
        if picked_color:
            set_color(picked_color)
    
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
color_picker = ColorPicker(0, 500, 200, 100)
mainFrame.add_UI_element(color_picker)

key_listener = KeyHandler()
key_listener.add_command_for_key(ExitCommand(), Key.ESC)
key_listener.add_command_for_key(UndoCommand(undo_history, redo_history), Key.CTRL_Z, Key.U)
key_listener.add_command_for_key(RedoCommand(redo_history, undo_history), Key.CTRL_Y, Key.R)
key_listener.add_command_for_key(NoneCommand(), Key.NONE)

hand_detector = HandDetectorWrapper()
first_click = True

def normalize_finger_position(point: Point, img_width=800, img_height=600, canvas_width=800, canvas_height=600) -> Point:
    if point is None:
        return None
    x = point.get_x() / img_width
    y = point.get_y() / img_height
    x = int(x * canvas_width)
    y = int(y * canvas_height)
    return Point(x, y)

while True:
    frame = vid.read()[1]
    frame = cv2.flip(frame, 1)  # Espejo para selfie view
    
    hand_detector.setImage(frame)
    hands = hand_detector.findHands(draw=True)

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

        index_finger_point = normalize_finger_position(hand_detector.get_index_finger(hands, 0))
        if index_finger_point is not None:
            if pred.item() > 0.5:
                if first_click:
                    handle_button_down(Event(index_finger_point, ActionType.LEFT_BUTTON_DOWN))
                    first_click = False
                mouse_publisher.notify_click(Event(index_finger_point, ActionType.LEFT_DRAG))
                cv2.putText(frame, "Dibujando", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
                mainFrame.setCursorType(0)
            else:
                first_click = True
                mouse_publisher.clear_subscriber()
                redo_history.clear()
                cv2.putText(frame, "No dibujando", (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)
                mainFrame.setCursorType(1)
            
            # dibujar posición del dedo índice
            mainFrame.setCursorPosition(index_finger_point.get_x(), index_finger_point.get_y())
            cv2.imshow("Hand Tracking", frame)
           
        
    mainFrame.redraw()
    key  = cv2.waitKey(1)
    key_listener.get_command(key).execute()

