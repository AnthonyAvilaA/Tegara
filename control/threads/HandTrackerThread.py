import threading
import queue
import time
import cv2
from model.Point import Point
from model.HandDetectorWrapper import HandDetectorWrapper
from view.MainFrame import MainFrame
from model.SmallClassifier import SmallClassifier
from definitions.HandsGestures import HandsGestures
import torch
import numpy as np

class HandTrackerThread(threading.Thread):
    def __init__(self, event_queue: queue.Queue, vid: cv2.VideoCapture, hand_detector: HandDetectorWrapper, model: SmallClassifier, mainFrame: MainFrame):
        super().__init__(daemon=True)
        self.event_queue = event_queue
        self.vid = vid
        self.hand_detector = hand_detector
        self.model = model
        self.mainFrame = mainFrame

        self.prev_index_finger_point = {i: Point(400, 300) for i in range(21)}
        self.running = True
        self.start_timer = True
        self.first_click = True

    def normalize_finger_position(self, point: Point, prev_point: Point, img_w: int, img_h: int, cw: int, ch: int) -> Point:
        if point is None:
            return prev_point

        point = point.scale_axes(1/img_w, 1/img_h)
        point = point.scale_axes(cw, ch)
        point = point.lerp(prev_point, 0.3)
        point = point.scale(1.1)
        return point.to_int()

    def run(self):
        while self.running:
            ret, frame = self.vid.read()
            if not ret:
                continue

            frame = cv2.flip(frame, 1)
            self.hand_detector.setImage(frame)
            hands = self.hand_detector.findHands(draw=False)

            if not hands:
                time.sleep(0.005)
                continue

            # ======== Clasificación Multiclases ========
            hand = hands[0]
            lmList = hand["lmList"]

            x_norm = self.model.normalize_sample(lmList)
            
            if x_norm is None:
                continue

            x_tensor = torch.tensor(np.array(x_norm), dtype=torch.float32).flatten().unsqueeze(0)
            with torch.no_grad():
                outputs = self.model(x_tensor)
                prob, pred = torch.max(outputs, 1)
                gesture_id = pred.item()

            # ======== Normalización ========
            hand_points = self.hand_detector.get_hand_points(hands, 0)
            img_h, img_w = frame.shape[:2]
            cw, ch = self.mainFrame.get_window_size()

            for i in range(len(hand_points)):
                hand_points[i] = self.normalize_finger_position(
                    hand_points[i],
                    self.prev_index_finger_point[i],
                    img_w, img_h,
                    cw, ch
                )
                self.prev_index_finger_point[i] = hand_points[i]

            index_finger = hand_points[8]

            # Enviamos datos crudos al hilo principal
            self.event_queue.put({
                "type": "cursor_update",
                "points": hand_points
            })
            

            # ======== Lógica de clic y drag ========
            if index_finger is None:
                time.sleep(0.005)
                continue

            if gesture_id == 0:
                gesture_id = 7
            gesture = HandsGestures(gesture_id)

            if gesture != HandsGestures.IDLE and prob.item() > 0.8:
                if self.start_timer:
                    self.pointing_timer = cv2.getTickCount() + 0.3 * cv2.getTickFrequency()
                    self.start_timer = False
                elif cv2.getTickCount() > self.pointing_timer:
                    self.event_queue.put({
                            "type": "hand_gesture",
                            "gesture": gesture
                        })
                    if gesture == HandsGestures.POINTING or gesture == HandsGestures.ERASE or gesture == HandsGestures.FILL:                        
                        if self.first_click:
                            self.event_queue.put({
                                "type": "left_down",
                                "point": index_finger
                            })
                            self.event_queue.put({
                                "type": "cursor_type",
                                "cursor": 0
                            })
                            self.first_click = False

                        self.event_queue.put({
                            "type": "left_drag",
                            "point": index_finger
                        })
                    else:
                        self.event_queue.put({"type": "reset_drag"})
                        self.first_click = True
                        self.start_timer = True
            else:
                self.start_timer = True
                self.first_click = True
                self.event_queue.put({"type": "reset_drag"})
                
                self.event_queue.put({
                    "type": "cursor_type",
                    "cursor": 1
                })

            # Cursor
            self.event_queue.put({
                "type": "cursor_position",
                "point": index_finger
            })

            time.sleep(0.05)  # Desaturar CPU
