from cvzone.HandTrackingModule import HandDetector
import cv2
from definitions.key import Key
import numpy as np
import torch
from model.SmallClassifier import SmallClassifier

# Cámara
vid = cv2.VideoCapture(0)

# Initializa detector
detector = HandDetector(staticMode=False, maxHands=2, modelComplexity=1, detectionCon=0.5, minTrackCon=0.5)
startRecording = False

pointingRecord = list() # Distancia desde el centro de la palma a los
notPointingRecord = list() 

modelTrained = False

model = SmallClassifier()

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
        prediction = model.predict(sample)
        if prediction == 1:
            cv2.putText(frame, 'Pointing', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)
        else:
            cv2.putText(frame, 'Not Pointing', (10, 110), cv2.FONT_HERSHEY_PLAIN, 3, (0, 255, 0), 3)

    # Display the image in a window
    cv2.imshow("Image", frame)

    key = cv2.waitKey(1)
    if key == Key.R:  # ESC para salir
        pointingRecord.append(lmList1)
        print(f"Registro de muestra apuntando. Total: {len(pointingRecord)}")
    elif key == Key.N:  # ESC para salir
        notPointingRecord.append(lmList1)
        print(f"Registro de muestra no apuntando. Total: {len(notPointingRecord)}")
    elif key == Key.T:
        newPointingRecord = list()
        newNotPointingRecord = list()
        for i in [model.normalize_sample(s).flatten() for s in pointingRecord]:
            if i is not None:
                newPointingRecord.append(i)
        for i in [model.normalize_sample(s).flatten() for s in notPointingRecord]:
            if i is not None:
                newNotPointingRecord.append(i)
        if len(newPointingRecord) == 0 or len(newNotPointingRecord) == 0:
            print("No hay suficientes datos para entrenar")
            continue
        X = np.array(newPointingRecord + newNotPointingRecord, dtype=np.float32)
        y = np.array([1]*len(newPointingRecord) + [0]*len(newNotPointingRecord), dtype=np.float32)
        
        X = torch.tensor(X)
        y = torch.tensor(y).unsqueeze(1)

        model.fit(X, y, epochs=200)
        
        modelTrained = True
        print("Entrenamiento terminado")
        
    elif key == 27:  # ESC para salir
        break

# Libera el objeto de captura
vid.release()
# Destruye ventanas
cv2.destroyAllWindows()

torch.save(model.state_dict(), "modelo_pointing.pth")

