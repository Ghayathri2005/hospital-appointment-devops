from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = "hospital-devops-secret"
DATABASE = "hospital.db"

DOCTORS = [
    ("Dr. Anitha Kumar", "Cardiologist", "09:00 AM - 01:00 PM"),
    ("Dr. Rahul Sharma", "General Physician", "10:00 AM - 02:00 PM"),
    ("Dr. Priya Menon", "Dermatologist", "09:30 AM - 01:30 PM"),
    ("Dr. Arjun Rao", "Orthopedic", "02:00 PM - 06:00 PM"),
    ("Dr. Meena Iyer", "Pediatrician", "03:00 PM - 07:00 PM"),
]

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            availability TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            doctor_id INTEGER NOT NULL,
            appointment_date TEXT NOT NULL,
            appointment_time TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (doctor_id) REFERENCES doctors(id)
        )
    """)
    if conn.execute("SELECT COUNT(*) FROM doctors").fetchone()[0] == 0:
        conn.executemany(
            "INSERT INTO doctors (name, specialization, availability) VALUES (?, ?, ?)",
            DOCTORS
        )
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    count = conn.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]
    conn.close()
    return render_template("index.html", doctors=doctors, appointment_count=count)

@app.route("/doctors")
def doctors():
    conn = get_db()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()
    conn.close()
    return render_template("doctors.html", doctors=doctors)

@app.route("/book", methods=["GET", "POST"])
def book():
    conn = get_db()
    doctors = conn.execute("SELECT * FROM doctors").fetchall()

    if request.method == "POST":
        patient_name = request.form.get("patient_name", "").strip()
        phone = request.form.get("phone", "").strip()
        doctor_id = request.form.get("doctor_id")
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")

        if not all([patient_name, phone, doctor_id, appointment_date, appointment_time]):
            flash("Please fill in all fields.", "error")
            conn.close()
            return render_template("book.html", doctors=doctors)

        conn.execute("""
            INSERT INTO appointments
            (patient_name, phone, doctor_id, appointment_date, appointment_time, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            patient_name, phone, doctor_id, appointment_date,
            appointment_time, datetime.now().isoformat(timespec="seconds")
        ))
        conn.commit()
        conn.close()
        flash("Appointment booked successfully!", "success")
        return redirect(url_for("appointments"))

    conn.close()
    return render_template("book.html", doctors=doctors)

@app.route("/appointments")
def appointments():
    conn = get_db()
    appointments = conn.execute("""
        SELECT a.*, d.name AS doctor_name, d.specialization
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        ORDER BY a.appointment_date, a.appointment_time
    """).fetchall()
    conn.close()
    return render_template("appointments.html", appointments=appointments)

@app.route("/cancel/<int:appointment_id>", methods=["POST"])
def cancel(appointment_id):
    conn = get_db()
    conn.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    flash("Appointment cancelled.", "success")
    return redirect(url_for("appointments"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
