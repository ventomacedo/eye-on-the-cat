import os
from datetime import datetime
from collections import deque
import time

import cv2

class Capture:
    def __init__(self):
        self.CAPTURES_FOLDER = "captures"
        os.makedirs(self.CAPTURES_FOLDER, exist_ok=True)
        self.fps = 24
        self.total_frames = 10 * self.fps
        self.cooldown_seconds = 15
        self.recordings = {}

    def is_recording(self, id):
        return self.recordings.get(id, {}).get("active", False)

    def printCapture(self, frame, id):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        today = datetime.now().strftime("%Y%m%d")
        filename = os.path.join(self.CAPTURES_FOLDER, id, f"{today}", "images", f"{timestamp}.jpg")
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        cv2.imwrite(filename, frame)
        print(f"Movimento detectado, salvando...")

    def recorder(self, frame, id, annotated_frame=None, detected=False):
        if id not in self.recordings:
            self.recordings[id] = {
                "active": False,
                "writer": None,
                "frames_left": 0,
                "cooldown_until": 0,
                "path": None,
            }

        record = self.recordings[id]
        now = time.time()

        if detected and not record["active"] and now >= record["cooldown_until"]:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            today = datetime.now().strftime("%Y%m%d")
            filename = os.path.join(self.CAPTURES_FOLDER, id, f"{today}", "videos", f"{timestamp}.mp4")
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            height, width = frame.shape[:2]
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(filename, fourcc, self.fps, (width, height))

            if writer.isOpened():
                record.update({
                    "active": True,
                    "writer": writer,
                    "frames_left": self.total_frames - 1,
                    "path": filename,
                })

                output_frame = annotated_frame if annotated_frame is not None else frame
                writer.write(output_frame)
                print(f"🐱 Gato detectado! Gravando 10 segundos em: {filename}")
            else:
                print(f"Erro ao iniciar gravação de vídeo: {filename}")
                writer.release()

        if record["active"] and record["writer"] is not None:
            output_frame = annotated_frame if annotated_frame is not None else frame
            record["writer"].write(output_frame)
            record["frames_left"] -= 1

            if record["frames_left"] <= 0:
                record["writer"].release()
                record["active"] = False
                record["writer"] = None
                record["cooldown_until"] = now + self.cooldown_seconds
                print(f"✅ Vídeo salvo em: {record['path']}. Próxima gravação disponível em {self.cooldown_seconds}s.")