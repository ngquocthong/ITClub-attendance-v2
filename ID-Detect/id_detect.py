import cv2
import pytesseract
import re
import requests
import pyglet


def recognize_student_id(frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    # pattern = r"(.+)\s+Student ID:\s+([A-Z]{3}\d{5,6})"
    pattern = r"(.+)\s+([A-Z]{3}\d{5,6})"
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


cap = cv2.VideoCapture(1)

# Set frame resolution
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 440)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 280)

# Determine rotation angles based on expected orientation
rotation_angles = [-10, 0, 10]  # Change angles as desired

arr_is_exist_student_id = []
URL = "https://script.google.com/macros/s/AKfycbxqKrzlIpLs7U9uRMToknoNXoHjzSJ8kfzgjnBsJQnsKqBqRg2OBcEAkne_S5Yci19NsA/exec"

while True:
    try:
        # Read frame from webcam
        ret, frame = cap.read()

        # Check if frame reading was successful
        if not ret:
            break

        max_full_name = None
        max_student_id = None
        rotated_region = None

        for angle in rotation_angles:
            rotated_image = rotate_image(frame, angle)
            result = recognize_student_id(rotated_image)
            if result:
                print(f"Student ID: {result[1]}")
                max_full_name = result[0]
                max_student_id = result[1]
                rotated_region = rotated_image
                break

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
            thankSound = pyglet.resource.media("assets/media/thank.mp3", streaming=True)
            thankSound.play()
            # try:
            #     if max_student_id not in arr_is_exist_student_id:
            #         arr_is_exist_student_id.append(max_student_id)
            #         x = requests.get(
            #             URL
            #             + "?event=infoSession&cardid="
            #             + max_student_id
            #             + "&name=Unknow"
            #         )
            #         print(x.text)
            #         thankSound = pyglet.resource.media(
            #             "assets/media/thank.mp3", streaming=True
            #         )
            #         thankSound.play()
            # except Exception as e:
            #     print("An error occurred:", str(e))
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
        if cv2.waitKey(1) == ord("q"):
            break
    except Exception as e:
        # print("KeyboardInterrupt detected. Stopping the webcam loop.")
        print("Exception caught:", str(e))
        break

# Release resources
cap.release()
cv2.destroyAllWindows()
