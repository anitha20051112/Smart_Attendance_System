import cv2
import numpy as np
import os
import pickle

data_path = "data"
model_file = "trained_model.yml"
label_map_file = "label_map.pkl"

face_recognizer = cv2.face.LBPHFaceRecognizer_create()

faces, labels = [], []

# Load existing label map
if os.path.exists(label_map_file):
    with open(label_map_file, "rb") as f:
        label_map = pickle.load(f)
else:
    label_map = {}

current_label = max(label_map.values(), default=-1) + 1

for file_name in os.listdir(data_path):
    if file_name.endswith(".jpg"):

        user_id = file_name.split(".")[1]

        if user_id not in label_map:
            label_map[user_id] = current_label
            current_label += 1

        img_path = os.path.join(data_path, file_name)

        gray_img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

        if gray_img is None:
            continue

        faces.append(gray_img)
        labels.append(label_map[user_id])

if len(faces) == 0:
    print("❌ No training images found")
    exit()

# First training
face_recognizer.train(faces, np.array(labels))

face_recognizer.save(model_file)

with open(label_map_file, "wb") as f:
    pickle.dump(label_map, f)

print("✅ Training completed successfully")
print("Users trained:", len(label_map))