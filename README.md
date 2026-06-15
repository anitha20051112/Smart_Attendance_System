# Smart Attendance System – File Description & Workflow

## Project Overview

A Face Recognition Based Smart Attendance System developed using Python, Flask, OpenCV, and SQLite. The system captures student face images, trains a face recognition model, identifies students in real time, and automatically records attendance.

---

## Technologies Used

* Python
* Flask
* OpenCV
* SQLite
* HTML
* CSS
* JavaScript
* Pandas

---

## File Descriptions

### Core Python Files

* **app.py** – Main Flask application that runs the web interface and manages attendance operations.
* **capture_face.py** – Captures student face images through the webcam and stores them for training.
* **train_model.py** – Trains the face recognition model using the captured images.
* **recognization.py** – Recognizes faces in real time and marks attendance automatically.
* **init_db.py** – Creates and initializes the attendance database.
* **check_db.py** – Displays and verifies stored attendance records.
* **check_schema.py** – Checks the database structure and table schema.

### Templates Folder

* **admin_login.html** – Administrator login page.
* **dashboard.html** – Main dashboard displaying system options and statistics.
* **attendance.html** – Attendance records page.
* **manage_students.html** – Student management interface.
* **analytics.html** – Attendance analysis and reports.
* **view_database.html** – Database viewing page.

### Other Files

* **attendance.db** – SQLite database storing student and attendance information.
* **attendance.xlsx** – Exported attendance records in Excel format.
* **static/** – Contains CSS, JavaScript, and images used by the web application.
* **Templates/** – Contains all HTML pages rendered by Flask.

---

## Auto-Generated Files

The following files are generated automatically and are not included in this repository:

* **data/** – Stores captured face images of students.
* **trained_model.yml** – Face recognition model generated after training.
* **label_map.pkl** – Stores mappings between student names and model labels.
* ****pycache**/** – Python cache files automatically created during execution.

---

## System Workflow

### Step 1: Initialize Database

Run:

```bash
python init_db.py
```

This creates the attendance database.

### Step 2: Capture Student Images

Run:

```bash
python capture_face.py
```

Student face images are captured through the webcam and stored inside the **data/** folder.

### Step 3: Train the Recognition Model

Run:

```bash
python train_model.py
```

This generates:

* `trained_model.yml`
* `label_map.pkl`

### Step 4: Start the Application

Run:

```bash
python app.py
```

The Flask web application starts and opens the attendance management system.

### Step 5: Face Recognition & Attendance

* The system recognizes students using the trained model.
* Attendance is marked automatically.
* Records are stored in **attendance.db**.
* Attendance reports can be exported to **attendance.xlsx**.

---

## Features

* Face Registration
* Face Recognition Based Attendance
* Automatic Attendance Marking
* Student Management
* Attendance Analytics
* Database Management
* Excel Export Support
* Web-Based Dashboard

---

## Note

The `data/`, `trained_model.yml`, `label_map.pkl`, and `__pycache__/` files are excluded from this repository because they are automatically generated during execution. The `data/` folder may also contain personal training images and is therefore not included for privacy reasons.

To use this project:

1. Run `init_db.py`
2. Capture student images using `capture_face.py`
3. Train the model using `train_model.py`
4. Start the application using `app.py`

The required model files and mappings will be generated automatically during the training process.
