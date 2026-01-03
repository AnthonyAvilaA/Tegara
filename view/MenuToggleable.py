from view.Menu import Menu
from view.MenuIcon import MenuIcon
from view.ToggleableUI import ToggleableUI
from model.Point import Point
from model.Color import COLOR_WHITE, Color
from definitions.Tools import Tools
import numpy as np
import cv2

class MenuToggleable(ToggleableUI[Menu]):
    def __init__(self, point: Point, width: int, height: int, menu: Menu, toggled_on: bool = False, color: Color = Color(255, 255, 255, 150)) -> None:
        super().__init__(point, width, height, None, menu, toggled_on)
        self.__border_color = color.get_tuple()
        super().set_image(self.create_image())
    
    def is_opaque(self):
        return False

    def create_image(self) -> np.ndarray:
        """Crea una imagen simple para representar el menú cuando está colapsado"""
        height = super().get_height()
        width = super().get_width()
        image = np.zeros((height, width, 4), dtype=np.uint8)
        
        # Dibujar una doble flecha apuntado a la derecha
        cv2.line(image, (int(width * 0.25), int(height * 0.1)), (int(width * 0.45), int(height * 0.5)), self.__border_color, 3)
        cv2.line(image, (int(width * 0.25), int(height * 0.8)), (int(width * 0.45), int(height * 0.5)), self.__border_color, 3)
        
        cv2.line(image, (int(width * 0.55), int(height * 0.1)), (int(width * 0.75), int(height * 0.5)), self.__border_color, 3)
        cv2.line(image, (int(width * 0.55), int(height * 0.8)), (int(width * 0.75), int(height * 0.5)), self.__border_color, 3)

        # Borde
        cv2.rectangle(image, (0, 0), (width - 1, height - 1), self.__border_color, 2)
        
        return image
    
    def get_icon_clicked(self, point: Point) -> MenuIcon | None:
        """Delega al menú si está expandido"""
        element = super().get_element()
        if super().is_toggled_on():
            return element.get_icon_clicked(point)
        return None
    
    def add_element(self, icon) -> None:
        """Agrega un icono al menú subyacente"""
        element: Menu = super().get_element()
        element.add_element(icon)
    
    def set_tool(self, tool: Tools) -> None:
        """Establece la herramienta activa en el menú subyacente"""
        element: Menu = super().get_element()
        element.set_tool(tool.value)

    def get_tool(self) -> Tools:
        """Obtiene la herramienta activa del menú subyacente"""
        element: Menu = super().get_element()
        tool_index = element.get_tool()  # Acceso al atributo privado
        if tool_index == 0:
            return Tools.PENCIL
        elif tool_index == 1:
            return Tools.ERASER
        elif tool_index == 2:
            return Tools.FILL
        
        return None