# face/face_save_db.py

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
        # GPU 사용 여부 설정
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print("Using:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

        # 얼굴 감지 모델과 임베딩 모델 초기화
        self.mtcnn = MTCNN(keep_all=False, device=self.device)
        self.facenet = InceptionResnetV1(pretrained='vggface2').eval().to(self.device)

    # 얼굴 임베딩 추출
    def extract_embedding(self, image):
        boxes, _ = self.mtcnn.detect(image)
        if boxes is not None and len(boxes) > 0:
            x1, y1, x2, y2 = [int(b) for b in boxes[0]]
            face = image[max(y1, 0):min(y2, image.shape[0]), max(x1, 0):min(x2, image.shape[1])]
            if face.size == 0:
                return None, None

            transform = transforms.Compose([
                transforms.ToPILImage(),
                transforms.Resize((160, 160)),
                transforms.ToTensor(),
                transforms.Normalize([0.5, 0.5, 0.5], [0.5, 0.5, 0.5])
            ])
            face_tensor = transform(face).unsqueeze(0).to(self.device)
            embedding = self.facenet(face_tensor).detach().cpu().numpy().flatten()
            return embedding, boxes[0]
        return None, None

    # 얼굴 임베딩을 DB에 저장
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

    # 캠 실행 -> 's' 입력 시 저장
    # 반환만 하도록 수정
    def register_face(self):
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            print("Failed to open webcam.")
            return None

        print("Press 's' to save new face, 'q' to quit.")

        embedding_to_return = None

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            embedding, box = self.extract_embedding(frame_rgb)

            if embedding is not None and box is not None:
                x1, y1, x2, y2 = [int(b) for b in box]
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.imshow("Face Registration", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s') and embedding is not None:
                embedding_to_return = embedding
                break
            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        return embedding_to_return
# ❌ CLI용 입력 제거: Flask에서 student_id를 넘겨주는 구조로 통일
