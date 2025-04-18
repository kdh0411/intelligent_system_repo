import cv2
from ultralytics import YOLO
import os

class BookDetector:
    def __init__(self, model_path='yolov8m.pt', save_path='book_detect/book_crop.jpg'):
        self.model = YOLO(model_path)
        self.class_id = 73  # COCO에서 책의 클래스 ID
        self.save_path = save_path
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

    def detect_books(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("❌ 웹캠을 열 수 없습니다.")
            return

        print("📷 책 검출 시작. 's'를 누르면 캡처, 'q'를 누르면 종료됩니다.")

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            results = self.model(frame, verbose=False)[0]
            book_box = None

            for box in results.boxes:
                class_id = int(box.cls[0])
                if class_id == self.class_id:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    book_box = (x1, y1, x2, y2)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, "Book", (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            cv2.imshow("Book Detection", frame)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('s') and book_box:
                x1, y1, x2, y2 = book_box
                cropped = frame[y1:y2, x1:x2]
                cv2.imwrite(self.save_path, cropped)
                print(f"✅ 캡처 저장 완료: {self.save_path}")

            elif key == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

# 책 검출 및 수동 캡처 테스트
if __name__ == "__main__":
    detector = BookDetector()
    detector.detect_books()
