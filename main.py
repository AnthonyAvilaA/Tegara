from view.MainFrame import MainFrame
import cv2

mainFrame = MainFrame()

def control_mouse_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"Mouse clicked at ({x}, {y})")
        
mainFrame.add_cursor_listener(control_mouse_event)

while True:
    mainFrame.redraw()
    if cv2.waitKey(20) & 0xFF == 27:  # Exit on 'ESC' key
        break