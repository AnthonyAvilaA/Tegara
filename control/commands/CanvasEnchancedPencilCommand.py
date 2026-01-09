
from control.commands.CanvasDrawCommand import CanvasDrawCommand
from model.Point import Point
from model.Color import Color
from view.Canvas import Canvas
import numpy as np
from ultralytics import YOLO
import cv2
from model.SketchTool import SketchTool
from model.Sketches import sketches

class CanvasEnchancedPencilCommand(CanvasDrawCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.memory = []
        self.model = YOLO("../yolo.pt")

    def undo(self):
        if self.memory:
            self._canvas.set_image(self.memory.pop())

    def clear_canvas_area(self, x0, y0, x1, y1):
        image = self._canvas.get_image()
        image[y0:y1, x0:x1] = np.array([255, 255, 255, 255], dtype=np.uint8)

    def get_matched_box(self, conf_threshold=0.35):
        rgba_image = self._canvas.get_image()
        rg_image = self.rgba_to_white_bg(rgba_image)
        rgb_image = cv2.cvtColor(rg_image, cv2.COLOR_RGBA2RGB)

        results = self.model(
            source=rgb_image,
            conf=conf_threshold,
            verbose=False
        )
        return results

    def draw_sketch_on_canvas(self):
        print("Drawing detected sketch on canvas...")
        results = self.get_matched_box()
        for r in results:
            boxes = r.boxes
            names = r.names
            
            for box in boxes:
                # Bounding box
                x1, y1, x2, y2 = map(int, box.xyxy[0])

                # Clase detectada
                cls_id = int(box.cls[0])
                label = names[cls_id]
                print(f"Detected sketch: {label}")

                matched_sketch = sketches.get(label)
                if not matched_sketch:
                    continue

                # Guardar estado para undo
                self.memory.append(self._canvas.get_image().copy())

                # Limpiar zona detectada
                self.clear_canvas_area(x1, y1, x2, y2)

                # Dibujar sketch
                sketch = SketchTool(matched_sketch)
                sketch.draw_on_canvas(
                    self._canvas.get_image(),
                    box=(x1, y1, x2, y2),
                    color=Color(0, 0, 0),
                    thickness=self._draw_size
                )
                return
    
    def rgba_to_white_bg(self, rgbA_img: np.ndarray) -> np.ndarray:
        """
        Convierte una imagen RGBA con transparencia
        a RGB con fondo blanco.
        """
        # Separar canales
        rgb = rgbA_img[..., :3].astype(np.float32)
        alpha = rgbA_img[..., 3].astype(np.float32) / 255.0  # [0,1]

        # Fondo blanco
        white_bg = np.ones_like(rgb) * 255

        # Alpha blending: out = fg * a + bg * (1 - a)
        out = rgb * alpha[..., None] + white_bg * (1 - alpha[..., None])

        return out.astype(np.uint8)
