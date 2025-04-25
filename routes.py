from app import app, db
from flask import render_template, redirect, url_for, flash, request, jsonify
from forms import LoginForm, StudentLeadForm, TeacherForm, AssignTeacherForm, ScheduleDemoForm, FeedbackForm
from models import Admin, Student, Teacher, TuitionAssignment, Demo, Feedback
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from helpers import calculate_match_score, generate_dashboard_stats
from datetime import datetime
import json
import logging

# Add context processor to make datetime available in all templates
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

# Login route
@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(email=form.email.data).first()
        if admin and check_password_hash(admin.password_hash, form.password.data):
            login_user(admin, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

# Dashboard route
@app.route('/dashboard')
@login_required
def dashboard():
    stats = generate_dashboard_stats()
    return render_template('dashboard.html', title='Dashboard', stats=stats)

# Student Lead routes
@app.route('/student-leads')
@login_required
def student_leads():
    status_filter = request.args.get('status', '')
    if status_filter:
        leads = Student.query.filter_by(status=status_filter).order_by(Student.created_at.desc()).all()
    else:
        leads = Student.query.order_by(Student.created_at.desc()).all()
    return render_template('student_leads.html', title='Student Leads', leads=leads, current_filter=status_filter)

@app.route('/student-lead/new', methods=['GET', 'POST'])
@login_required
def new_student_lead():
    form = StudentLeadForm()
    if form.validate_on_submit():
        subjects_json = json.dumps(form.subjects.data)
        student = Student(
            name=form.name.data,
            phone=form.phone.data,
            class_level=form.class_level.data,
            subjects=subjects_json,
            fee=form.fee.data,
            area=form.area.data,
            gender_preference=form.gender_preference.data,
            lead_source=form.lead_source.data,
            referral_name=form.referral_name.data if form.lead_source.data == 'Referral' else None,
            preferred_timing=form.preferred_timing.data
        )
        db.session.add(student)
        db.session.commit()
        flash('Student lead added successfully!', 'success')
        return redirect(url_for('student_leads'))
    
    return render_template('student_form.html', title='New Student Lead', form=form)

@app.route('/student-lead/<int:lead_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_student_lead(lead_id):
    student = Student.query.get_or_404(lead_id)
    form = StudentLeadForm()
    
    if form.validate_on_submit():
        student.name = form.name.data
        student.phone = form.phone.data
        student.class_level = form.class_level.data
        student.subjects = json.dumps(form.subjects.data)
        student.fee = form.fee.data
        student.area = form.area.data
        student.gender_preference = form.gender_preference.data
        student.lead_source = form.lead_source.data
        student.referral_name = form.referral_name.data if form.lead_source.data == 'Referral' else None
        student.preferred_timing = form.preferred_timing.data
        
        db.session.commit()
        flash('Student lead updated successfully!', 'success')
        return redirect(url_for('student_leads'))
    
    elif request.method == 'GET':
        form.name.data = student.name
        form.phone.data = student.phone
        form.class_level.data = student.class_level
        form.subjects.data = json.loads(student.subjects)
        form.fee.data = student.fee
        form.area.data = student.area
        form.gender_preference.data = student.gender_preference
        form.lead_source.data = student.lead_source if student.lead_source else ''
        form.referral_name.data = student.referral_name if student.referral_name else ''
        form.preferred_timing.data = student.preferred_timing if student.preferred_timing else ''
    
    return render_template('student_form.html', title='Edit Student Lead', form=form)

@app.route('/student-lead/<int:lead_id>/delete', methods=['POST'])
@login_required
def delete_student_lead(lead_id):
    student = Student.query.get_or_404(lead_id)
    db.session.delete(student)
    db.session.commit()
    flash('Student lead deleted successfully!', 'success')
    return redirect(url_for('student_leads'))

# Teacher routes
@app.route('/teachers')
@login_required
def teachers():
    status_filter = request.args.get('status', '')
    if status_filter:
        teachers = Teacher.query.filter_by(status=status_filter).order_by(Teacher.created_at.desc()).all()
    else:
        teachers = Teacher.query.order_by(Teacher.created_at.desc()).all()
    return render_template('teachers.html', title='Teachers', teachers=teachers, current_filter=status_filter)

@app.route('/teacher/new', methods=['GET', 'POST'])
@login_required
def new_teacher():
    form = TeacherForm()
    if form.validate_on_submit():
        areas = [area.strip() for area in form.preferred_areas.data.splitlines() if area.strip()]
        preferred_areas_json = json.dumps(areas)
        preferred_subjects_json = json.dumps(form.preferred_subjects.data)
        
        teacher = Teacher(
            name=form.name.data,
            phone=form.phone.data,
            alternate_phone=form.alternate_phone.data,
            preferred_areas=preferred_areas_json,
            preferred_subjects=preferred_subjects_json,
            gender=form.gender.data,
            pincode=form.pincode.data,
            qualification=form.qualification.data,
            stream=form.stream.data,
            board=form.board.data,
            teaching_experience=form.teaching_experience.data,
            teaching_experience_details=form.teaching_experience_details.data
        )
        db.session.add(teacher)
        db.session.commit()
        flash('Teacher added successfully!', 'success')
        return redirect(url_for('teachers'))
    
    return render_template('teacher_form.html', title='New Teacher', form=form)

@app.route('/teacher/<int:teacher_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    form = TeacherForm()
    
    if form.validate_on_submit():
        areas = [area.strip() for area in form.preferred_areas.data.splitlines() if area.strip()]
        teacher.name = form.name.data
        teacher.phone = form.phone.data
        teacher.alternate_phone = form.alternate_phone.data
        teacher.preferred_areas = json.dumps(areas)
        teacher.preferred_subjects = json.dumps(form.preferred_subjects.data)
        teacher.gender = form.gender.data
        teacher.pincode = form.pincode.data
        teacher.qualification = form.qualification.data
        teacher.stream = form.stream.data
        teacher.board = form.board.data
        teacher.teaching_experience = form.teaching_experience.data
        teacher.teaching_experience_details = form.teaching_experience_details.data
        
        db.session.commit()
        flash('Teacher updated successfully!', 'success')
        return redirect(url_for('teachers'))
    
    elif request.method == 'GET':
        form.name.data = teacher.name
        form.phone.data = teacher.phone
        form.alternate_phone.data = teacher.alternate_phone
        form.preferred_areas.data = '\n'.join(json.loads(teacher.preferred_areas))
        form.preferred_subjects.data = json.loads(teacher.preferred_subjects)
        form.gender.data = teacher.gender
        form.pincode.data = teacher.pincode
        form.qualification.data = teacher.qualification
        form.stream.data = teacher.stream
        form.board.data = teacher.board
        form.teaching_experience.data = teacher.teaching_experience
        form.teaching_experience_details.data = teacher.teaching_experience_details
    
    return render_template('teacher_form.html', title='Edit Teacher', form=form)

@app.route('/teacher/<int:teacher_id>/delete', methods=['POST'])
@login_required
def delete_teacher(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    db.session.delete(teacher)
    db.session.commit()
    flash('Teacher deleted successfully!', 'success')
    return redirect(url_for('teachers'))

@app.route('/teacher/<int:teacher_id>/toggle-status', methods=['POST'])
@login_required
def toggle_teacher_status(teacher_id):
    teacher = Teacher.query.get_or_404(teacher_id)
    teacher.status = 'Inactive' if teacher.status == 'Active' else 'Active'
    db.session.commit()
    flash(f'Teacher status updated to {teacher.status}!', 'success')
    return redirect(url_for('teachers'))

# Assignment routes
@app.route('/assignments')
@login_required
def assignments():
    status_filter = request.args.get('status', '')
    if status_filter:
        assignments = TuitionAssignment.query.filter_by(status=status_filter).order_by(TuitionAssignment.assigned_date.desc()).all()
    else:
        assignments = TuitionAssignment.query.order_by(TuitionAssignment.assigned_date.desc()).all()
    return render_template('assignments.html', title='Tuition Assignments', assignments=assignments, current_filter=status_filter)

@app.route('/student-lead/<int:lead_id>/assign', methods=['GET', 'POST'])
@login_required
def assign_teacher(lead_id):
    student = Student.query.get_or_404(lead_id)
    
    # Check if student already has an assignment
    existing_assignment = TuitionAssignment.query.filter_by(student_id=student.id, status='Pending').first()
    if existing_assignment:
        flash('This student already has a pending assignment!', 'warning')
        return redirect(url_for('student_leads'))
    
    form = AssignTeacherForm()
    
    # Get suitable teachers based on matching criteria
    suitable_teachers = []
    all_teachers = Teacher.query.filter_by(status='Active').all()
    
    for teacher in all_teachers:
        match_score = calculate_match_score(student, teacher)
        if match_score > 0:
            suitable_teachers.append({
                'teacher': teacher,
                'match_score': match_score
            })
    
    # Sort by match score (highest first)
    suitable_teachers.sort(key=lambda x: x['match_score'], reverse=True)
    
    # Update form choices
    form.teacher_id.choices = [(t['teacher'].id, f"{t['teacher'].name} - {t['teacher'].teacher_id} (Match: {t['match_score']}%)") 
                              for t in suitable_teachers]
    
    if form.validate_on_submit():
        teacher = Teacher.query.get(form.teacher_id.data)
        
        # Create assignment
        assignment = TuitionAssignment(
            student_id=student.id,
            teacher_id=teacher.id,
            status='Pending'
        )
        db.session.add(assignment)
        
        # Update student status
        student.status = 'Assigned'
        
        db.session.commit()
        flash('Teacher assigned successfully!', 'success')
        return redirect(url_for('assignments'))
    
    return render_template('assign_teacher.html', title='Assign Teacher', form=form, 
                          student=student, suitable_teachers=suitable_teachers)

@app.route('/assignment/<int:assignment_id>/schedule-demo', methods=['GET', 'POST'])
@login_required
def schedule_demo(assignment_id):
    assignment = TuitionAssignment.query.get_or_404(assignment_id)
    form = ScheduleDemoForm()
    
    if form.validate_on_submit():
        demo = Demo(
            assignment_id=assignment.id,
            scheduled_date=form.scheduled_date.data,
            status='Scheduled'
        )
        db.session.add(demo)
        
        # Update assignment status
        assignment.status = 'Demo Scheduled'
        
        db.session.commit()
        flash('Demo scheduled successfully!', 'success')
        return redirect(url_for('demo_tracking'))
    
    return render_template('schedule_demo.html', title='Schedule Demo', form=form, assignment=assignment)

# Demo Tracking routes
@app.route('/demo-tracking')
@login_required
def demo_tracking():
    status_filter = request.args.get('status', '')
    if status_filter:
        demos = Demo.query.filter_by(status=status_filter).order_by(Demo.scheduled_date).all()
    else:
        demos = Demo.query.order_by(Demo.scheduled_date).all()
    return render_template('demo_tracking.html', title='Demo Tracking', demos=demos, current_filter=status_filter)

@app.route('/demo/<int:demo_id>/send-reminder', methods=['GET', 'POST'])
@login_required
def send_reminder(demo_id):
    demo = Demo.query.get_or_404(demo_id)
    
    if request.method == 'POST':
        notes = request.form.get('reminder_notes', '')
        
        # Get details for the email record
        student_name = demo.assignment.student.name
        teacher_name = demo.assignment.teacher.name
        scheduled_date = demo.scheduled_date.strftime("%Y-%m-%d %H:%M")
        
        # Create a record of the email (without actually sending it)
        # This allows the system to work without requiring an API key
        log_message = f"Email reminder noted for {student_name} and {teacher_name} for demo on {scheduled_date}."
        if notes:
            log_message += f" Notes: {notes}"
        
        # Update the demo with reminder information
        demo.reminder_sent = True
        demo.reminder_sent_at = datetime.utcnow()
        demo.reminder_notes = notes
        
        # Add to database
        db.session.commit()
        
        flash('Reminder recorded and notification details saved!', 'success')
        logging.info(log_message)
        return redirect(url_for('demo_tracking'))
    
    # GET request - show the reminder form
    return render_template('send_reminder.html', title='Send Demo Reminder', demo=demo)

@app.route('/demo/<int:demo_id>/mark-completed', methods=['POST'])
@login_required
def mark_demo_completed(demo_id):
    demo = Demo.query.get_or_404(demo_id)
    demo.status = 'Completed'
    db.session.commit()
    flash('Demo marked as completed!', 'success')
    return redirect(url_for('demo_tracking'))

@app.route('/demo/<int:demo_id>/mark-cancelled', methods=['POST'])
@login_required
def mark_demo_cancelled(demo_id):
    demo = Demo.query.get_or_404(demo_id)
    demo.status = 'Cancelled'
    
    # Update assignment status
    assignment = demo.assignment
    assignment.status = 'Cancelled'
    
    db.session.commit()
    flash('Demo marked as cancelled!', 'success')
    return redirect(url_for('demo_tracking'))

# Feedback routes
@app.route('/demo/<int:demo_id>/feedback', methods=['GET', 'POST'])
@login_required
def provide_feedback(demo_id):
    demo = Demo.query.get_or_404(demo_id)
    
    # Check if feedback already exists
    existing_feedback = Feedback.query.filter_by(demo_id=demo.id).first()
    if existing_feedback:
        flash('Feedback already provided for this demo!', 'warning')
        return redirect(url_for('demo_tracking'))
    
    form = FeedbackForm()
    
    if form.validate_on_submit():
        feedback = Feedback(
            demo_id=demo.id,
            rating=form.rating.data,
            comments=form.comments.data,
            student_interest=form.student_interest.data
        )
        db.session.add(feedback)
        
        # Update assignment status based on student interest
        assignment = demo.assignment
        if form.student_interest.data == 'Interested':
            assignment.status = 'Converted'
            assignment.student.status = 'Converted'
        elif form.student_interest.data == 'Not Interested':
            assignment.status = 'Cancelled'
            assignment.student.status = 'Lost'
        
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('demo_tracking'))
    
    return render_template('feedback_form.html', title='Provide Feedback', form=form, demo=demo)

# API routes for dashboard data
@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    stats = generate_dashboard_stats()
    return jsonify(stats)
