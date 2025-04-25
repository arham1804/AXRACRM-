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

class ChangeTeacherForm(FlaskForm):
    teacher_id = SelectField('Select New Teacher', coerce=int, validators=[DataRequired()])
    reason = SelectField('Reason for Change', 
                       choices=[
                           ('Unavailability', 'Teacher Unavailable'),
                           ('Better Match', 'Better Subject Match'),
                           ('Student Request', 'Student Requested Change'),
                           ('Area Issue', 'Location/Area Conflict'),
                           ('Other', 'Other Reason')
                       ],
                       validators=[DataRequired()])
    comments = TextAreaField('Additional Comments')
    submit = SubmitField('Change Teacher')
