from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
import uuid
import json
from sqlalchemy import or_, Text

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
    lead_source = db.Column(db.String(50), nullable=True)  # Google, WhatsApp, Referral, Other
    referral_name = db.Column(db.String(100), nullable=True)  # If lead_source is Referral
    preferred_timing = db.Column(db.String(50), nullable=True)  # Preferred demo timing
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
    teaching_experience = db.Column(db.Integer, default=0)  # Years of teaching experience
    teaching_experience_details = db.Column(db.Text, nullable=True)  # Details about experience
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
    reminder_sent_at = db.Column(db.DateTime, nullable=True)
    reminder_notes = db.Column(db.Text, nullable=True)
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

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_id = db.Column(db.String(10), unique=True, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    notification_type = db.Column(db.String(20), nullable=False)  # new_lead, assignment, upcoming_demo, unassigned_lead, demo_failed
    is_read = db.Column(db.Boolean, default=False)
    is_urgent = db.Column(db.Boolean, default=False)
    related_id = db.Column(db.Integer, nullable=True)  # Can store student_id, teacher_id, assignment_id, or demo_id
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(Notification, self).__init__(**kwargs)
        if not self.notification_id:
            self.notification_id = f"NOT{uuid.uuid4().hex[:7].upper()}"
            
    @staticmethod
    def create_notification(title, message, notification_type, related_id=None, is_urgent=False):
        notification = Notification(
            title=title,
            message=message,
            notification_type=notification_type,
            related_id=related_id,
            is_urgent=is_urgent
        )
        db.session.add(notification)
        db.session.commit()
        return notification
    
    @staticmethod
    def get_unread_notifications():
        return Notification.query.filter_by(is_read=False).order_by(Notification.created_at.desc()).all()
    
    @staticmethod
    def get_recent_notifications(limit=10):
        return Notification.query.order_by(Notification.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_urgent_notifications():
        return Notification.query.filter_by(is_urgent=True, is_read=False).all()
    
    @staticmethod
    def mark_as_read(notification_id):
        notification = Notification.query.filter_by(id=notification_id).first()
        if notification:
            notification.is_read = True
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def delete_notification(notification_id):
        notification = Notification.query.filter_by(id=notification_id).first()
        if notification:
            db.session.delete(notification)
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def check_unassigned_leads():
        # Find unassigned leads that are older than 1 hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        unassigned_leads = Student.query.filter(
            Student.status == "New",
            Student.created_at <= one_hour_ago
        ).all()
        
        for lead in unassigned_leads:
            # Check if we already have a notification for this lead
            existing_notification = Notification.query.filter_by(
                notification_type='unassigned_lead',
                related_id=lead.id,
                is_read=False
            ).first()
            
            if not existing_notification:
                Notification.create_notification(
                    title=f"Unassigned Lead: {lead.name}",
                    message=f"Lead {lead.name} has been unassigned for more than 1 hour. Please assign a teacher.",
                    notification_type='unassigned_lead',
                    related_id=lead.id,
                    is_urgent=True
                )
    
    @staticmethod
    def check_upcoming_demos():
        # Find demos that are scheduled within the next hour
        now = datetime.utcnow()
        one_hour_later = now + timedelta(hours=1)
        
        upcoming_demos = Demo.query.filter(
            Demo.status == "Scheduled",
            Demo.scheduled_date >= now,
            Demo.scheduled_date <= one_hour_later
        ).all()
        
        for demo in upcoming_demos:
            # Check if we already have a notification for this demo
            existing_notification = Notification.query.filter_by(
                notification_type='upcoming_demo',
                related_id=demo.id,
                is_read=False
            ).first()
            
            if not existing_notification:
                student_name = demo.assignment.student.name
                teacher_name = demo.assignment.teacher.name
                
                Notification.create_notification(
                    title=f"Upcoming Demo: {student_name} with {teacher_name}",
                    message=f"A demo for {student_name} with {teacher_name} is scheduled within the next hour at {demo.scheduled_date.strftime('%H:%M')}.",
                    notification_type='upcoming_demo',
                    related_id=demo.id,
                    is_urgent=True
                )

class CommunicationTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # email, sms, whatsapp
    category = db.Column(db.String(50), nullable=False)  # lead_followup, reminder, confirmation, etc.
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        super(CommunicationTemplate, self).__init__(**kwargs)
        if not self.template_id:
            self.template_id = f"TPL{uuid.uuid4().hex[:7].upper()}"
    
    def render_template(self, **kwargs):
        """
        Render the template content with provided variables
        
        Parameters:
        - kwargs: Dictionary of variables to substitute in the template
          (e.g., student_name, teacher_name, demo_date, etc.)
        
        Returns:
        - Tuple of (rendered_subject, rendered_content)
        """
        rendered_subject = self.subject
        rendered_content = self.content
        
        # Replace variables in template content
        for key, value in kwargs.items():
            placeholder = f"{{{{{key}}}}}"
            rendered_subject = rendered_subject.replace(placeholder, str(value))
            rendered_content = rendered_content.replace(placeholder, str(value))
            
        return rendered_subject, rendered_content
        
class Communication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    communication_id = db.Column(db.String(10), unique=True, nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('communication_template.id'), nullable=True)
    subject = db.Column(db.String(200), nullable=True)  # For emails
    content = db.Column(db.Text, nullable=False)
    type = db.Column(db.String(50), nullable=False)  # email, sms, whatsapp
    status = db.Column(db.String(20), default="Pending")  # Pending, Sent, Failed
    recipient = db.Column(db.String(100), nullable=False)  # Email or phone number
    recipient_name = db.Column(db.String(100), nullable=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=True)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teacher.id'), nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    template = db.relationship('CommunicationTemplate', backref=db.backref('communications', lazy=True))
    student = db.relationship('Student', backref=db.backref('communications', lazy=True))
    teacher = db.relationship('Teacher', backref=db.backref('communications', lazy=True))
    
    def __init__(self, **kwargs):
        super(Communication, self).__init__(**kwargs)
        if not self.communication_id:
            self.communication_id = f"COM{uuid.uuid4().hex[:7].upper()}"
