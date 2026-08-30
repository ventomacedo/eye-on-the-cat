import os
import cv2
from .rtsp import RTSPCamera
from dotenv import load_dotenv

load_dotenv()
# Não forçamos UDP globalmente aqui. O RTSPCamera fará fallback para UDP somente se a conexão normal falhar.
SHOW_WINDOW = os.getenv("SHOW_WINDOW") == "True"

class CameraWorker:
    
    def __init__(self, id, url, detector=None):
        self.id = id
        self.detector = detector
        self.camera = RTSPCamera(url=url)
        self.running = False

    def start(self):
        try:
            if self.detector is None:
                from detection import Detector
                from integrations.tuya import TuyaController

                tuya = TuyaController()
                self.detector = Detector(tuya)

            if not self.camera.connect():
                return

            self.running = True

            while self.running:
                ret, frame = self.camera.read()

                if not ret or frame is None:
                    print("Falha ao receber frame. Tentando reconectar...")
                    self.running = False
                    break

                self.resized = self.camera.resize(frame, size=(740, 416))
                self.blured = self.resized #self.detector.detectPlates(self.resized)
                self.video = self.detector.detectCat(self.blured, self.id)

                if SHOW_WINDOW is True:
                    self.camera.show(self.video, self.id)
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
        except Exception as e:
            print(f"Erro na câmera {self.id}: {e}")
        finally:
            self.release()

    def release(self):
        self.camera.release()

    def stop(self):
        self.running = False