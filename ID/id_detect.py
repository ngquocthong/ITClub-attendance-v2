import cv2
import pytesseract
import re
import numpy as np


def recognize_student_id(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    pattern = r"[A-Z]{3}\d{6}"
    match = re.search(pattern, text)
    if match:
        student_id = match.group(0)
        return student_id
    return None


def rotate_image(image, angle):
    rows, cols = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
    return rotated_image


cap = cv2.VideoCapture(0)

while True:
    # Đọc khung hình từ webcam
    ret, frame = cap.read()

    # Kiểm tra xem việc đọc khung hình có thành công hay không
    if not ret:
        break

    # Xác định góc quay của khung hình
    angles = [-20, -10, 5, 0, 5, 10, 20]  # Các góc quay có thể thay đổi
    rotated_frame = None
    max_student_id = None

    for angle in angles:
        rotated_image = rotate_image(frame, angle)
        student_id = recognize_student_id(rotated_image)
        if student_id:
            max_student_id = student_id
            rotated_frame = rotated_image

    # Hiển thị kết quả lên khung hình
    if max_student_id:
        cv2.putText(
            frame,
            f"Student ID: {max_student_id}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            2,
        )
    else:
        cv2.putText(
            frame,
            "Student ID: Not found",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            2,
        )

    cv2.imshow("Webcam", frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) == ord("q"):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
