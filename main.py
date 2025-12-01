from control.MouseListener import MouseListener
from view.Canvas import Canvas
from model.Color import Color
from view.MainFrame import MainFrame
from control.MousePublisher import MousePublisher
from model.Event import Event
from model.ActionType import ActionType
from control.handlers.CanvasHandler import CanvasHandler
from control.Command import Command
from model.Point import Point
import cv2

mainFrame = MainFrame()
mouse_publisher = MousePublisher()
command_history = []
color = Color(0, 0, 0)  # Default color set to black

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
        canvas_handler = CanvasHandler(UIElement, event, color)
        command = canvas_handler.get_command()
        start_command(command)
    
def control_mouse_event(event, x, y, flags, param):
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


mainFrame.add_cursor_listener(control_mouse_event)
mainFrame.add_layer(Canvas(800, 600))

while True:
    mainFrame.redraw()
    if cv2.waitKey(20) & 0xFF == 27:  # Exit on 'ESC' key
        break
    if cv2.waitKey(20) & 0xFF == ord('u'):  # Undo on 'u' key
        if command_history:
            last_command = command_history.pop()
            last_command.undo()

cv2.destroyAllWindows()
