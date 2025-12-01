from model.Canvas import Canvas
from model.Clickeable import Clickeable
import numpy as np
import cv2

class MainFrame:
    def __init__(self, width: int = 800, height: int = 600) -> None:
        self.__title = "AirCanvas"
        self.__layers = []
        self.__UI = []
        self.__width = width
        self.__height = height
        self.__rotation = 0.0
        self.__actual_layer = 0
        cv2.namedWindow(self.__title, cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(self.__title, width, height)
        self.redraw()
    
    def redraw(self) -> None:
        image = np.zeros((self.__height, self.__width, 3), dtype=np.uint8)
        for layer in self.__layers:
            image = cv2.addWeighted(image, 1, layer.get_image(), 1, 0)
        
        for element in self.__UI:
            element_image = element.get_image()
            center_x, center_y = element._center
            img_height, img_width = element_image.shape[:2]
            top_left_x = center_x - img_width // 2
            top_left_y = center_y - img_height // 2
            image[top_left_y:top_left_y + img_height, top_left_x:top_left_x + img_width] = cv2.addWeighted(
                image[top_left_y:top_left_y + img_height, top_left_x:top_left_x + img_width], 1,
                element_image, 1, 0)
        cv2.imshow(self.__title, image)

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
    
    def get_UI_elements(self) -> list:
        return self.__UI.copy()
    
    def get_layers(self) -> list:
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
            self.__actual_layer = index
    
    def get_actual_layer(self) -> int:
        return self.__actual_layer

    def get_element_clicked(self, x: int, y: int) -> Clickeable | None:
        for element in self.__UI:
            if element.check_click(x, y):
                return element
        
        if self.__layers[self.__actual_layer].check_click(x, y):
            return self.__layers[self.__actual_layer]
        return None