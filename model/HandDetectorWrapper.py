from cvzone.HandTrackingModule import HandDetector
from model.Point import Point

class HandDetectorWrapper:
    def __init__(self, staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5):
        self.detector = HandDetector(staticMode=staticMode, maxHands=maxHands, modelComplexity=modelComplexity,
                                     detectionCon=detectionCon, minTrackCon=minTrackCon)
        self.img = None

    def setImage(self, img) -> None:
        self.img = img

    def findHands(self, draw=True) -> list[dict]:
        hands, _ = self.detector.findHands(self.img, draw=draw)
        return hands

    def get_index_finger(self, hands: list[dict], handNo=0) -> Point:
        if hands and len(hands) > handNo:
            lmList = hands[handNo]['lmList']
            return Point(lmList[8][0], lmList[8][1])  # Índice del dedo índice
        return None

    def get_hand_points(self, hands: list[dict], handNo=0) -> dict[int, Point]:
        points = dict()
        if hands and len(hands) > handNo:
            lmList = hands[handNo]['lmList']
            for i, lm in enumerate(lmList):
                points[i] = Point(lm[0], lm[1])
        return points
