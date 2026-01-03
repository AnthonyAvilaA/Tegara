import cv2
class SketchTool():
    def __init__(self, sketch):
        self.sketch = sketch
    
    def sketch_bbox(self):
        xs = [x for stroke in self.sketch for (x, _) in stroke]
        ys = [y for stroke in self.sketch for (_, y) in stroke]
        return min(xs), min(ys), max(xs), max(ys)

    def normalize_sketch(self):
        x0, y0, x1, y1 = self.sketch_bbox()
        w = x1 - x0
        h = y1 - y0

        normalized = []
        for stroke in self.sketch:
            norm_stroke = []
            for x, y in stroke:
                nx = (x - x0) / w
                ny = (y - y0) / h
                norm_stroke.append((nx, ny))
            normalized.append(norm_stroke)

        return normalized

    def fit_sketch_to_box(self, normalized_sketch, box, keep_aspect=True):
        bx0, by0, bx1, by1 = box
        bw = bx1 - bx0
        bh = by1 - by0

        if keep_aspect:
            scale = min(bw, bh)
            ox = bx0 + (bw - scale) / 2
            oy = by0 + (bh - scale) / 2
            sx, sy = scale, scale
        else:
            ox, oy = bx0, by0
            sx, sy = bw, bh

        fitted = []
        for stroke in normalized_sketch:
            fitted_stroke = []
            for nx, ny in stroke:
                x = int(nx * sx + ox)
                y = int(ny * sy + oy)
                fitted_stroke.append((x, y))
            fitted.append(fitted_stroke)

        return fitted

    def draw_sketch(self, sketch, canvas, color, thickness):
        for stroke in sketch:
            for (x1, y1), (x2, y2) in zip(stroke, stroke[1:]):
                cv2.line(
                    canvas,
                    (x1, y1),
                    (x2, y2),
                    color.get_tuple(),
                    thickness
                )
                
    def draw_on_canvas(self, canvas, box, color, thickness):
        normalized = self.normalize_sketch()
        adapted = self.fit_sketch_to_box(
            normalized,
            box=box,
            keep_aspect=True
        )
        self.draw_sketch(adapted, canvas, color, thickness)