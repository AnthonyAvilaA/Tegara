from numpy import ndarray
from collections import deque
from control.commands.Command import Command
from model.Point import Point
from model.Color import Color
from view.Canvas import Canvas
from model.CanvasPixel import CanvasPixel
import numpy as np


class CanvasColorPickerCommand(Command):
    def __init__(self, canvas: Canvas, position: Point) -> None:
        self.__canvas: Canvas = canvas
        self.__position: Point = position
        self.__color = None

    def redo(self):
        pass

    def undo(self):
        pass
    
    def execute(self):
        self.__color =  self.__canvas.get_color_at(self.__position)
    
    def get_color_selected(self) -> Color:
        return self.__color