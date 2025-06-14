from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms import TextAreaField, SelectField, FloatField, IntegerField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, ValidationError, Optional, NumberRange
import json

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class StudentLeadForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    class_level = SelectField('Class', 
                            choices=[
                                ('', 'Select Class'),
                                ('Primary', 'Primary (1-5)'),
                                ('Middle', 'Middle (6-8)'),
                                ('Secondary', 'Secondary (9-10)'),
                                ('Sr. Secondary', 'Sr. Secondary (11-12)'),
                                ('College', 'College')
                            ],
                            validators=[DataRequired()])
    subjects = SelectMultipleField('Subjects', 
                                  choices=[
                                      ('All Subjects', 'All Subjects'),
                                      ('Mathematics', 'Mathematics'),
                                      ('Science', 'Science'),
                                      ('Physics', 'Physics'),
                                      ('Chemistry', 'Chemistry'),
                                      ('Biology', 'Biology'),
                                      ('English', 'English'),
                                      ('Hindi', 'Hindi'),
                                      ('Social Studies', 'Social Studies'),
                                      ('History', 'History'),
                                      ('Geography', 'Geography'),
                                      ('Computer Science', 'Computer Science'),
                                      ('Accountancy', 'Accountancy'),
                                      ('Business Studies', 'Business Studies'),
                                      ('Economics', 'Economics')
                                  ],
                                  validators=[DataRequired()])
    fee = FloatField('Expected Fee (₹)', validators=[DataRequired()])
    area = StringField('Area/Locality', validators=[DataRequired(), Length(max=100)])
    gender_preference = SelectField('Gender Preference', 
                                  choices=[
                                      ('ANY', 'Any'),
                                      ('MALE', 'Male'),
                                      ('FEMALE', 'Female')
                                  ],
                                  validators=[DataRequired()])
    lead_source = SelectField('Lead Source', 
                           choices=[
                               ('', 'Select Source'),
                               ('Google', 'Google'),
                               ('WhatsApp', 'WhatsApp'),
                               ('Referral', 'Referral'),
                               ('Other', 'Other')
                           ],
                           validators=[DataRequired()])
    referral_name = StringField('Referral Name', validators=[Optional(), Length(max=100)])
    preferred_timing = SelectField('Preferred Demo Timing',
                                choices=[
                                    ('', 'Select Timing'),
                                    ('Morning (9AM-12PM)', 'Morning (9AM-12PM)'),
                                    ('Afternoon (12PM-3PM)', 'Afternoon (12PM-3PM)'),
                                    ('Evening (3PM-6PM)', 'Evening (3PM-6PM)'),
                                    ('Night (6PM-9PM)', 'Night (6PM-9PM)')
                                ],
                                validators=[Optional()])
    submit = SubmitField('Save Lead')

from flask_wtf.file import FileField, FileAllowed

class TeacherForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    alternate_phone = StringField('Alternate Phone Number', validators=[Optional(), Length(min=10, max=15)])
    preferred_areas = TextAreaField('Preferred Areas (minimum 5, one per line)', validators=[DataRequired()])
    
    def validate_preferred_areas(form, field):
        areas = [area.strip() for area in field.data.splitlines() if area.strip()]
        if len(areas) < 5:
            raise ValidationError('Please enter at least 5 preferred areas')
    
    preferred_subjects = SelectMultipleField('Preferred Subjects', 
                                          choices=[
                                              ('All Subjects', 'All Subjects'),
                                              ('Mathematics', 'Mathematics'),
                                              ('Science', 'Science'),
                                              ('Physics', 'Physics'),
                                              ('Chemistry', 'Chemistry'),
                                              ('Biology', 'Biology'),
                                              ('English', 'English'),
                                              ('Hindi', 'Hindi'),
                                              ('Social Studies', 'Social Studies'),
                                              ('History', 'History'),
                                              ('Geography', 'Geography'),
                                              ('Computer Science', 'Computer Science'),
                                              ('Accountancy', 'Accountancy'),
                                              ('Business Studies', 'Business Studies'),
                                              ('Economics', 'Economics')
                                          ],
                                          validators=[DataRequired()])
    gender = SelectField('Gender', 
                        choices=[
                            ('MALE', 'Male'),
                            ('FEMALE', 'Female')
                        ],
                        validators=[DataRequired()])
    pincode = StringField('Pincode', validators=[DataRequired(), Length(max=10)])
    qualification = StringField('Last Qualification', validators=[DataRequired(), Length(max=100)])
    stream = SelectField('Stream', 
                        choices=[
                            ('', 'Select Stream'),
                            ('Science', 'Science'),
                            ('Commerce', 'Commerce'),
                            ('Arts', 'Arts'),
                            ('Engineering', 'Engineering'),
                            ('Medical', 'Medical'),
                            ('Other', 'Other')
                        ],
                        validators=[DataRequired()])
    board = SelectField('School Board', 
                       choices=[
                           ('CBSE', 'CBSE'),
                           ('ICSE', 'ICSE'),
                           ('UP', 'UP')
                       ],
                       validators=[DataRequired()])
    teaching_experience = IntegerField('Teaching Experience (Years)', validators=[Optional(), NumberRange(min=0, max=50)])
    teaching_experience_details = TextAreaField('Experience Details', validators=[Optional()])
    submit = SubmitField('Save Teacher')

class TeacherBulkUploadForm(FlaskForm):
    file = FileField('Upload Teacher File (CSV or Excel)', validators=[
        FileAllowed(['csv', 'xls', 'xlsx'], 'CSV and Excel files only!'),
        DataRequired()
    ])
    submit = SubmitField('Upload')

class AssignTeacherForm(FlaskForm):
    teacher_id = SelectField('Select Teacher', coerce=int, validators=[DataRequired()])
    submit = SubmitField('Assign Teacher')

class ScheduleDemoForm(FlaskForm):
    scheduled_date = DateTimeField('Demo Date and Time', format='%Y-%m-%dT%H:%M', validators=[DataRequired()])
    submit = SubmitField('Schedule Demo')

class FeedbackForm(FlaskForm):
    rating = SelectField('Rating', 
                        choices=[
                            ('1', '1 - Poor'),
                            ('2', '2 - Below Average'),
                            ('3', '3 - Average'),
                            ('4', '4 - Good'),
                            ('5', '5 - Excellent')
                        ],
                        coerce=int,
                        validators=[DataRequired()])
    student_interest = SelectField('Student Interest', 
                                 choices=[
                                     ('Interested', 'Interested'),
                                     ('Not Interested', 'Not Interested'),
                                     ('Maybe', 'Maybe')
                                 ],
                                 validators=[DataRequired()])
    comments = TextAreaField('Comments')
    submit = SubmitField('Submit Feedback')

class ReassignTeacherForm(FlaskForm):
    teacher_id = SelectField('Select New Teacher', coerce=int, validators=[DataRequired()])
    reason = TextAreaField('Reason for Reassignment', validators=[DataRequired(), Length(min=5, max=500)])
    submit = SubmitField('Reassign Teacher')

class CommunicationTemplateForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired(), Length(min=2, max=100)])
    subject = StringField('Email Subject', validators=[DataRequired(), Length(min=2, max=200)])
    content = TextAreaField('Template Content', validators=[DataRequired(), Length(min=10)])
    type = SelectField('Communication Type', 
                      choices=[
                          ('email', 'Email'),
                          ('sms', 'SMS'),
                          ('whatsapp', 'WhatsApp')
                      ],
                      validators=[DataRequired()])
    category = SelectField('Template Category', 
                         choices=[
                             ('lead_followup', 'Lead Follow-up'),
                             ('demo_confirmation', 'Demo Confirmation'),
                             ('demo_reminder', 'Demo Reminder'),
                             ('demo_feedback', 'Demo Feedback'),
                             ('payment_reminder', 'Payment Reminder'),
                             ('general', 'General Communication')
                         ],
                         validators=[DataRequired()])
    is_active = BooleanField('Active Template', default=True)
    submit = SubmitField('Save Template')

class SendCommunicationForm(FlaskForm):
    template_id = SelectField('Select Template', coerce=int, validators=[DataRequired()])
    recipient_type = SelectField('Send To', 
                               choices=[
                                   ('student', 'Student'),
                                   ('teacher', 'Teacher'),
                                   ('custom', 'Custom Recipient')
                               ],
                               validators=[DataRequired()])
    custom_recipient = StringField('Custom Recipient (Email/Phone)', validators=[Optional(), Length(max=100)])
    custom_recipient_name = StringField('Custom Recipient Name', validators=[Optional(), Length(max=100)])
    subject = StringField('Subject Override', validators=[Optional(), Length(max=200)])
    content = TextAreaField('Content Override', validators=[Optional()])
    student_id = SelectField('Select Student', coerce=int, validators=[Optional()])
    teacher_id = SelectField('Select Teacher', coerce=int, validators=[Optional()])
    submit = SubmitField('Send Communication')
