

from paddleocr import PaddleOCR
import cv2
import numpy as np
import time
from PIL import Image, ImageDraw, ImageFont

from control.commands.CanvasDrawCommand import CanvasDrawCommand

def get_bbox_from_strokes(canvas_rgba):
    rgb = cv2.cvtColor(canvas_rgba, cv2.COLOR_RGBA2RGB)
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    mask = gray < 250  # detecta trazo

    coords = np.column_stack(np.where(mask))
    if coords.size == 0:
        return None, None

    y_coords, x_coords = coords[:, 0], coords[:, 1]

    bbox = (
        x_coords.min(),
        y_coords.min(),
        x_coords.max(),
        y_coords.max()
    )

    roi = rgb[bbox[1]:bbox[3]+1, bbox[0]:bbox[2]+1]
    return roi, bbox


def add_padding(roi, pad=20, color=255):
    """
    roi: imagen (H, W, C) o (H, W)
    pad: píxeles de padding por lado
    color: color del padding (255 = blanco)
    """
    if roi is None or roi.size == 0:
        return None

    if len(roi.shape) == 3:
        h, w, c = roi.shape
        padded = np.full(
            (h + 2*pad, w + 2*pad, c),
            color,
            dtype=roi.dtype
        )
        padded[pad:pad+h, pad:pad+w] = roi
    else:
        h, w = roi.shape
        padded = np.full(
            (h + 2*pad, w + 2*pad),
            color,
            dtype=roi.dtype
        )
        padded[pad:pad+h, pad:pad+w] = roi

    return padded


class CanvasTextDetectionCommand():
    def __init__(self):
        self.reader = None
        self._get_reader()

    def _get_reader(self):
        if self.reader is None:
            self.reader = PaddleOCR(
                lang='ch',
                ocr_version='PP-OCRv4'
            )
        
    def detect(self, image):
        start = time.time()
        
        image = self.rgba_to_white_bg(image)
        roi, bbox = get_bbox_from_strokes(image)
        roi = add_padding(roi, pad=80, color=255)

        if roi is None:
            print("No text regions detected.")
            return [], None
        results = self.reader.predict(roi)

        for page in results:
            texts = page.get("rec_texts", [])
            scores = page.get("rec_scores", [])

            for text, score in zip(texts, scores):
                print(f"Texto: {text} | Confianza: {score:.2f}")
                
        print(f"PaddleOCR detection time: {time.time() - start} seconds {roi.shape}")
        return texts, bbox
    
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
    
    

class CanvasTxtCommand(CanvasDrawCommand):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.memory = []

    def undo(self):
        if self.memory:
            self._canvas.set_image(self.memory.pop())

    def clear_canvas_area(self, x0, y0, x1, y1):
        image = self._canvas.get_image()
        image[y0:y1, x0:x1] = np.array([255, 255, 255, 255], dtype=np.uint8)

    def draw_text_fit_bbox_pil(self, text, bbox):
        self.memory.append(self._canvas.get_image().copy())
        # --- texto seguro ---
        if isinstance(text, (list, tuple)):
            text = text[0]

        x1, y1, x2, y2 = bbox

        # --- limpiar zona con margen ---
        clear_pad = 12
        self.clear_canvas_area(
            max(0, x1 - clear_pad),
            max(0, y1 - clear_pad),
            x2 + clear_pad,
            y2 + clear_pad
        )

        # --- padding interno de la bbox ---
        inner_pad = 8
        x1 += inner_pad
        y1 += inner_pad
        x2 -= inner_pad
        y2 -= inner_pad

        box_w = max(1, x2 - x1)
        box_h = max(1, y2 - y1)

        # --- obtener imagen RGBA del canvas ---
        img_bgra = self._canvas.get_image()   # (H,W,4) BGRA
        img_rgba = cv2.cvtColor(img_bgra, cv2.COLOR_BGRA2RGBA)

        pil_img = Image.fromarray(img_rgba)
        draw = ImageDraw.Draw(pil_img)

        # --- fuente CJK (segura en Windows) ---
        font_path = "C:\\Windows\\Fonts\\simsun.ttc"

        # ======================================================
        # 🔥 CLAVE: tamaño inicial desde la bbox, NO fijo
        # ======================================================
        font_size = max(12, int(box_h * 0.75))
        font = ImageFont.truetype(font_path, font_size)

        # --- ajustar SOLO si el ancho se pasa ---
        bbox_text = draw.textbbox((0, 0), text, font=font)
        tw = bbox_text[2] - bbox_text[0]
        th = bbox_text[3] - bbox_text[1]

        if tw > box_w:
            scale = box_w / tw
            font_size = max(12, int(font_size * scale * 0.95))
            font = ImageFont.truetype(font_path, font_size)

            bbox_text = draw.textbbox((0, 0), text, font=font)
            tw = bbox_text[2] - bbox_text[0]
            th = bbox_text[3] - bbox_text[1]

        # --- centrar texto en bbox ---
        text_x = x1 + (box_w - tw) // 2
        text_y = y1 + (box_h - th) // 2

        # --- dibujar texto (NEGRO sólido) ---
        draw.text((text_x, text_y), text, fill=(0, 0, 0), font=font)

        # --- volver a BGRA conservando alpha ---
        out_rgba = np.array(pil_img)
        out_bgra = cv2.cvtColor(out_rgba, cv2.COLOR_RGBA2BGRA)

        img_bgra[:] = out_bgra
