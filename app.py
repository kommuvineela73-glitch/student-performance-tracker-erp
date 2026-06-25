# ==========================================================
# STUDENT PERFORMANCE TRACKER ERP (CLEAN VERSION)
# ==========================================================

import os
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, jsonify, session
)

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from config import Config
from models import db, Student, Subject, Grade, User

# ==========================================================
# APP CONFIG
# ==========================================================

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)

# ==========================================================
# LOGIN DECORATOR (FIXED)
# ==========================================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

# ==========================================================
# CREATE DB + DEFAULT ADMIN
# ==========================================================

with app.app_context():
    db.create_all()

    admin = User.query.filter_by(username="admin").first()
    if not admin:
        admin = User(
            full_name="Administrator",
            username="admin",
            email="admin@test.com",
            password=generate_password_hash("admin123"),
            role="Admin",
            dark_mode=False
        )
        db.session.add(admin)
        db.session.commit()
        print("Default admin created: admin / admin123")


# ==========================================================
# DASHBOARD
# ==========================================================

@app.route("/")
@login_required
def dashboard():

    total_students = Student.query.count()
    total_subjects = Subject.query.count()
    grades = Grade.query.all()

    if grades:
        average_marks = round(sum(g.marks for g in grades) / len(grades), 2)
        highest_marks = max(g.marks for g in grades)
        lowest_marks = min(g.marks for g in grades)
    else:
        average_marks = highest_marks = lowest_marks = 0

    topper_name = "N/A"
    topper_total = 0
    passed_students = 0
    failed_students = 0

    students = Student.query.all()
    recent_students = Student.query.order_by(Student.id.asc()).limit(5).all()
    for s in students:
        total = sum(g.marks for g in s.grades)

        if total > topper_total:
            topper_total = total
            topper_name = s.name

        if s.grades:
            avg = total / len(s.grades)
            if avg >= 35:
                passed_students += 1
            else:
                failed_students += 1

    return render_template(
    "dashboard.html",
    total_students=total_students,
    total_subjects=total_subjects,
    average_marks=average_marks,
    highest_marks=highest_marks,
    lowest_marks=lowest_marks,
    topper_name=topper_name,
    passed_students=passed_students,
    failed_students=failed_students,
    recent_students=recent_students   # MUST be here
) 

# ==========================================================
# STUDENTS
# ==========================================================

@app.route("/students")
@login_required
def students():
    data = Student.query.order_by(Student.id.asc()).all()


    return render_template("students.html", students=data)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add_student():

    if request.method == "POST":

        roll = request.form["roll_number"]

        if Student.query.filter_by(roll_number=roll).first():
            flash("Roll number already exists", "danger")
            return redirect(url_for("add_student"))

        student = Student(
            name=request.form["name"],
            roll_number=roll,
            branch=request.form.get("branch"),
            year=request.form.get("year"),
            section=request.form.get("section"),
            email=request.form.get("email"),
            phone=request.form.get("phone")
        )

        photo = request.files.get("photo")
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            student.photo = filename

        db.session.add(student)
        db.session.commit()

        flash("Student added", "success")
        return redirect(url_for("students"))

    return render_template("add_student.html")


@app.route("/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_student(id):

    student = Student.query.get_or_404(id)

    if request.method == "POST":
        student.name = request.form["name"]
        student.roll_number = request.form["roll_number"]
        student.branch = request.form["branch"]
        student.year = request.form["year"]
        student.section = request.form["section"]
        student.email = request.form["email"]
        student.phone = request.form["phone"]

        photo = request.files.get("photo")
        if photo and photo.filename:
            filename = secure_filename(photo.filename)
            photo.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
            student.photo = filename

        db.session.commit()
        flash("Updated successfully", "success")
        return redirect(url_for("students"))

    return render_template("edit_student.html", student=student)


@app.route("/delete/<int:id>", methods=["POST"])
@login_required
def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash("Deleted successfully", "warning")
    return redirect(url_for("students"))


# ==========================================================
# SUBJECTS
# ==========================================================

@app.route("/subjects", methods=["GET", "POST"])
@login_required
def subjects():

    if request.method == "POST":
        name = request.form["name"].strip()

        if not name:
            flash("Subject cannot be empty", "danger")
            return redirect(url_for("subjects"))

        if Subject.query.filter_by(name=name).first():
            flash("Subject exists", "warning")
            return redirect(url_for("subjects"))

        db.session.add(Subject(name=name))
        db.session.commit()

    data = Subject.query.order_by(Subject.name).all()
    return render_template("subjects.html", subjects=data)


@app.route("/subjects/delete/<int:id>")
@login_required
def delete_subject(id):
    sub = Subject.query.get_or_404(id)
    db.session.delete(sub)
    db.session.commit()
    return redirect(url_for("subjects"))

# ==========================================================
# MARKS MODULE
# ==========================================================

@app.route("/marks", methods=["GET", "POST"])
@login_required
def marks():

    students = Student.query.all()
    grades = Grade.query.order_by(Grade.id.desc()).all()

    if request.method == "POST":

        if not request.form["marks"]:
            flash("Marks required", "danger")
            return redirect(url_for("marks"))

        student_id = request.form["student_id"]
        subject = request.form["subject"].strip()
        marks_value = float(request.form["marks"])

        # ✅ CHECK IF SAME STUDENT + SUBJECT ALREADY EXISTS
        existing = Grade.query.filter_by(
            student_id=student_id,
            subject=subject
        ).first()

        if existing:
            # UPDATE OLD RECORD
            existing.marks = marks_value
            flash("Marks updated successfully", "success")
        else:
            # INSERT NEW RECORD
            grade = Grade(
                student_id=student_id,
                subject=subject,
                marks=marks_value
            )
            db.session.add(grade)
            flash("Marks added successfully", "success")

        db.session.commit()
        return redirect(url_for("marks"))

    return render_template(
        "marks.html",
        students=students,
        grades=grades
    )


# ==========================================================
# DELETE MARK
# ==========================================================

@app.route("/marks/delete/<int:id>", methods=["POST"])
@login_required
def delete_mark(id):

    grade = Grade.query.get_or_404(id)
    db.session.delete(grade)
    db.session.commit()

    flash("Marks deleted successfully", "warning")
    return redirect(url_for("marks"))


# ==========================================================
# STUDENT REPORT (FIXED)
# ==========================================================
@app.route("/report/<int:student_id>")
@login_required
def student_report(student_id):

    student = Student.query.get_or_404(student_id)

    grades_raw = Grade.query.filter_by(student_id=student.id).all()

    # ✅ remove duplicates (keep latest value)
    subject_map = {}

    for g in grades_raw:
        subject_map[g.subject] = g.marks

    grades = [
        {"subject": sub, "marks": mark}
        for sub, mark in subject_map.items()
    ]

    total = sum(g["marks"] for g in grades)
    average = round(total / len(grades), 2) if grades else 0

    return render_template(
        "report.html",
        student=student,
        grades=grades,
        total=total,
        average=average
    )
# ==========================================================
# ANALYTICS MODULE
# ==========================================================

@app.route("/analytics")
@login_required
def analytics():

    students = Student.query.all()
    grades = Grade.query.all()

    class_avg = round(
        sum(g.marks for g in grades) / len(grades),
        2
    ) if grades else 0

    topper = "N/A"
    max_total = 0

    for s in students:
        total = sum(g.marks for g in s.grades)
        if total > max_total:
            max_total = total
            topper = s.name

    subjects = Subject.query.all()

    subject_names = []
    avg_marks = []

    for sub in subjects:
        subject_grades = Grade.query.filter_by(subject=sub.name).all()

        subject_names.append(sub.name)

        avg_marks.append(
            round(sum(g.marks for g in subject_grades) / len(subject_grades), 2)
            if subject_grades else 0
        )

    return render_template(
        "analytics.html",
        topper_name=topper,
        class_average=class_avg,
        subject_names=subject_names,
        avg_marks=avg_marks
    )


# ==========================================================
# AUTH
# ==========================================================

@app.route("/login", methods=["GET", "POST"])
def login():

    if session.get("user_id"):
        return redirect(url_for("dashboard"))

    if request.method == "POST":

        user = User.query.filter_by(username=request.form["username"]).first()

        if user and check_password_hash(user.password, request.form["password"]):
            session["user_id"] = user.id
            session["username"] = user.username
            return redirect(url_for("dashboard"))

        flash("Invalid credentials", "danger")

    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        if User.query.filter_by(username=request.form["username"]).first():
            flash("Username exists", "warning")
            return redirect(url_for("register"))

        user = User(
            full_name=request.form["full_name"],
            username=request.form["username"],
            email=request.form["email"],
            password=generate_password_hash(request.form["password"]),
            role="Teacher"
        )

        db.session.add(user)
        db.session.commit()

        flash("Registered successfully", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==========================================================
# SETTINGS PAGE (MISSING FIX - THIS WAS YOUR ERROR)
# ===========================================================
@app.route("/settings")
@login_required
def settings():
    user = db.session.get(User, session["user_id"])
    return render_template("settings.html", user=user)

# ==========================================================
# SETTINGS APIs
# ==========================================================

@app.route("/api/update_profile", methods=["POST"])
@login_required
def update_profile():
    data = request.get_json()
    user = db.session.get(User, session["user_id"])

    user.username = data.get("username")
    user.email = data.get("email")

    db.session.commit()
    return jsonify({"message": "Profile updated"})


@app.route("/api/change_password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json()
    user = db.session.get(User, session["user_id"])

    if not check_password_hash(user.password, data["current_password"]):
        return jsonify({"message": "Wrong current password"})

    if data["new_password"] != data["confirm_password"]:
        return jsonify({"message": "Passwords do not match"})

    user.password = generate_password_hash(data["new_password"])
    db.session.commit()

    return jsonify({"message": "Password changed successfully"})


@app.route("/api/toggle_dark_mode", methods=["POST"])
@login_required
def toggle_dark_mode():
    user = db.session.get(User, session["user_id"])
    user.dark_mode = not user.dark_mode
    db.session.commit()

    return jsonify({"dark_mode": user.dark_mode})


# ==========================================================
# REPORTS PAGE (FIXED)
# ==========================================================

@app.route("/reports")
@login_required
def reports():
    students = Student.query.order_by(Student.id.desc()).all()
    return render_template("reports.html", students=students)

# ==========================================================
# RUN APP
# ==========================================================

if __name__ == "__main__":
    app.run(debug=True)
