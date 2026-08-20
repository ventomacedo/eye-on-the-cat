import os
import sys
import cv2
import numpy as np

kernel_sharpening = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])

class FileProcessor:
    
    def __init__(self, detector):
        self.detector = detector

    def blurPlateRegions(self, frame, boxes):
        result = frame.copy()
        for box in boxes:
            xyxy = box.xyxy[0]
            if hasattr(xyxy, "cpu"):
                xyxy = xyxy.cpu().numpy()
            if hasattr(xyxy, "tolist"):
                xyxy = xyxy.tolist()

            x1, y1, x2, y2 = map(int, xyxy)
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(result.shape[1], x2), min(result.shape[0], y2)
            roi = result[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            blur = cv2.GaussianBlur(roi, (51, 51), 0)
            result[y1:y2, x1:x2] = blur

        return result

    def processImage(self, image_path, save_path=None, id="local"):
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Não foi possível abrir a imagem: {image_path}")

        # Detectar gato
        annotated = self.detector.detectCat(image, id)
        # Detectar e borrar placa
        processed = self.detector.detectPlates(annotated)

        if save_path:
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            cv2.imwrite(save_path, processed)
            print(f"✅ Imagem processada salva em: {save_path}")

        return processed

    def processVideo(self, video_path, output_path=None, id=None):
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Não foi possível abrir o vídeo: {video_path}")

        id = id or os.path.splitext(os.path.basename(video_path))[0]
        fps = cap.get(cv2.CAP_PROP_FPS) or 24.0
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

        writer = None
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            if not writer.isOpened():
                cap.release()
                raise RuntimeError(f"Não foi possível criar o arquivo de saída: {output_path}")

        frame_count = 0
        print(f"🎬 Processando vídeo: {video_path}")
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            # frame = cv2.filter2D(frame, -1, kernel_sharpening)
            # Detectar gato
            plateProcessed = self.detector.detectPlates(frame)
            catProcessed = self.detector.detectCat(plateProcessed, id)
            frame_count += 1

            if frame_count % 30 == 0:
                print(f"Processados {frame_count} frames...")

            if writer is not None:
                writer.write(catProcessed)

        cap.release()
        if writer is not None:
            writer.release()
            print(f"✅ Vídeo processado salvo em: {output_path}")

        print(f"📊 Total de frames processados: {frame_count}")
        print("✅ Processamento de vídeo concluído. Encerrando aplicação...")

        cv2.destroyAllWindows()
        sys.exit(0)
