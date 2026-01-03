
from control.commands.Command import Command
from model.Point import Point
from model.Color import Color
from view.Canvas import Canvas
import numpy as np
from ultralytics import YOLO
import cv2
from model.SketchTool import SketchTool
from model.Sketches import sketches

class CanvasEnchancedPencilCommand(Command):
    def __init__(self, canvas: Canvas, draw_size: int):
        self.__canvas: Canvas = canvas
        self.__draw_size: int = draw_size
        self.memory = []
        self.model = YOLO("../yolo.pt")
        
    def undo(self):
        if self.memory:
            self.__canvas.set_image(self.memory.pop())
        return

    def execute(self):
        results = self.get_matched_box()
        for r in results:
            boxes = r.boxes
            names = r.names

            for box in boxes:
                # Bounding box (xyxy)
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Clase
                cls_id = int(box.cls[0])
                label = names[cls_id]
                matched_sketch = sketches.get(label)
                
                if matched_sketch:
                    self.memory.append(self.__canvas.get_image().copy())
                    sketch = SketchTool(matched_sketch)
                    self.clear_canvas_area(x1, y1, x2, y2)
                    sketch.draw_on_canvas(
                        self.__canvas.get_image(),
                        box=(x1, y1, x2, y2),
                        color=Color(0, 0, 0),
                        thickness=self.__draw_size
                    )
        return
    
    def clear_canvas_area(self, x0, y0, x1, y1):
        self.__canvas.get_image()[y0:y1, x0:x1] = np.array([255, 255, 255, 255], dtype=np.uint8)
        
    def get_matched_box(self, CONF_THRESHOLD=0.35):
        rgba_image = self.__canvas.get_image()
        rgb_image = cv2.cvtColor(rgba_image, cv2.COLOR_RGBA2RGB)
        results = self.model(
            source=rgb_image,
            conf=CONF_THRESHOLD
        )
        return results
