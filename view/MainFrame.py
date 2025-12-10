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
        self.hand_data: list[Point] = []
        self.cursor_type = 0  # 0: drawing, 1: pointer
        self.needs_redraw = True
        cv2.namedWindow(self.__title, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.__title, width, height)
        self.redraw()
    
    def redraw(self) -> None:
        self.check_redraw()
        if not self.needs_redraw:
            return
        image = np.full((self.__height, self.__width, 4), 255, dtype=np.uint8)
        for layer in self.__layers:
            self.draw_element(image, layer)
        
        for element in self.__UI:
            self.draw_element(image, element)
        
        if self.cursor is not None:
            self.draw_cursor(image)
        
        for point in self.hand_data:
            cv2.circle(image, (point.get_x(), point.get_y()), 5, Color(255, 0, 0).get_tuple(), cv2.FILLED)
            
        cv2.imshow(self.__title, image)

    def check_redraw(self) -> bool:
        for element in self.__UI:
            print("Checking UI element dirty:", element)
            if element.is_dirty():
                self.needs_redraw = True
                return True
        self.needs_redraw = False
        return False
    
    def draw_element(self, image: np.ndarray, element: Clickeable):
        point = element.get_origin_point()
        h = element.get_height()
        w = element.get_width()

        # Asegurar que no se salga
        if point.get_y() + h > self.__height or point.get_x() + w > self.__width:
            print("UI element out of bounds", point, (w, h))
            return
        
        element_img = element.get_image()

        if np.any(element_img[..., : 4] < 255):    
            # Recorte de zona destino
            roi = image[point.get_y():point.get_y()+h, point.get_x():point.get_x()+w]
            # Alpha blend
            element_img = self.alpha_blend(roi, element_img)

        # Copiar resultado
        image[point.get_y():point.get_y()+h, point.get_x():point.get_x()+w] = element_img
    
    def alpha_blend(self, bg, fg):
        # 1. Extract alpha channel and expand dimensions for broadcasting
        # Shape becomes (H, W, 1) so it can multiply against (H, W, 3)
        alpha = fg[..., 3].astype(np.uint16)[..., None]
        inv_alpha = 255 - alpha

        # 2. Extract RGB channels and convert to uint16 to prevent overflow
        fg_rgb = fg[..., :3].astype(np.uint16)
        bg_rgb = bg[..., :3].astype(np.uint16)

        # 3. Perform blending using integer math
        # Formula: (FG * Alpha + BG * (255 - Alpha)) / 255
        out_rgb = (fg_rgb * alpha + bg_rgb * inv_alpha) // 255

        # 4. Calculate resulting alpha (usually just keeping the highest alpha or saturated add)
        # Simple approach: max alpha or saturated addition. 
        # Here we just keep 255 (opaque) since the canvas is usually opaque.
        # However, to be mathematically correct like your previous function:
        fg_a = fg[..., 3].astype(np.uint16)
        bg_a = bg[..., 3].astype(np.uint16)
        out_alpha = (fg_a + bg_a * (255 - fg_a) // 255)[..., None]

        # 5. Concatenate and cast back to uint8
        return np.concatenate((out_rgb, out_alpha), axis=2).astype(np.uint8)

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
    
    def set_cursor_position(self, point: Point) -> None:
        self.cursor = point
    
    def set_cursor_type(self, cursor_type: int) -> None:
        self.cursor_type = cursor_type
    
    def set_hand(self, hand_data: list[Point]) -> None:
        self.hand_data = hand_data

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

    def get_element_clicked(self, point: Point) -> Clickeable | None:
        for element in self.__UI:
            if element.check_click(point):
                return element
        
        if self.__layers[self._current_layer].check_click(point):
            return self.__layers[self._current_layer]
        return None