from view.MenuIcon import MenuIcon
from view.Clickeable import Clickeable
from model.Color import COLOR_BLACK, COLOR_BLUE, Color
from model.Point import Point
import numpy as np
import cv2

class Menu(Clickeable):
    def __init__(self, origin: Point, color: Color, border_width: int, is_vertical: bool = True, vertical_padding: int = 0, horizontal_padding: int = 0) -> None:
        self.origin = origin
        self.elements: list[Clickeable] = []
        self.__is_dirty = True
        self.color = color
        self.border_width = border_width
        self.is_vertical = is_vertical
        self.vertical_padding = vertical_padding
        self.horizontal_padding = horizontal_padding
        self.tool_selected = 0
        self.__set_image()
        self.set_dirty()
    
    def get_image(self) -> np.ndarray:
        return self.__image

    def is_opaque(self) -> bool:
        return True
    
    def is_dirty(self) -> bool:
        return self.__is_dirty
    
    def clear_dirty(self) -> None:
        self.__is_dirty = False

    def set_dirty(self) -> None:
        self.__is_dirty = True
    
    def get_origin_point(self) -> Point:
        return self.origin
    
    def check_click(self, point: Point) -> bool:
        menu_width = self.__image.shape[1]
        menu_height = self.__image.shape[0]
        if (self.origin.get_x() <= point.get_x() <= self.origin.get_x() + menu_width and
            self.origin.get_y() <= point.get_y() <= self.origin.get_y() + menu_height):
            return True
        return False

    def get_icon_clicked(self, point: Point) -> MenuIcon | None:
        #if not self.check_click(point): #inferido
        #    return None

        relative_x = point.get_x() - self.origin.get_x()
        relative_y = point.get_y() - self.origin.get_y()

        current_x = 0
        current_y = 0

        for i, element in enumerate(self.elements):
            elem_image = element.get_image()
            h, w = elem_image.shape[:2]
            
            start_x = current_x + self.horizontal_padding // 2
            start_y = current_y + self.vertical_padding // 2

            if (start_x <= relative_x <= start_x + w and
                start_y <= relative_y <= start_y + h):
                self.tool_selected = i
                self.__set_image()
                self.set_dirty()
                return element

            if self.is_vertical:
                current_y += h + self.vertical_padding
            else:
                current_x += w + self.horizontal_padding
        
        return None
    
    def get_width(self) -> int:
        return self.__image.shape[1]

    def get_height(self) -> int:
        return self.__image.shape[0]

    def add_element(self, element: Clickeable) -> None:
        self.elements.append(element)
        self.__set_image()
        self.set_dirty()
    
    def __set_image(self) -> None:
            self.__image: np.ndarray = np.full((1, 1, 4), self.color.get_tuple(), dtype=np.uint8)
            total_width = 0
            total_height = 0
            max_width = 0
            max_height = 0
            for element in self.elements:
                elem_image = element.get_image()
                h, w = elem_image.shape[:2]
                if self.is_vertical:
                    total_height += h + self.vertical_padding
                    max_width = max(max_width, w)
                else:
                    total_width += w + self.horizontal_padding
                    max_height = max(max_height, h)

            if self.is_vertical:
                total_width = max_width + self.horizontal_padding
            else:
                total_height = max_height + self.vertical_padding

            if total_width <= 0 or total_height <= 0:
                return

            menu_image = np.full((total_height, total_width, 4), self.color.get_tuple(), dtype=np.uint8)
            current_x = 0
            current_y = 0

            for i, element in enumerate(self.elements):
                elem_image = element.get_image()
                h, w = elem_image.shape[:2]
                
                start_x = current_x + self.horizontal_padding // 2
                start_y = current_y + self.vertical_padding // 2
                menu_image[start_y:start_y + h, start_x:start_x + w] = elem_image
                
                border_color = COLOR_BLACK.get_tuple()
                if i == self.tool_selected:
                    border_color = COLOR_BLUE.get_tuple()
                cv2.rectangle(menu_image, (start_x - 2, start_y - 2), (start_x + w + 1, start_y + h + 1), border_color, 2)

                if self.is_vertical:
                    current_y += h + self.vertical_padding
                else:
                    current_x += w + self.horizontal_padding
                cv2.rectangle(menu_image, (0, 0), (total_width - 1, total_height - 1), (0, 0, 0, 255), self.border_width)

            self.__image = menu_image
            self.set_dirty()