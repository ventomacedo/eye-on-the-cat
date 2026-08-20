import os
import cv2
from dotenv import load_dotenv
import numpy as np

load_dotenv()
SHOW_WINDOW = os.getenv("SHOW_WINDOW") == "True"

kernel_sharpening = np.array([[-1, -1, -1], 
                              [-1,  9, -1], 
                              [-1, -1, -1]])

class RTSPCamera:
    def __init__(self, url):
        self.url = url
        self.cap = None

    def connect(self):
        original_option = os.environ.get("OPENCV_FFMPEG_CAPTURE_OPTIONS")
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
            "rtsp_transport;udp|fflags;nobuffer|flags;low_delay|max_delay;2000000|fifo_size;500000"
        )

        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)
        
        if self.cap.isOpened():
            try:
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass
            
            print(f"Conectado ao stream (udp): {self.url}")
            if original_option is not None:
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = original_option
            else:
                os.environ.pop("OPENCV_FFMPEG_CAPTURE_OPTIONS", None)
            return True

        print(f"Falha ao conectar ao stream (udp): {self.url}")
        if self.cap is not None:
            self.cap.release()

        self.cap = None
        if original_option is not None:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = original_option
        else:
            os.environ.pop("OPENCV_FFMPEG_CAPTURE_OPTIONS", None)

        print(f"Falha ao conectar ao stream: {self.url}")
        return False

    def read(self):
        if self.cap is None:
            return False, None

        ret, frame = self.cap.read()
        if not ret or frame is None:
            return False, None

        frame = cv2.filter2D(frame, -1, kernel_sharpening)

        # Limpa o buffer interno e retorna o último frame disponível
        # if not SHOW_WINDOW:
        #     while True:
        #         has_more = self.cap.grab()
        #         if not has_more:
        #             break
        #         ret2, frame2 = self.cap.retrieve()
        #         if not ret2 or frame2 is None:
        #             break
        #         frame = frame2

        return True, frame

    def resize(self, frame, size):
        return cv2.resize(frame, size)

    def release(self):
        if self.cap is not None:
            return self.cap.release()
        return None

    def show(self, frame, id):
        return cv2.imshow(f"{id}", frame)

    def closeWindow(self):
        return cv2.destroyAllWindows();

    def isOpened(self):
        if self.cap is not None:
            return self.cap.isOpened()
        return False