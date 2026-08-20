import os
import cv2
import json
import subprocess
import platform

from multiprocessing import Process

from dotenv import load_dotenv
from camera import CameraWorker
from camera.worker import SHOW_WINDOW

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
PORT = os.getenv("PORT") or "554"
CAMERAS = json.loads(os.getenv("CAMERAS") or "[]")

if not USERNAME or not PASSWORD:
    raise ValueError("USERNAME, PASSWORD devem estar definidos em .env")

def avoidSleep():
    """Garante que o macOS não entre em repouso enquanto o script estiver rodando."""
    if platform.system() == "Darwin":
        # -d: impede repouso da tela
        # -i: impede repouso do sistema/CPU
        # -m: impede repouso dos discos
        # -s: impede repouso quando conectado à tomada
        # -w: atrela o caffeinate ao PID do processo Python atual
        pid = os.getpid()
        subprocess.Popen(["caffeinate", "-dims", "-w", str(pid)])
        print("🔒 Prevenção de repouso do macOS ativa (caffeinate).")

def build_rtsp_url(ip: str) -> str:
    return f"rtsp://{USERNAME}:{PASSWORD}@{ip}:{PORT}/onvif1"


def main():
    processesList = []

    #Cameras
    if len(CAMERAS) > 0:
        for cam in CAMERAS:
            url = build_rtsp_url(cam["ip"])
            worker = CameraWorker(cam["name"], url)

            process = Process(
                target=worker.start,
                args=(),
                name=f"CameraWorker-{cam['name']}"
            )
            process.daemon = True
            process.start()
            processesList.append(process)

    try:
        while True:
            if cv2.waitKey(1) & 0xFF == ord("q"):
                if SHOW_WINDOW:
                    cv2.destroyAllWindows()
                break
    finally:
        for process in processesList:
            process.terminate()
            process.join()
        

if __name__ == "__main__":
    avoidSleep()
    main()