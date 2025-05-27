# face/face_save.py
import os
import sqlite3
import json
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import transforms
import cv2
import numpy as np

class FaceSaver:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DB", "users.db")

    def __init__(self):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print("Using:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

        self.mtcnn = MTCNN(keep_all=False, device=self.device)
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    def extract_embedding(self, image_bgr):
        image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
        boxes, _ = self.mtcnn.detect(image_rgb)
        if boxes is not None and len(boxes) > 0:
            x1, y1, x2, y2 = [int(b) for b in boxes[0]]
            face = image_rgb[max(y1, 0):min(y2, image_rgb.shape[0]), max(x1, 0):min(x2, image_rgb.shape[1])]
            if face.size == 0:
                return None

            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((160, 160)),
                transforms.ToTensor(),
                transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
            ])
            face_tensor = transform(face).unsqueeze(0).to(self.device)
            embedding = self.facenet(face_tensor).detach().cpu().numpy().flatten()
            return embedding
        return None

    def save_embedding_to_db(self, student_id, embedding):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE users SET face_embedding = ? WHERE student_id = ?
            """, (json.dumps(embedding.tolist()), student_id))
            conn.commit()
            print(f"✅ {student_id}의 얼굴 임베딩이 DB에 저장되었습니다.")
        except sqlite3.Error as e:
            print("❌ DB 업데이트 오류:", e)
        finally:
            conn.close()
