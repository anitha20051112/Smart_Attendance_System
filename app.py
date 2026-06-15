from flask import Flask, render_template, request, redirect, url_for, session,send_file
import subprocess
import sqlite3
import pandas as pd
from io import BytesIO

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "attendance.db")


app = Flask(__name__)
app.secret_key = "supersecretkey"
students = []

# ---------- DB Connection ----------
def get_db():
    print("📂 Flask is connecting to DB:", DB_PATH, flush=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
 

# ---------- Home ----------
@app.route('/')
def home():
    return render_template('dashboard.html')

# ---------- Admin Login ----------
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == "admin" and password == "1234":
            session['admin'] = True
            return redirect(url_for('view_database'))
        else:
            return render_template("admin_login.html", error="Invalid credentials")
    return render_template("admin_login.html")

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('home'))

# ---------- Capture Faces ----------
@app.route('/capture', methods=['POST'])
def capture():
    user_id = request.form['student_id']

    try:
        subprocess.run(["python", "capture_face.py", user_id], check=True)
    except subprocess.CalledProcessError as e:
        print("❌ Error capturing face:", e)

    return redirect(url_for('home'))

# ---------- Train Model ----------
@app.route('/train')
def train():
    try:
        subprocess.run(["python", "train_model.py"], check=True)
        print("✅ Model trained successfully")
    except subprocess.CalledProcessError as e:
        print("❌ Error training model:", e)

    return redirect(url_for('home'))

# ---------- Recognize & Mark Attendance ----------
@app.route('/recognize')
def recognize():
    subprocess.run(["python", "recognization.py"], shell=True)
    return redirect(url_for('home'))

# ---------- View Attendance ----------
@app.route('/attendance')
def attendance():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, s.name, s.department, s.year, a.date, a.time
        FROM attendance a
        LEFT JOIN students s ON a.id = s.id
        ORDER BY a.date DESC, a.time DESC
    """)
    records = cur.fetchall()
    conn.close()
    return render_template("attendance.html", records=records)

# ---------- Download Attendance Excel ----------
@app.route('/download_excel')
def download_excel():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT a.id, s.name, s.department, s.year, a.date, a.time
        FROM attendance a
        LEFT JOIN students s ON a.id = s.id
        ORDER BY a.date DESC, a.time DESC
    """)
    rows = cur.fetchall()
    conn.close()

    if not rows:
        return "No attendance records found."

    # Convert sqlite3.Row objects to dict
    df = pd.DataFrame([dict(r) for r in rows])
    df.rename(columns={
        "id": "Student ID",
        "name": "Name",
        "department": "Department",
        "year": "Year",
        "date": "Date",
        "time": "Time"
    }, inplace=True)

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Attendance")
    output.seek(0)

    return send_file(
        output,
        download_name="attendance.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# ---------- View / Manage Students ----------
@app.route('/view_database', methods=['GET', 'POST'])
def view_database():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        sid = request.form['id']
        name = request.form['name']
        dept = request.form['dept']
        year = int(request.form['year'])

        # Insert or update student based on primary key id
        cur.execute("""
            INSERT INTO students (id, name, department, year)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name=excluded.name,
                department=excluded.department,
                year=excluded.year
        """, (sid, name, dept, year))
        conn.commit()
        return redirect(url_for('view_database'))

    # Fetch all students
    cur.execute("SELECT * FROM students")
    students = [dict(row) for row in cur.fetchall()]

    # Filter by department
    selected_dept = request.args.get('filter_dept', '')
    if selected_dept:
        students = [s for s in students if s['department'] == selected_dept]

    # Get list of departments
    cur.execute("SELECT DISTINCT department FROM students")
    departments = [row['department'] for row in cur.fetchall()]

    conn.close()

    return render_template(
        'view_database.html',
        students=students,
        departments=departments,
        selected_dept=selected_dept
    )

# ---------- Delete Student ----------
@app.route('/delete_student/<sid>')
def delete_student(sid):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=?", (sid,))
    conn.commit()
    conn.close()

    return redirect(url_for('view_database'))

# ---------- Analytics ----------
@app.route('/analytics', methods=['GET', 'POST'])
def analytics():
    conn = get_db()
    cur = conn.cursor()

    # Fetch students & departments for filter dropdowns
    cur.execute("SELECT DISTINCT id, name FROM students")
    students = cur.fetchall()
    cur.execute("SELECT DISTINCT department FROM students")
    departments = [row['department'] for row in cur.fetchall()]

    # Default filters
    selected_student = request.form.get('student', 'all')
    selected_department = request.form.get('department', 'all')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    query = """
        SELECT a.id, s.name, s.department, a.date
        FROM attendance a
        LEFT JOIN students s ON a.id = s.id
        WHERE 1=1
    """
    params = []

    if selected_student != 'all':
        query += " AND a.id=?"
        params.append(selected_student)
    if selected_department != 'all':
        query += " AND s.department=?"
        params.append(selected_department)
    if start_date:
        query += " AND a.date>=?"
        params.append(start_date)
    if end_date:
        query += " AND a.date<=?"
        params.append(end_date)

    cur.execute(query, params)
    records = cur.fetchall()
    conn.close()

    # Prepare chart data (group by student name)
    if records:
        import pandas as pd
        df = pd.DataFrame(records, columns=['id', 'name', 'department', 'date'])
        chart_data = df.groupby('name').size().reset_index(name='count')
        chart_labels = chart_data['name'].tolist()
        chart_counts = chart_data['count'].tolist()
    else:
        chart_labels, chart_counts = [], []

    return render_template(
        'analytics.html',
        students=students,
        departments=departments,
        chart_labels=chart_labels,
        chart_counts=chart_counts,
        selected_student=selected_student,
        selected_department=selected_department,
        start_date=start_date,
        end_date=end_date
    )


# ---------- Run App ----------
if __name__ == "__main__":
    app.run(debug=True)
