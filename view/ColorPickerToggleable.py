from turtle import color
from control.CommandHandler import CommandHandler
from view.ColorPicker import ColorPicker
from view.ToggleableUI import ToggleableUI
from model.Point import Point
from model.Color import Color
import numpy as np
import cv2

class ColorPickerToggleable(ToggleableUI[ColorPicker]):
    def __init__(self, point: Point, width: int, height: int, color_picker: ColorPicker, color: Color = Color(0,0,0), toggled_on: bool = False) -> None:
        super().__init__(point, width, height, None, color_picker, toggled_on)
        self.color = color
        super().set_image(self.create_image())
    
    """
    def create_image(self) -> np.ndarray:
        height = super().get_height()
        width = super().get_width()
        image = np.zeros((height, width, 4), dtype=np.uint8)

        text = "Color"
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 1

        # 1. calcular fontScale óptimo
        font_scale, (tw, th) = self.fit_text_to_box(text, width, height, font, thickness)

        # 2. centrar el texto
        x = (width - tw) // 2
        y = (height + th) // 2
        
        # 3. dibujar texto y borde
        cv2.putText(image, text, (x, y), font, font_scale, (100, 100, 100, 255), thickness)
        cv2.rectangle(image, (0, 0), (width - 1, height - 1), (100, 100, 100, 255), 2)

        return image

    
    def fit_text_to_box(self, text, box_width, box_height, font=cv2.FONT_HERSHEY_SIMPLEX, thickness=2, margin=10):
        max_width = box_width - margin*2
        max_height = box_height - margin*2

        font_scale = 1.0

        # Ajuste descendente hasta que encaje
        while font_scale > 0:
            (text_width, text_height), _ = cv2.getTextSize(text, font, font_scale, thickness)
            if text_width <= max_width and text_height <= max_height:
                return font_scale, (text_width, text_height)
            font_scale -= 0.01  # reduce hasta encajar

        return 0.5, cv2.getTextSize(text, font, 0.5, thickness)[0]  # fallback
    """

    def is_opaque(self):
        return False

    def create_image(self) -> np.ndarray:
        height = super().get_height()
        width = super().get_width()
        image = np.zeros((height, width, 4), dtype=np.uint8)
        r, g, b, a = self.color.get_tuple()
        cv2.circle(image, (width // 2, height // 2), min(width, height) // 3, (r, g, b, 155), -1)
        cv2.circle(image, (width // 2, height // 2), min(width, height) // 3, (0,0,0,155), 3)
        return image
    
    def update_color(self, color: Color) -> None:
        if color is None:
            return
        self.color = color
        super().set_image(self.create_image())

    def get_color_at(self, point: Point) -> Color:
        element = super().get_element()
        if super().is_toggled_on():
            return element.get_color_at(point)
        return None