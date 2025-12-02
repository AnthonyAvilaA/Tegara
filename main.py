from control.MouseListener import MouseListener
from control.commands.ExitCommand import ExitCommand
from control.commands.NoneCommand import NoneCommand
from control.commands.UndoCommand import UndoCommand
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

mainFrame = MainFrame()
mouse_publisher = MousePublisher()
command_history = []
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
        command_history.append(command)
        if isinstance(command, MouseListener):
            mouse_publisher.set_subscriber(command)
            
def handle_button_down(event: Event):
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
    
    if event == cv2.EVENT_MOUSEWHEEL:
        change_draw_size(flags)

mainFrame.add_cursor_listener(control_mouse_event)
mainFrame.add_layer(Canvas(800, 600))
color_picker = ColorPicker(0, 400, 200, 200)
mainFrame.add_UI_element(color_picker)

key_listener = KeyHandler()
key_listener.add_command_for_key(ExitCommand(), Key.ESC)
key_listener.add_command_for_key(UndoCommand(command_history), Key.CTRL_Z, Key.U)
key_listener.add_command_for_key(NoneCommand(), Key.NONE)

while True:
    mainFrame.redraw()
    key_listener.get_command(cv2.waitKey(1)).execute()

