import math
from view.ToggleableUI import ToggleableUI
from view.Canvas import Canvas
from model.Point import Point
from model.Color import COLOR_WHITE, Color, COLOR_BLACK
from view.Clickeable import Clickeable
from control.MouseListener import MouseListener
from screeninfo import get_monitors
import numpy as np
import cv2
from control.PointTranslator import PointTranslator

class MainFrame:
    def __init__(self, width: int = 800, height: int = 600) -> None:
        self.__title = "Tegara"
        self.__layers: list[Canvas] = []
        self.__UI: list[Clickeable] = []
        self.__rotation_level = 0
        
        self.__width = width
        self.__height = height
        self.__current_layer = 0
        self.__image = np.full((height, width, 4), 255, dtype=np.uint8)
        self.__cursor: Point = None
        self.__hand_data: list[Point] = []
        self.__zoom_level = 1.0
        self.__cursor_type = 0  # 0: drawing, 1: pointer
        cv2.namedWindow(self.__title, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.__title, width, height)
        cv2.namedWindow(self.__title, cv2.WINDOW_GUI_NORMAL | cv2.WINDOW_NORMAL)
        cv2.setWindowProperty(self.__title, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

        self.redraw()

    def redraw(self) -> None:
        if self.needs_redraw():
            image_to_draw_on = np.full((self.__height, self.__width, 4), 135, dtype=np.uint8)
            
            x, y = self.__width // 2, self.__height // 2
            for layer in self.__layers:
                layer.set_origin_point(Point(x, y))
                self.draw_element(image_to_draw_on, layer)
            
            for element in self.__UI:
                self.draw_element(image_to_draw_on, element)

            self.__image = image_to_draw_on
        
        image_display = self.__image.copy()   

        for point in self.__hand_data:
            cv2.circle(image_display, (point.get_x(), point.get_y()), 5, (0, 0, 255, 255), cv2.FILLED)
        
        if self.__cursor is not None:
            self.draw_cursor(image_display)
        
        cv2.imshow(self.__title, image_display)

    def needs_redraw(self) -> bool:
        for element in self.__UI:
            if element.is_dirty():
                element.clear_dirty()
                return True
        for element in self.__layers:
            if element.is_dirty():
                element.clear_dirty()
                return True
        return False
    
    
    def draw_element(self, image: np.ndarray, element: Clickeable):
        point: Point = element.get_origin_point()

        if isinstance(element, Canvas):
            angle = math.radians(self.__rotation_level)

            bb_w, bb_h = self.rotated_bounding_box(element.get_width(), element.get_height(), angle)
            rotated = self.render_rotated_canvas(element, self.__rotation_level, bb_w, bb_h)

            # Recorte seguro a la ventana
            cx = point.get_x() - bb_w // 2
            cy = point.get_y() - bb_h // 2

            x0 = max(cx, 0)
            y0 = max(cy, 0)
            x1 = min(cx + bb_w, self.__width)
            y1 = min(cy + bb_h, self.__height)


            if x0 >= x1 or y0 >= y1:
                return

            roi = image[y0:y1, x0:x1]

            rx0 = x0 - cx
            ry0 = y0 - cy
            rx1 = rx0 + (x1 - x0)
            ry1 = ry0 + (y1 - y0)

            blended = self.alpha_blend(roi, rotated[ry0:ry1, rx0:rx1])

            image[y0:y1, x0:x1] = blended
            return

        # --- Caso normal ---
        h = element.get_height()
        w = element.get_width()
        element_img = element.get_image()

        if not element.is_opaque():
            roi = image[point.get_y():point.get_y()+h, point.get_x():point.get_x()+w]
            element_img = self.alpha_blend(roi, element_img)

        image[point.get_y():point.get_y()+h, point.get_x():point.get_x()+w] = element_img

    def alpha_blend(self, bg: np.ndarray, fg: np.ndarray) -> np.ndarray:
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

    def add_cursor_listener(self, listener: MouseListener) -> None:
        cv2.setMouseCallback(self.__title, listener)
        
    def add_layer(self, canva: Canvas) -> None:
        self.__layers.append(canva)
    
    def remove_layer(self, index: int) -> None:
        if index == -1:
            index = len(self.__layers) - 1

        if 0 <= index < len(self.__layers) and len(self.__layers) > 1:
            removed_layer = self.__layers.pop(index)

            if self.__current_layer >= len(self.__layers):
                self.__current_layer = max(0, len(self.__layers) - 1)
        
        self.__layers[self.__current_layer].set_dirty()
    
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
            self.__current_layer = index
    
    def get_current_layer_index(self) -> int:
        return self.__current_layer
    
    def set_current_layer(self, index: int) -> None:
        if 0 <= index < len(self.__layers):
            self.__current_layer = index
    
    def set_cursor_position(self, point: Point) -> None:
        self.__cursor = point
    
    def set_cursor_type(self, cursor_type: int) -> None:
        self.__cursor_type = cursor_type
    
    def set_hand(self, hand_data: list[Point]) -> None:
        self.__hand_data = hand_data
    
    def get_hand_points(self) -> list[Point]:
        return list(self.__hand_data)

    def get_title(self) -> str:
        return self.__title

    def get_title(self) -> str:
        return self.__title
    
    def get_rotation_level(self) -> float:
        return self.__rotation_level
    
    def set_rotation_level(self, rotation: float) -> None:
        self.__rotation_level = rotation
        self.__layers[self.__current_layer].set_dirty()

    def draw_cursor(self, image: np.ndarray) -> None:
        color = COLOR_BLACK
        if self.__cursor.get_x() < 0 or self.__cursor.get_x() >= self.__width or self.__cursor.get_y() < 0 or self.__cursor.get_y() >= self.__height:
            return
        if self.__cursor_type == 1:
            cv2.circle(image, (self.__cursor.get_x(), self.__cursor.get_y()), 10, color.get_tuple(), cv2.FILLED)
        else:
            # Diubujar una cruz para el cursor de dibujo
            cv2.line(image, (self.__cursor.get_x() - 10, self.__cursor.get_y()), (self.__cursor.get_x() + 10, self.__cursor.get_y()), color.get_tuple(), 2)
            cv2.line(image, (self.__cursor.get_x(), self.__cursor.get_y() - 10), (self.__cursor.get_x(), self.__cursor.get_y() + 10), color.get_tuple(), 2)

    def get_element_selected(self, point: Point) -> Clickeable | None:
        for element in self.__UI:
            if element.check_click(point):
                return element
        
        canvas_point = PointTranslator.window_to_canvas(point, self.__rotation_level, self.__layers[self.__current_layer], self.__zoom_level)

        if self.__layers[self.__current_layer].check_click(canvas_point):
            print(self.__current_layer)
            return self.__layers[self.__current_layer]
        return None
    
    def rotated_bounding_box(self, w: int, h: int, angle_rad: float) -> tuple[int, int]:
        cos_a = abs(math.cos(angle_rad))
        sin_a = abs(math.sin(angle_rad))

        base_w = w * self.__zoom_level
        base_h = h * self.__zoom_level

        new_w = int(base_w * cos_a + base_h * sin_a)
        new_h = int(base_w * sin_a + base_h * cos_a)
        
        return new_w, new_h

    def render_rotated_canvas(self, canvas: Canvas, rotation_deg: float, target_w: int, target_h: int) -> np.ndarray:
        src = canvas.get_image()
        (h, w) = src.shape[:2]
        center = (w // 2, h // 2)

        # 1. Generar la matriz de rotación (OpenCV usa sentido antihorario por defecto)
        # Usamos -rotation_deg si quieres que coincida con tu lógica previa
        M = cv2.getRotationMatrix2D(center, rotation_deg, self.__zoom_level)

        # 2. Ajustar la traslación en la matriz para que el centro del canvas 
        # original coincida con el centro del target (bounding box)
        M[0, 2] += (target_w / 2) - center[0]
        M[1, 2] += (target_h / 2) - center[1]

        # 3. Aplicar la transformación de una sola vez
        return cv2.warpAffine(
            src, 
            M, 
            (target_w, target_h), 
            flags=cv2.INTER_LINEAR, 
            borderMode=cv2.BORDER_CONSTANT, 
            borderValue=(0, 0, 0, 0) # Transparente fuera de los límites
        )

    def get_zoom_level(self) -> float:
        return self.__zoom_level

    def zoom_in(self, factor: float = 0.1) -> None:
        self.__zoom_level += factor
        if self.__zoom_level > 5.0:
            self.__zoom_level = 5.0
        self.__layers[self.__current_layer].set_dirty()
    
    def zoom_out(self, factor: float = 0.1) -> None:
        self.__zoom_level -= factor
        if self.__zoom_level < 0.1:
            self.__zoom_level = 0.1
        self.__layers[self.__current_layer].set_dirty()