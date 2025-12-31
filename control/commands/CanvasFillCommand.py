from numpy import ndarray
from collections import deque
from control.commands.Command import Command
from model.Point import Point
from model.Color import Color
from view.Canvas import Canvas
from model.CanvasPixel import CanvasPixel 
import numpy as np


class CanvasFillCommand(Command):
    def __init__(self, canvas: Canvas, color: Color, position: Point) -> None:
        self.__canvas: Canvas = canvas
        self.__color: Color = color
        self.__position: Point = position
        self.__changed_pixels: set[CanvasPixel] = set()
    
    def execute(self):
        if self.__changed_pixels:
            self.redo()
            return
            
        image = self.__canvas.get_image()
        self.__flood_fill(self.__position, image)
        self.__canvas.set_image(image)
    
    def redo(self):
        image = self.__canvas.get_image()
        target_color_list = self.__color.get_list()
        for pixel in self.__changed_pixels:
            image[pixel.get_y(), pixel.get_x()] = target_color_list
        self.__canvas.set_image(image)

    def undo(self):
        image = self.__canvas.get_image()
        for pixel in self.__changed_pixels:
            image[pixel.get_y(), pixel.get_x()] = pixel.color.get_list()
        self.__canvas.set_image(image)

    def __flood_fill(self, start_point: Point, image: ndarray) -> None:
        h, w, _ = image.shape
        sx, sy = start_point.get_x(), start_point.get_y()

        if not (0 <= sx < w and 0 <= sy < h):
            return

        original_color = image[sy, sx].copy()
        target_color = np.array(self.__color.get_list(), dtype=image.dtype)

        if np.array_equal(original_color, target_color):
            return

        original_mask = np.all(image == original_color, axis=2)
        visited = np.zeros((h, w), dtype=bool)

        stack = deque([(sx, sy)])

        while stack:
            x, y = stack.pop()

            if not original_mask[y, x]:
                continue

            # expand left
            left = x
            while left > 0 and original_mask[y, left - 1]:
                left -= 1

            # expand right
            right = x
            while right < w - 1 and original_mask[y, right + 1]:
                right += 1

            # fill scanline
            for i in range(left, right + 1):
                if visited[y, i]:
                    continue
                
                orig = image[y, i].copy()
                r, g, b, a = orig.tolist()

                self.__changed_pixels.add(
                    CanvasPixel(Point(i, y), Color(r, g, b, a))
                )

                visited[y, i] = True
                original_mask[y, i] = False
                image[y, i] = target_color

                if y > 0 and original_mask[y - 1, i]:
                    stack.append((i, y - 1))
                if y < h - 1 and original_mask[y + 1, i]:
                    stack.append((i, y + 1))

