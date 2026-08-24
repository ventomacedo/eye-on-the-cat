import os

from ultralytics import YOLO
from detection.processor import FileProcessor
from integrations.audio import CatRepellentAudio
from storage.capture import Capture

DEVICE_TYPE = os.getenv("DEVICE_TYPE") or "cpu"
TAKE_PICTURE = os.getenv("TAKE_PICTURE") == "True"
TAKE_RECORD = os.getenv("TAKE_RECORD") == "True"

class Detector:
    def __init__(self, tuyaController=None):
        self.storage = Capture()
        self.frame_count = 0
        self.model = YOLO("yolo11n.pt")
        self.plateModel = YOLO("license_plates.pt")
        self.tuyaController = tuyaController
        self.repellentAudio = CatRepellentAudio()
        self.resetMessage = False
        self.processor = FileProcessor(self)

    def detectPlates(self, frame):
        try:
            self.platesResult = self.plateModel.predict(
                source=frame,
                conf=0.02,
            )
            for box in self.platesResult[0].boxes:
                cls_id = int(box.cls[0])
                label = self.plateModel.names[cls_id]
                print(f"Placa detectada! label={label} conf={float(box.conf):.2f}")

            # Blur das placas sem desenhar boxes
            _annotated_frame = self.processor.blurPlateRegions(frame, self.platesResult[0].boxes)
            return _annotated_frame
        except Exception as e:
                print(f"Erro na detecção: {e}")
                return frame

    def detectCat(self, frame, id):
        try:
            self.catResults = self.model.predict(
                source=frame,
                imgsz=640,
                device=DEVICE_TYPE,
                verbose=False,
                classes=[15], # Classes do YOLO https://gist.github.com/rcland12/dc48e1963268ff98c8b2c4543e7a9be8,
                conf=0.20
            )
            _annotated_frame = self.catResults[0].plot()

            detected = False
            for box in self.catResults[0].boxes:
                if float(box.conf) < 0.50:
                    continue

                print(float(box.conf))
                cls_id = int(box.cls[0])
                label = self.model.names[cls_id]

                detected = True
                print(f"🐱 detectado! id={id} label={label} conf={float(box.conf):.2f}")

                if self.tuyaController is not None:
                    try:
                        self.tuyaController.turnOnAllLights()
                        print("💡 Luzes acionadas via Tuya.")
                    except Exception as tuya_error:
                        print(f"⚠️ Falha ao acender luzes via Tuya: {tuya_error}")

                    self.repellentAudio.play()

                if TAKE_PICTURE:
                    self.storage.printCapture(frame, id)
                break

            if TAKE_RECORD:self.storage.recorder(frame, id, annotated_frame=_annotated_frame, detected=detected)
            return _annotated_frame
        except Exception as e:
            print(f"Erro na detecção: {e}")
            return frame