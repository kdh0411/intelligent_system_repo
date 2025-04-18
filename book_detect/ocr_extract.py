from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='korean')  # 한글 포함
result = ocr.ocr('book_detect/book_crop.jpg', cls=True)

# 결과 출력
for line in result[0]:
    print(line[1][0])  # 인식된 텍스트
