import cv2
from model.Clickeable import Clickeable

class MainFrame:
    def __init__(self):
        self.__title = "AirCanvas"
        self.__layers = []
        self.__UI = []
        cv2.namedWindow(self.__title, cv2.WINDOW_AUTOSIZE)
        cv2.resizeWindow(self.__title, 800, 600)
        self.redraw()
    
    def redraw(self) -> None:
        for layer in self.__layers:
            cv2.imshow(self.__title, layer)
        
        for element in self.__UI:
            cv2.imshow(self.__title, element.get_image())

    def add_cursor_listener(self, listener) -> None:
        cv2.setMouseCallback(self.__title, listener)
        
    def add_layer(self) -> None:
        self.__layers.append(list())
    
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