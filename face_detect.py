import os
import json
import sqlite3
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1
from torchvision import transforms
import cv2

class FaceDetect:
    DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "DB", "users.db")

    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print("Using:", torch.cuda.get_device_name(0) if torch.cuda.is_available() else "CPU")

        self.mtcnn = MTCNN(keep_all=False, device=self.device)
        self.facenet = InceptionResnetV1(pretrained="vggface2").eval().to(self.device)

        self.embeddings = self.load_embeddings_from_db()
        self.stable_user = None
        self.stable_count = 0
        self.required_count = 20  # ✅ 연속 인식 기준 프레임 수

    def load_embeddings_from_db(self):
        conn = sqlite3.connect(self.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT student_id, face_embedding FROM users WHERE face_embedding IS NOT NULL")
        rows = cursor.fetchall()
        conn.close()

        result = {}
        for student_id, embedding_json in rows:
            embedding = np.array(json.loads(embedding_json))
            result[student_id] = embedding
        return result

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

    def calculate_distance(self, emb1, emb2):
        return np.linalg.norm(emb1 - emb2)

    def feed_frame(self, frame):
        """한 프레임 입력 → 내부 상태 업데이트 → 매칭 결과 리턴"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        embedding, box = self.extract_embedding(frame_rgb)

        if embedding is None:
            self.stable_user = None
            self.stable_count = 0
            return {"match": False}

        match_id = "No Match"
        for student_id, ref_emb in self.embeddings.items():
            if self.calculate_distance(embedding, ref_emb) < 0.8:
                match_id = student_id
                break

        if match_id == self.stable_user:
            self.stable_count += 1
        else:
            self.stable_user = match_id
            self.stable_count = 1 if match_id != "No Match" else 0

        if self.stable_user != "No Match" and self.stable_count >= self.required_count:
            result = self.stable_user
            self.stable_user = None
            self.stable_count = 0
            return {"match": True, "student_id": result}
        else:
            return {
                "match": False,
                "progress": self.stable_count if self.stable_user != "No Match" else 0,
                "match_id": match_id,
                "box": box
            }

    def recognize_face(self):
        """OpenCV 창 띄우고 실시간 인식 테스트"""
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

        if not cap.isOpened():
            print("❌ 캠 열기 실패")
            return "No Match"

        print("📸 얼굴 인식 중입니다. 30프레임 동안 같은 사용자 유지 시 로그인됩니다.")

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            result = self.feed_frame(frame)
            box = result.get("box")
            match_id = result.get("match_id", "No Match")

            if box is not None:
                x1, y1, x2, y2 = [int(b) for b in box]
                color = (0, 255, 0) if match_id != "No Match" else (0, 0, 255)
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                cv2.putText(frame, match_id, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

            cv2.imshow("Face Login", frame)

            if result.get("match"):
                print(f"✅ 로그인 성공: {result['student_id']}")
                cap.release()
                cv2.destroyAllWindows()
                return result["student_id"]

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()
        return "No Match"

    def recognize_face_from_frame(self, frame):
        """Flask용 AJAX 라우팅에서 한 프레임 처리"""
        return self.feed_frame(frame)

#테스트
if __name__ == "__main__":
    detector = FaceDetect()
    student_id = detector.recognize_face()

    if student_id == "No Match":
        print("❌ 얼굴 인식 실패")
    else:
        print(f"✅ 로그인 성공: {student_id}")