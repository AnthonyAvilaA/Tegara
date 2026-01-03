from view.Clickeable import Clickeable
from model.Point import Point
import numpy as np
import definitions.tools as Tools
import cv2

class MenuIcon(Clickeable):
    def __init__(self, origin: Point, type: Tools, width: int, height: int, image_src: str) -> None:
        self.origin = origin
        self.__image: np.ndarray
        self.__is_dirty = True
        self.__image = cv2.imread(image_src, cv2.IMREAD_UNCHANGED)
        self.__type = type
        if self.__image is None:
            raise FileNotFoundError(f"Image file not found: {image_src}")
        
        self.__image = cv2.resize(self.__image, (width, height))
        if self.__image.shape[2] == 3:
            b_channel, g_channel, r_channel = cv2.split(self.__image)
            alpha_channel = np.ones(b_channel.shape, dtype=b_channel.dtype) * 255
            self.__image = cv2.merge((b_channel, g_channel, r_channel, alpha_channel))
        
        # colorear el fondo transparente de blanco
        for y in range(self.__image.shape[0]):
            for x in range(self.__image.shape[1]):
                if self.__image[y, x, 3] == 0:
                    self.__image[y, x] = [255, 255, 255, 255]

    def is_opaque(self) -> bool:
        return True

    def get_origin_point(self) -> Point:
        return self.origin
    
    def is_dirty(self) -> bool:
        return self.__is_dirty
    
    def set_dirty(self) -> None:
        self.__is_dirty = True
    
    def clear_dirty(self) -> None:
        self.__is_dirty = False

    def get_image(self) -> np.ndarray:
        return self.__image
    
    def check_click(self, point: Point) -> bool:
        img_width = self.__image.shape[1]
        img_height = self.__image.shape[0]
        if (self.origin.get_x() <= point.get_x() <= self.origin.get_x() + img_width and
            self.origin.get_y() <= point.get_y() <= self.origin.get_y() + img_height):
            return True
        return False
    
    def get_width(self) -> int:
        return self.__image.shape[1]

    def get_height(self) -> int:
        return self.__image.shape[0]

    def get_type(self) -> Tools:
        return self.__type