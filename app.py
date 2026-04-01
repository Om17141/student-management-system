from flask import Flask, render_template, request, redirect, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_table():
    conn = get_db()
    
    conn.execute("DROP TABLE IF EXISTS students")
    
    conn.execute('''
        CREATE TABLE students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            roll TEXT,
            subject TEXT,
            marks INTEGER
        )
    ''')
    
    conn.commit()
    conn.close()

create_table()

# ✅ SINGLE INDEX FUNCTION (WITH DASHBOARD)
@app.route("/", methods=["GET", "POST"])
def index():
    conn = get_db()
    search = request.form.get("search")

    if search:
        students = conn.execute(
            "SELECT * FROM students WHERE name LIKE ?",
            ('%' + search + '%',)
        ).fetchall()
    else:
        students = conn.execute("SELECT * FROM students").fetchall()

    # 🔥 FIX: marks ko int me convert
    marks_list = [int(s["marks"]) for s in students]

    total = len(students)

    if total > 0:
        avg = sum(marks_list) / total
        topper = students[marks_list.index(max(marks_list))]
        pass_count = len([m for m in marks_list if m >= 40])
        pass_percent = (pass_count / total) * 100
    else:
        avg = 0
        topper = None
        pass_percent = 0

    conn.close()

    return render_template(
        "index.html",
        students=students,
        total=total,
        avg=round(avg, 2),
        topper=topper,
        pass_percent=round(pass_percent, 2)
    )

# ADD
@app.route("/add", methods=["GET", "POST"])
def add():
    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        subject = request.form["subject"]
        marks = request.form["marks"]

        if not name or not roll or not subject or not marks:
            flash("All fields are required!")
            return redirect("/add")

        conn = get_db()
        conn.execute("INSERT INTO students (name, roll, subject, marks) VALUES (?, ?, ?, ?)",
                     (name, roll, subject, marks))
        conn.commit()
        conn.close()

        flash("Student Added Successfully!")
        return redirect("/")

    return render_template("add.html")

# DELETE
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM students WHERE id=?", (id,))
    conn.commit()
    conn.close()
    flash("Student Deleted!")
    return redirect("/")

# EDIT
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):
    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        roll = request.form["roll"]
        subject = request.form["subject"]
        marks = request.form["marks"]

        conn.execute("UPDATE students SET name=?, roll=?, subject=?, marks=? WHERE id=?",
                     (name, roll, subject, marks, id))
        conn.commit()
        conn.close()

        flash("Student Updated!")
        return redirect("/")

    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("edit.html", student=student)

# VIEW
@app.route("/view/<int:id>")
def view(id):
    conn = get_db()
    student = conn.execute("SELECT * FROM students WHERE id=?", (id,)).fetchone()
    conn.close()

    percentage = int(student["marks"])

    if percentage >= 80:
        grade = "A"
    elif percentage >= 50:
        grade = "B"
    else:
        grade = "C"

    return render_template("view.html", student=student, percentage=percentage, grade=grade)

# ✅ ALWAYS KEEP THIS AT LAST
if __name__ == "__main__":
    app.run(debug=True)