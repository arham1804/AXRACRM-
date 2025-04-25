from app import db
from flask_login import UserMixin
from datetime import datetime
import uuid
import json

class Admin(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lead_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    class_level = db.Column(db.String(20), nullable=False)
    subjects = db.Column(db.Text, nullable=False)  # JSON string
    fee = db.Column(db.Float, nullable=False)
    area = db.Column(db.String(100), nullable=False)
    gender_preference = db.Column(db.String(10), nullable=False)  # MALE, FEMALE, ANY
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="New")  # New, Assigned, Converted, Lost
    
    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)
        if not self.lead_id:
            self.lead_id = f"LD{uuid.uuid4().hex[:8].upper()}"
    
    def get_subjects_list(self):
        return json.loads(self.subjects)

class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    alternate_phone = db.Column(db.String(15))
    preferred_areas = db.Column(db.Text, nullable=False)  # JSON string
    preferred_subjects = db.Column(db.Text, nullable=False)  # JSON string
    gender = db.Column(db.String(10), nullable=False)  # MALE, FEMALE
    pincode = db.Column(db.String(10), nullable=False)
    qualification = db.Column(db.String(100), nullable=False)
    stream = db.Column(db.String(50), nullable=False)
    board = db.Column(db.String(10), nullable=False)  # CBSE, ICSE, UP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Active")  # Active, Inactive
    
    def __init__(self, **kwargs):
        super(Teacher, self).__init__(**kwargs)
        if not self.teacher_id:
            self.teacher_id = f"TCH{uuid.uuid4().hex[:7].upper()}"
    
    def get_preferred_areas_list(self):
        return json.loads(self.preferred_areas)
    
    def get_preferred_subjects_list(self):
        return json.loads(self.preferred_subjects)

class TuitionAssignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tuition_id = db.Column(db.String(10), unique=True, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=False)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default="Pending")  # Pending, Demo Scheduled, Converted, Cancelled
    
    # Relationships
    student = db.relationship('Student', backref=db.backref('assignments', lazy=True))
    teacher = db.relationship('Teacher', backref=db.backref('assignments', lazy=True))
    
    def __init__(self, **kwargs):
        super(TuitionAssignment, self).__init__(**kwargs)
        if not self.tuition_id:
            self.tuition_id = f"TUI{uuid.uuid4().hex[:7].upper()}"

class Demo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    assignment_id = db.Column(db.Integer, db.ForeignKey('tuition_assignment.id'), nullable=False)
    scheduled_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="Scheduled")  # Scheduled, Completed, Cancelled
    reminder_sent = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    assignment = db.relationship('TuitionAssignment', backref=db.backref('demos', lazy=True))

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    demo_id = db.Column(db.Integer, db.ForeignKey('demo.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5
    comments = db.Column(db.Text)
    student_interest = db.Column(db.String(20), nullable=False)  # Interested, Not Interested, Maybe
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    demo = db.relationship('Demo', backref=db.backref('feedback', lazy=True, uselist=False))
