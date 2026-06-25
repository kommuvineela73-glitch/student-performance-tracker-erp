from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# =========================
# USER MODEL (ADMIN / TEACHER)
# =========================
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)  # hashed password only
    role = db.Column(db.String(20), default="Teacher")
    dark_mode = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# STUDENT MODEL
# =========================
class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(120), nullable=False)
    roll_number = db.Column(db.String(50), unique=True, nullable=False)

    branch = db.Column(db.String(50))
    year = db.Column(db.String(20))
    section = db.Column(db.String(10))

    email = db.Column(db.String(120))
    phone = db.Column(db.String(20))
    photo = db.Column(db.String(200))

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship with grades
    grades = db.relationship(
        "Grade",
        back_populates="student",
        cascade="all, delete-orphan"
    )


# =========================
# SUBJECT MODEL
# =========================
class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)


# =========================
# GRADE MODEL
# =========================
class Grade(db.Model):
    __tablename__ = "grades"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("students.id", ondelete="CASCADE"),
        nullable=False
    )

    subject = db.Column(db.String(100), nullable=False)
    marks = db.Column(db.Float, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # relationship back to student
    student = db.relationship(
        "Student",
        back_populates="grades"
    )