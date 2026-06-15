import cv2, sqlite3, pickle, os
from datetime import datetime
import pandas as pd

# Load trained model
recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read("trained_model.yml")

with open("label_map.pkl", "rb") as f:
    label_map = pickle.load(f)
reverse_label_map = {v: k for k, v in label_map.items()}

# Face detection
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

attendance_file = "attendance.xlsx"
marked_users = set()  # To avoid multiple marking in same session

def mark_attendance(user_id):
    if user_id in marked_users:
        return
    marked_users.add(user_id)

    now = datetime.now()
    date_str, time_str = now.strftime("%Y-%m-%d"), now.strftime("%H:%M:%S")

    conn = sqlite3.connect("attendance.db")
    cur = conn.cursor()

    # Check last attendance for same user
    cur.execute("SELECT date, time FROM attendance WHERE id=? ORDER BY date DESC, time DESC LIMIT 1", (user_id,))
    last = cur.fetchone()
    allow_insert = True
    if last:
        last_date, last_time = last
        last_dt = datetime.strptime(f"{last_date} {last_time}", "%Y-%m-%d %H:%M:%S")
        if (now - last_dt).total_seconds() < 3600:
            allow_insert = False

    if allow_insert:
        cur.execute("INSERT INTO attendance (id, date, time) VALUES (?, ?, ?)", (user_id, date_str, time_str))
        conn.commit()
        df_new = pd.DataFrame([[user_id, date_str, time_str]], columns=["ID", "Date", "Time"])
        if os.path.exists(attendance_file):
            df_existing = pd.read_excel(attendance_file)
            df_final = pd.concat([df_existing, df_new], ignore_index=True)
        else:
            df_final = df_new
        df_final.to_excel(attendance_file, index=False)

    conn.close()

# Initialize webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Could not open webcam.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Resize frame to speed up detection
    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
    gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)

    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=5)
    for (x, y, w, h) in faces:
        # Correct coordinates for original frame
        x1, y1, x2, y2 = x*2, y*2, (x+w)*2, (y+h)*2
        face = cv2.cvtColor(frame[y1:y2, x1:x2], cv2.COLOR_BGR2GRAY)
        face = cv2.resize(face, (200, 200))

        label, conf = recognizer.predict(face)
        if conf < 70 and label in reverse_label_map:
            user_id = reverse_label_map[label]
            conn = sqlite3.connect("attendance.db")
            cur = conn.cursor()
            cur.execute("SELECT name, department, year FROM students WHERE id=?", (user_id,))
            row = cur.fetchone()
            conn.close()
            if row:
                name, dept, year = row
                mark_attendance(user_id)
                text, color = f"{user_id} | {name} | {dept} | Year {year}", (0,255,0)
            else:
                text, color = f"Unregistered ID {user_id}", (0,165,255)
        else:
            text, color = "Unknown", (0,0,255)

        cv2.rectangle(frame, (x1,y1),(x2,y2), color, 2)
        cv2.putText(frame, text, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

    cv2.imshow("Face Recognition", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
