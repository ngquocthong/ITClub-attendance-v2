import cv2
import pytesseract
import re
import requests
from numba import jit 

def recognize_student_id(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    pattern = r"(.+)\s+Student ID:\s+([A-Z]{3}\d{5,6,7})"
    match = re.search(pattern, text)
    if match:
        name = match.group(1)
        student_id = match.group(2)
        return name, student_id
    return None

def rotate_image(image, angle):
    rows, cols = image.shape[:2]
    rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
    rotated_image = cv2.warpAffine(image, rotation_matrix, (cols, rows))
    return rotated_image


# Preload Tesseract OCR model
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
tessdata_dir_config = r"--tessdata-dir C:\Program Files\Tesseract-OCR\tessdata"

cap = cv2.VideoCapture(0)

# Set frame resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# Set frame rate and frame skip
frame_delay = 10  # 10ms delay between frames
frame_skip = 5  # Process every 5th frame

# Define ROI coordinates
roi_x = 100
roi_y = 100
roi_width = 400
roi_height = 200

# Determine rotation angles based on expected orientation
rotation_angles = [0]  # Change angles as desired

arr_student_id = []
URL = "https://script.google.com/macros/s/AKfycbxqKrzlIpLs7U9uRMToknoNXoHjzSJ8kfzgjnBsJQnsKqBqRg2OBcEAkne_S5Yci19NsA/exec"  # ?event=*&carid=*&name=*

while True:
    # Read frame from webcam
    ret, frame = cap.read()

    # Check if frame reading was successful
    if not ret:
        break

    # Skip frames
    frame_count = cap.get(cv2.CAP_PROP_POS_FRAMES)
    if frame_count % frame_skip != 0:
        continue

    # Crop ROI
    roi = frame[roi_y : roi_y + roi_height, roi_x : roi_x + roi_width]

    # Apply text recognition to a smaller region within the ROI
    student_id_region = roi[int(roi_height / 3) : int(2 * roi_height / 3), :]

    max_full_name = None
    max_student_id = None
    rotated_region = None

    for angle in rotation_angles:
        rotated_image = rotate_image(student_id_region, angle)
        result = recognize_student_id(rotated_image)
        if result:
            print(f"Student ID: {result[1]}")
            print(f"Name: {result[0]}")
            max_full_name = result[0]
            max_student_id = result[1]
            rotated_region = rotated_image
            break

    # Draw ROI outline
    cv2.rectangle(
        frame, (roi_x, roi_y), (roi_x + roi_width, roi_y + roi_height), (255, 0, 0), 2
    )

    # Display the result on the frame
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
        if max_student_id not in arr_student_id:
            arr_student_id.append(max_student_id)
            x = requests.get(
                URL + "?event=test&cardid=" + max_student_id + "&name=Test"
            )
            print(x.text)
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

    # Delay between frames
    if cv2.waitKey(frame_delay) == ord("q"):
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
