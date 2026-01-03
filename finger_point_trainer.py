from cvzone.HandTrackingModule import HandDetector
import cv2
from definitions.Key import Key
import numpy as np
import torch
from model.SmallClassifier import SmallClassifier

# Cámara
vid = cv2.VideoCapture(0)

# Initializa detector
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.2, minTrackCon=0.1)
startRecording = False

pointingRecord = list() # dedo índice apuntando
eraseRecord = list() # palma abierta hacia la camara
zoomRecord = list()  # "haciendo una boca con la mano hacia la camara"
fillRecord = list()  # dos dedos juntos (indice y medio) extendidos
rotateRecord = list()  # dos dedos separados (indice y medio) extendidos
scrollRecord = list() # palma abierta hacia arriba o abajo
idleRecord = list() # puño cerrado


modelTrained = False

model = SmallClassifier()


# Intentar cargar modelo previo para continuar entrenamiento
try:
    model.load_state_dict(torch.load("modelo_pointing_v2.pth", map_location="cpu"))
    modelTrained = True
    print("Modelo cargado. Continuando entrenamiento...")
except FileNotFoundError:
    print("No existe modelo anterior. Se entrenará desde cero.")


while(True):      
    # Fotograma a fotograma
    ret, frame = vid.read()
    frame = cv2.flip(frame, 1)  # Espejo para selfie view

    # Búsqueda de manos
    # 'draw' a True indica si se dibujan sobre la imagen 
    # 'flipType' a True para tratar la imagen reflejada
    hands, frame = detector.findHands(frame, draw=True, flipType=True)
    
    # Si hay manos detectadas
    if hands:
        # datos primera mano
        hand1 = hands[0]
        # dibujar la profundidad de cada punto
        for lm in hand1["lmList"]:
            cv2.putText(frame, f'{lm[2]}', (lm[0], lm[1]), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
        lmList1 = hand1["lmList"]  # 21 landmarks
        bbox1 = hand1["bbox"]  # Contenedor (x,y,w,h)
        center1 = hand1['center']  # Centro
        handType1 = hand1["type"]  # identifica si es la mano derecha o izquierda

        # Contabiliza dedos extendidos de la mano
        # fingers1 = detector.fingersUp(hand1)
        # print(f'H1 = {fingers1.count(1)}', end=" ")  

        # Calcula distancia entre dos elementos concretos de la mano, dibujando segmento entre ellos
        length, info, frame = detector.findDistance(lmList1[8][0:2], lmList1[12][0:2], frame, color=(255, 0, 0),
                                                  scale=10)

        # mostrar si se está grabando
        if startRecording:
            cv2.putText(frame, 'Recording', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3, (0, 0, 255), 3)

    if modelTrained and hands:
        sample = np.array(lmList1)
        sample = model.normalize_sample(sample).flatten().astype(np.float32)
        prob, prediction = model.predict(sample)
        if prediction == 1:
            cv2.putText(frame, 'Pointing', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        elif prediction == 2:
            cv2.putText(frame, 'Erase', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        elif prediction == 3:
            cv2.putText(frame, 'Zoom', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        elif prediction == 4:
            cv2.putText(frame, 'Fill', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        elif prediction == 5:
            cv2.putText(frame, 'Rotate', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        elif prediction == 6:
            cv2.putText(frame, 'Scroll', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        else:
            cv2.putText(frame, 'Not Pointing', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    # Display the image in a window
    cv2.imshow("Image", frame)

    key = cv2.waitKey(1)
    if hands:
        if key == Key.NUM_1:
            pointingRecord.append(lmList1)
            print(f"Registro de muestra apuntando. Total: {len(pointingRecord)}")
        elif key == Key.NUM_2:
            eraseRecord.append(lmList1)
            print(f"Registro de muestra palma abierta. Total: {len(eraseRecord)}")
        elif key == Key.NUM_3:
            zoomRecord.append(lmList1)
            print(f"Registro de muestra zoom. Total: {len(zoomRecord)}")
        elif key == Key.NUM_4:
            fillRecord.append(lmList1)
            print(f"Registro de muestra fill. Total: {len(fillRecord)}")
        elif key == Key.NUM_5:
            rotateRecord.append(lmList1)
            print(f"Registro de muestra rotate. Total: {len(rotateRecord)}")
        elif key == Key.NUM_6:
            scrollRecord.append(lmList1)
            print(f"Registro de muestra scroll. Total: {len(scrollRecord)}")
        elif key == Key.NUM_7:
            idleRecord.append(lmList1)
            print(f"Registro de muestra no apuntando. Total: {len(idleRecord)}")
    elif key == Key.T:
        newPointingRecord = list()
        newEraseRecord = list()
        newZoomRecord = list()
        newFillRecord = list()
        newRotateRecord = list()
        newScrollRecord = list()
        newIdleRecord = list()
        for i in [model.normalize_sample(s).flatten() for s in pointingRecord]:
            if i is not None:
                newPointingRecord.append(i)
        for i in [model.normalize_sample(s).flatten() for s in eraseRecord]:
            if i is not None:
                newEraseRecord.append(i)
        for i in [model.normalize_sample(s).flatten() for s in zoomRecord]:
            if i is not None:
                newZoomRecord.append(i)
        for i in [model.normalize_sample(s).flatten() for s in fillRecord]:
            if i is not None:
                newFillRecord.append(i)
        for i in [model.normalize_sample(s).flatten() for s in rotateRecord]:
            if i is not None:
                newRotateRecord.append(i)
        for i in [model.normalize_sample(s).flatten() for s in scrollRecord]:
            if i is not None:
                newScrollRecord.append(i)
        for i in [model.normalize_sample(s).flatten() for s in idleRecord]:
            if i is not None:
                newIdleRecord.append(i)

        X = np.array(
            newPointingRecord +
            newEraseRecord +
            newZoomRecord +
            newFillRecord +
            newRotateRecord +
            newScrollRecord +
            newIdleRecord, dtype=np.float32)

        y = np.array([1]*len(newPointingRecord) +
                     [2]*len(newEraseRecord) +
                     [3]*len(newZoomRecord) +
                     [4]*len(newFillRecord) +
                     [5]*len(newRotateRecord) +
                     [6]*len(newScrollRecord) +
                     [0]*len(newIdleRecord), dtype=np.float32)
        
        X = torch.tensor(X, dtype=torch.float32)
        # y = torch.tensor(y).unsqueeze(1)
        y = torch.tensor(y, dtype=torch.long)

        model.fit(X, y, epochs=200)
        
        modelTrained = True
        print("Entrenamiento terminado")
        
    elif key == 27:  # ESC para salir
        break

# Libera el objeto de captura
vid.release()
# Destruye ventanas
cv2.destroyAllWindows()

torch.save(model.state_dict(), "modelo_pointing_v2_new.pth")

