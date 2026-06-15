import cv2
import os
import sys

haar_cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
face_classifier = cv2.CascadeClassifier(haar_cascade_path)

if face_classifier.empty():
    print("❌ Error: Haarcascade file could not be loaded!")
    exit()

user_id = sys.argv[1]
img_id = 0

save_path = "data"
os.makedirs(save_path, exist_ok=True)

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Error: Could not open webcam!")
    exit()

print(f"✅ Capturing faces for User ID: {user_id}")

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Failed to capture frame")
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    for (x, y, w, h) in faces:
        img_id += 1
        face = gray[y:y+h, x:x+w]
        face = cv2.resize(face, (200, 200))  # crop to 200x200

        file_name = f"{save_path}/user.{user_id}.{img_id}.jpg"
        cv2.imwrite(file_name, face)
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0,255,0), 2)
        cv2.putText(frame, f"Images Captured: {img_id}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,0,0), 2)

    cv2.imshow("Face Capture", frame)

    if cv2.waitKey(1) == 13 or img_id >= 50:  # Enter or 50 images
        print(f"🛑 Capture completed for User {user_id}")
        break

cap.release()
cv2.destroyAllWindows()

