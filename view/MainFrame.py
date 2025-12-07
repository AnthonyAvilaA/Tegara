from model.Color import Color
from model.Point import Point
from view.Canvas import Canvas
from model.Clickeable import Clickeable
import numpy as np
import cv2

class MainFrame:
    def __init__(self, width: int = 800, height: int = 600) -> None:
        self.__title = "AirCanvas"
        self.__layers: list[Canvas] = []
        self.__UI: list[Clickeable] = []
        self.__width = width
        self.__height = height
        self.__rotation = 0.0
        self._current_layer = 0
        self.cursor: Point = None
        self.cursor_type = 0  # 0: drawing, 1: pointer
        cv2.namedWindow(self.__title, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.__title, width, height)
        self.redraw()
    
    def redraw(self) -> None:
        image = np.zeros((self.__height, self.__width, 3), dtype=np.uint8)
        for layer in self.__layers:
            self.draw_element(image, layer)
        
        for element in self.__UI:
            self.draw_element(image, element)
        
        if self.cursor is not None:
            self.draw_cursor(image)
            
        cv2.imshow(self.__title, image)

    def draw_element(self, image: np.ndarray, element: Clickeable):
        x = element.get_x()
        y = element.get_y()
        h = element.get_height()
        w = element.get_width()
        # Asegurense que no se salga de los bordes
        if y + h > self.__height or x + w > self.__width:
            print("UI element out of bounds")
            return
        image[y:y+h, x:x+w] = element.get_image()

    def add_cursor_listener(self, listener) -> None:
        cv2.setMouseCallback(self.__title, listener)
        
    def add_layer(self, canva: Canvas) -> None:
        self.__layers.append(canva)
    
    def add_UI_element(self, element: Clickeable) -> None:
        self.__UI.append(element)
    
    def get_number_of_layers(self) -> int:
        return len(self.__layers)
    
    def get_number_of_UI_elements(self) -> int:
        return len(self.__UI)
    
    def get_UI_elements(self) -> list[Clickeable]:
        return self.__UI.copy()
    
    def get_layers(self) -> list[Canvas]:
        return self.__layers.copy()
    
    def remove_layer(self, index: int) -> None:
        if 0 <= index < len(self.__layers):
            del self.__layers[index]
            
    def remove_UI_element(self, element: Clickeable) -> None:
        if element in self.__UI:
            self.__UI.remove(element)
            
    def update_layer(self, index: int, new_layer) -> None:
        if 0 <= index < len(self.__layers):
            self.__layers[index] = new_layer
            
    def get_window_size(self) -> tuple:
        return (self.__width, self.__height)

    def set_actual_layer(self, index: int) -> None:
        if 0 <= index < len(self.__layers):
            self._current_layer = index
    
    def get_current_layer_index(self) -> int:
        return self._current_layer
    
    def setCursorPosition(self, x: int, y: int) -> None:
        self.cursor = Point(x, y)
    
    def setCursorType(self, cursor_type: int) -> None:
        self.cursor_type = cursor_type

    def draw_cursor(self, image: np.ndarray) -> None:
        color = Color(0, 0, 0)
        if self.cursor.get_x() < 0 or self.cursor.get_x() >= self.__width or self.cursor.get_y() < 0 or self.cursor.get_y() >= self.__height:
            return
        if self.cursor_type == 1:
            cv2.circle(image, (self.cursor.get_x(), self.cursor.get_y()), 10, color.get_tuple(), cv2.FILLED)
        else:
            # Diubujar una cruz para el cursor de dibujo
            cv2.line(image, (self.cursor.get_x() - 10, self.cursor.get_y()), (self.cursor.get_x() + 10, self.cursor.get_y()), color.get_tuple(), 2)
            cv2.line(image, (self.cursor.get_x(), self.cursor.get_y() - 10), (self.cursor.get_x(), self.cursor.get_y() + 10), color.get_tuple(), 2)

    def get_element_clicked(self, x: int, y: int) -> Clickeable | None:
        for element in self.__UI:
            if element.check_click(x, y):
                return element
        
        if self.__layers[self._current_layer].check_click(x, y):
            return self.__layers[self._current_layer]
        return None