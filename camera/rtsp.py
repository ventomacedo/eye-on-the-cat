import os
import threading
import cv2
from dotenv import load_dotenv
import numpy as np

load_dotenv()
SHOW_WINDOW = os.getenv("SHOW_WINDOW") == "True"

kernel_sharpening = np.array([[-1, -1, -1], 
                              [-1,  9, -1], 
                              [-1, -1, -1]])

class RTSPCamera:
    RECONNECT_AFTER_FAILURES = 10

    def __init__(self, url):
        self.url = url
        self.cap = None
        self._fail_count = 0

        self._lock = None
        self._latest_frame = None
        self._frame_ready = None
        self._grab_thread = None
        self._stop_event = None

    def connect(self):
        original_option = os.environ.get("OPENCV_FFMPEG_CAPTURE_OPTIONS")
        transport = 'udp'
        os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = (
            f"rtsp_transport;{transport}|allowed_media_types;video|max_delay;500000|reorder_queue_size;100|fifo_size;5000000|buffer_size;5000000"
        )

        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)

        if self.cap.isOpened():
            try:
                self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass

            print(f"Conectado ao stream ({transport}): {self.url}")
            if original_option is not None:
                os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = original_option
            else:
                os.environ.pop("OPENCV_FFMPEG_CAPTURE_OPTIONS", None)

            self._start_grabber()
            return True

        print(f"Falha ao conectar ao stream ({transport}): {self.url}")
        if self.cap is not None:
            self.cap.release()
        self.cap = None

        if original_option is not None:
            os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = original_option
        else:
            os.environ.pop("OPENCV_FFMPEG_CAPTURE_OPTIONS", None)

        print(f"Falha ao conectar ao stream: {self.url}")
        return False

    def _start_grabber(self):
        if self._lock is None:
            self._lock = threading.Lock()
            self._frame_ready = threading.Event()
            self._stop_event = threading.Event()

        self._stop_event.clear()
        self._grab_thread = threading.Thread(target=self._grab_loop, daemon=True)
        self._grab_thread.start()

    def _stop_grabber(self):
        if self._stop_event is not None:
            self._stop_event.set()
        if self._grab_thread is not None:
            self._grab_thread.join(timeout=2)
        self._grab_thread = None

    def _grab_loop(self):
        while not self._stop_event.is_set():
            if self.cap is None:
                break

            ret, frame = self.cap.read()
            if not ret or frame is None:
                self._fail_count += 1
                if self._fail_count >= self.RECONNECT_AFTER_FAILURES:
                    print(f"Muitas falhas de leitura, reconectando: {self.url}")
                    self._stop_event.set()
                    self._reconnect()
                    return
                continue

            self._fail_count = 0
            # frame = cv2.filter2D(frame, -1, kernel_sharpening)

            with self._lock:
                self._latest_frame = frame
            self._frame_ready.set()

    def _reconnect(self):
        cap = self.cap
        self.cap = None
        if cap is not None:
            cap.release()
        self.connect()

    def read(self, timeout=5):
        if self.cap is None:
            return False, None

        if not self._frame_ready.wait(timeout=timeout):
            return False, None

        with self._lock:
            frame = self._latest_frame
            self._frame_ready.clear()

        if frame is None:
            return False, None

        return True, frame

    def resize(self, frame, size):
        return cv2.resize(frame, size)

    def release(self):
        self._stop_grabber()
        if self.cap is not None:
            cap = self.cap
            self.cap = None
            return cap.release()
        return None

    def show(self, frame, id):
        return cv2.imshow(f"{id}", frame)

    def closeWindow(self):
        return cv2.destroyAllWindows();

    def isOpened(self):
        if self.cap is not None:
            return self.cap.isOpened()
        return False