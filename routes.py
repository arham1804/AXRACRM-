from app import app, db
from flask import render_template, redirect, url_for, flash, request, jsonify
from forms import (LoginForm, StudentLeadForm, TeacherForm, AssignTeacherForm, 
                   ScheduleDemoForm, FeedbackForm, ReassignTeacherForm, 
                   CommunicationTemplateForm, SendCommunicationForm)
from models import (Admin, Student, Teacher, TuitionAssignment, 
                   Demo, Feedback, Notification, CommunicationTemplate, Communication)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from helpers import calculate_match_score, generate_dashboard_stats
from datetime import datetime, timedelta
from email_service import send_demo_reminder, send_teacher_demo_notification
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
        
        # Create notification for new lead
        Notification.create_notification(
            title="New Student Lead Added",
            message=f"New student lead '{student.name}' has been added. Please assign a teacher soon.",
            notification_type="new_lead",
            related_id=student.id
        )
        
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
        
        # Create notification for teacher assignment
        Notification.create_notification(
            title=f"Teacher Assigned to {student.name}",
            message=f"Teacher {teacher.name} has been assigned to student {student.name}. Please schedule a demo soon.",
            notification_type="assignment",
            related_id=assignment.id
        )
        
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
        
        # Create notification for demo scheduling
        student_name = assignment.student.name
        teacher_name = assignment.teacher.name
        scheduled_time = form.scheduled_date.data.strftime("%Y-%m-%d %H:%M")
        
        Notification.create_notification(
            title=f"Demo Scheduled: {student_name} with {teacher_name}",
            message=f"A demo has been scheduled for student {student_name} with teacher {teacher_name} on {scheduled_time}.",
            notification_type="demo_scheduled",
            related_id=demo.id
        )
        
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
    
    # Get student and teacher info for notification
    student_name = demo.assignment.student.name
    teacher_name = demo.assignment.teacher.name
    
    # Create notification
    Notification.create_notification(
        title=f"Demo Completed: {student_name}",
        message=f"The demo for {student_name} with {teacher_name} has been marked as completed. Please provide feedback.",
        notification_type="demo_completed",
        related_id=demo.id
    )
    
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
    
    # Get student and teacher info for notification
    student_name = demo.assignment.student.name
    teacher_name = demo.assignment.teacher.name
    
    # Create notification with urgent flag
    Notification.create_notification(
        title=f"Demo Cancelled: {student_name}",
        message=f"The demo for {student_name} with {teacher_name} has been cancelled. Please check the details and consider reassigning.",
        notification_type="demo_cancelled",
        related_id=demo.id,
        is_urgent=True
    )
    
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
        # Ensure we have a valid student_id
        if assignment.student_id is None:
            # Fix the assignment to use the proper student_id from the relationship
            student = demo.assignment.student
            if student:
                assignment.student_id = student.id
            else:
                # If no student is found, we can't proceed
                flash('Error: No student found for this assignment!', 'danger')
                return redirect(url_for('demo_tracking'))
        
        if form.student_interest.data == 'Interested':
            assignment.status = 'Converted'
            assignment.student.status = 'Converted'
        elif form.student_interest.data == 'Not Interested':
            assignment.status = 'Cancelled'
            assignment.student.status = 'Lost'
        
        # Create notification for feedback, make it urgent if feedback is negative
        student_name = demo.assignment.student.name
        teacher_name = demo.assignment.teacher.name
        is_negative = form.rating.data < 3
        
        notification_title = f"Demo Feedback: {student_name} - {'Poor' if is_negative else 'Good'}"
        notification_message = (
            f"Feedback has been provided for the demo of {student_name} with {teacher_name}. "
            f"Rating: {form.rating.data}/5, Interest: {form.student_interest.data}"
        )
        
        if form.comments.data:
            notification_message += f"\nComments: {form.comments.data}"
        
        Notification.create_notification(
            title=notification_title,
            message=notification_message,
            notification_type="demo_feedback",
            related_id=demo.id,
            is_urgent=is_negative
        )
        
        # If feedback is negative (rating < 3), suggest reassignment
        if is_negative and form.student_interest.data != 'Not Interested':
            Notification.create_notification(
                title=f"Reassignment Suggested: {student_name}",
                message=f"The feedback for {student_name}'s demo with {teacher_name} was poor (Rating: {form.rating.data}/5). Consider reassigning to another teacher.",
                notification_type="reassignment_suggested",
                related_id=demo.id,
                is_urgent=True
            )
        
        db.session.commit()
        flash('Feedback submitted successfully!', 'success')
        return redirect(url_for('demo_tracking'))
    
    return render_template('feedback_form.html', title='Provide Feedback', form=form, demo=demo)

# Notification routes
@app.route('/notifications')
@login_required
def notifications():
    all_notifications = Notification.query.order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', title='Notifications', notifications=all_notifications)

@app.route('/notifications/mark-read/<int:notification_id>', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    result = Notification.mark_as_read(notification_id)
    if result:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Notification not found'}), 404

@app.route('/notifications/delete/<int:notification_id>', methods=['POST'])
@login_required
def delete_notification(notification_id):
    result = Notification.delete_notification(notification_id)
    if result:
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Notification not found'}), 404

@app.route('/api/notifications/unread')
@login_required
def api_unread_notifications():
    try:
        # Run background checks for new notifications
        Notification.check_unassigned_leads()
        Notification.check_upcoming_demos()
        
        unread = Notification.get_unread_notifications()
        
        # Handle case where unread might be None
        if unread is None:
            return jsonify({
                'count': 0,
                'notifications': []
            })
        
        notifications_data = []
        for n in unread:
            try:
                # Format datetime safely
                created_at = n.created_at.strftime('%Y-%m-%d %H:%M') if n.created_at else ''
                
                notifications_data.append({
                    'id': n.id,
                    'title': n.title or '',
                    'message': n.message or '',
                    'type': n.notification_type or '',
                    'is_urgent': bool(n.is_urgent),
                    'created_at': created_at
                })
            except Exception as e:
                # Log the error but continue processing other notifications
                app.logger.error(f"Error processing notification {n.id}: {str(e)}")
                continue
        
        return jsonify({
            'count': len(notifications_data),
            'notifications': notifications_data
        })
    except Exception as e:
        # Log the error and return an empty response
        app.logger.error(f"Error in notifications API: {str(e)}")
        return jsonify({
            'count': 0,
            'notifications': [],
            'error': 'An error occurred while fetching notifications'
        }), 500

# Demo reassignment route for failed demos or unattended demos
@app.route('/demo/<int:demo_id>/reassign', methods=['GET', 'POST'])
@login_required
def reassign_teacher_for_demo(demo_id):
    demo = Demo.query.get_or_404(demo_id)
    
    # Allow reassignment for completed demos with poor feedback or demos that are scheduled but past due
    if demo.status == 'Completed' and demo.feedback:
        # For completed demos, check feedback rating
        if demo.feedback.rating >= 4:
            flash('This demo has positive feedback and does not need reassignment.', 'info')
            return redirect(url_for('demo_tracking'))
    elif demo.status == 'Scheduled':
        # For scheduled demos, check if they're past due (scheduled date is in the past)
        if demo.scheduled_date > datetime.utcnow():
            flash('This demo is still scheduled for the future and not eligible for reassignment yet.', 'warning')
            return redirect(url_for('demo_tracking'))
    else:
        flash('This demo is not eligible for teacher reassignment.', 'warning')
        return redirect(url_for('demo_tracking'))
    
    student = demo.assignment.student
    form = ReassignTeacherForm()
    
    # Get suitable teachers based on matching criteria
    suitable_teachers = []
    all_teachers = Teacher.query.filter_by(status='Active').all()
    
    # Filter out the current teacher
    all_teachers = [t for t in all_teachers if t.id != demo.assignment.teacher_id]
    
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
        new_teacher = Teacher.query.get(form.teacher_id.data)
        
        # Validate student is not None and has a valid ID before creating the assignment
        if student is None or student.id is None:
            flash('Error: Cannot reassign teacher because student information is missing.', 'danger')
            return redirect(url_for('demo_tracking'))
        
        # Create new assignment
        new_assignment = TuitionAssignment(
            student_id=student.id,
            teacher_id=new_teacher.id,
            status='Pending'
        )
        db.session.add(new_assignment)
        
        # Update old assignment status
        old_assignment = demo.assignment
        # Ensure old_assignment has a valid student_id
        if old_assignment.student_id is None and old_assignment.student is not None:
            old_assignment.student_id = old_assignment.student.id
        
        old_assignment.status = 'Cancelled'
        
        # Create notification for both new teacher and old teacher
        Notification.create_notification(
            title=f"Teacher Reassigned: {student.name}",
            message=f"Student {student.name} has been reassigned from {old_assignment.teacher.name} to {new_teacher.name}. Reason: {form.reason.data}",
            notification_type='teacher_reassigned',
            related_id=new_assignment.id,
            is_urgent=True
        )
        
        db.session.commit()
        flash('Teacher reassigned successfully!', 'success')
        return redirect(url_for('assignments'))
    
    return render_template('reassign_teacher.html', title='Reassign Teacher', form=form, demo=demo)

# API routes for dashboard data
@app.route('/api/dashboard/stats')
@login_required
def api_dashboard_stats():
    try:
        stats = generate_dashboard_stats()
        # Ensure all the data is JSON serializable
        for key, value in stats.items():
            if isinstance(value, dict):
                # Ensure all dictionary values are JSON serializable
                for inner_key, inner_value in value.items():
                    if not isinstance(inner_value, (str, int, float, bool, type(None))):
                        stats[key][inner_key] = str(inner_value)
            elif isinstance(value, list):
                # Ensure all list elements are JSON serializable
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        for item_key, item_value in item.items():
                            if not isinstance(item_value, (str, int, float, bool, type(None))):
                                stats[key][i][item_key] = str(item_value)
                    elif not isinstance(item, (str, int, float, bool, type(None))):
                        stats[key][i] = str(item)
            elif not isinstance(value, (str, int, float, bool, type(None))):
                stats[key] = str(value)
        
        return jsonify(stats)
    except Exception as e:
        # Log the error and return a valid JSON response with error information
        error_msg = f"Error in dashboard stats API: {str(e)}"
        print(error_msg)
        return jsonify({
            'error': error_msg,
            'status': 'error',
            'lead_status': {'new': 0, 'assigned': 0, 'converted': 0, 'lost': 0},
            'assignment_status': {'pending': 0, 'demo_scheduled': 0, 'converted': 0, 'cancelled': 0},
            'demo_status': {'scheduled': 0, 'completed': 0, 'cancelled': 0},
            'trend_months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'trend_leads': [0, 0, 0, 0, 0, 0],
            'trend_conversions': [0, 0, 0, 0, 0, 0]
        })

# Communication Templates routes
@app.route('/communication-templates')
@login_required
def communication_templates():
    templates = CommunicationTemplate.query.order_by(CommunicationTemplate.created_at.desc()).all()
    return render_template('communication_templates.html', title='Communication Templates', templates=templates)

@app.route('/communication-template/new', methods=['GET', 'POST'])
@login_required
def new_communication_template():
    form = CommunicationTemplateForm()
    if form.validate_on_submit():
        template = CommunicationTemplate(
            name=form.name.data,
            subject=form.subject.data,
            content=form.content.data,
            type=form.type.data,
            category=form.category.data,
            is_active=form.is_active.data
        )
        db.session.add(template)
        db.session.commit()
        flash('Communication template created successfully!', 'success')
        return redirect(url_for('communication_templates'))
    
    return render_template('communication_template_form.html', title='New Communication Template', form=form)

@app.route('/communication-template/<int:template_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_communication_template(template_id):
    template = CommunicationTemplate.query.get_or_404(template_id)
    form = CommunicationTemplateForm()
    
    if form.validate_on_submit():
        template.name = form.name.data
        template.subject = form.subject.data
        template.content = form.content.data
        template.type = form.type.data
        template.category = form.category.data
        template.is_active = form.is_active.data
        
        db.session.commit()
        flash('Communication template updated successfully!', 'success')
        return redirect(url_for('communication_templates'))
    
    elif request.method == 'GET':
        form.name.data = template.name
        form.subject.data = template.subject
        form.content.data = template.content
        form.type.data = template.type
        form.category.data = template.category
        form.is_active.data = template.is_active
    
    return render_template('communication_template_form.html', title='Edit Communication Template', form=form, template=template)

@app.route('/communication-template/<int:template_id>/delete', methods=['POST'])
@login_required
def delete_communication_template(template_id):
    template = CommunicationTemplate.query.get_or_404(template_id)
    db.session.delete(template)
    db.session.commit()
    flash('Communication template deleted successfully!', 'success')
    return redirect(url_for('communication_templates'))

@app.route('/communication-template/<int:template_id>/toggle-status', methods=['POST'])
@login_required
def toggle_template_status(template_id):
    template = CommunicationTemplate.query.get_or_404(template_id)
    template.is_active = not template.is_active
    db.session.commit()
    flash(f'Template is now {"active" if template.is_active else "inactive"}!', 'success')
    return redirect(url_for('communication_templates'))

# Quick Communication feature
@app.route('/communications')
@login_required
def communications():
    communications = Communication.query.order_by(Communication.created_at.desc()).all()
    return render_template('communications.html', title='Communications', communications=communications)

@app.route('/send-communication', methods=['GET', 'POST'])
@login_required
def send_communication():
    form = SendCommunicationForm()
    
    # Load active templates for the dropdown
    active_templates = CommunicationTemplate.query.filter_by(is_active=True).all()
    form.template_id.choices = [(t.id, f"{t.name} ({t.type})") for t in active_templates]
    
    # Load students for dropdown
    students = Student.query.all()
    form.student_id.choices = [(0, 'Select Student')] + [(s.id, f"{s.name} - {s.lead_id}") for s in students]
    
    # Load teachers for dropdown
    teachers = Teacher.query.filter_by(status='Active').all()
    form.teacher_id.choices = [(0, 'Select Teacher')] + [(t.id, f"{t.name} - {t.teacher_id}") for t in teachers]
    
    if form.validate_on_submit():
        recipient = ""
        recipient_name = ""
        selected_student = None
        selected_teacher = None
        
        # Determine recipient based on selection
        if form.recipient_type.data == 'student' and form.student_id.data != 0:
            selected_student = Student.query.get(form.student_id.data)
            recipient = selected_student.phone
            recipient_name = selected_student.name
        elif form.recipient_type.data == 'teacher' and form.teacher_id.data != 0:
            selected_teacher = Teacher.query.get(form.teacher_id.data)
            recipient = selected_teacher.phone
            recipient_name = selected_teacher.name
        elif form.recipient_type.data == 'custom':
            recipient = form.custom_recipient.data
            recipient_name = form.custom_recipient_name.data
        
        # Get the selected template
        template = CommunicationTemplate.query.get(form.template_id.data)
        
        # Use template content or override if provided
        subject = form.subject.data or template.subject
        content = form.content.data or template.content
        
        # If using template with placeholders, render it
        if not form.content.data and (selected_student or selected_teacher):
            context = {}
            if selected_student:
                context.update({
                    'student_name': selected_student.name,
                    'student_phone': selected_student.phone,
                    'student_area': selected_student.area,
                    'student_subjects': ', '.join(selected_student.get_subjects_list()),
                    'student_fee': selected_student.fee
                })
            if selected_teacher:
                context.update({
                    'teacher_name': selected_teacher.name,
                    'teacher_phone': selected_teacher.phone,
                    'teacher_areas': ', '.join(selected_teacher.get_preferred_areas_list()),
                    'teacher_subjects': ', '.join(selected_teacher.get_preferred_subjects_list()),
                    'teacher_qualification': selected_teacher.qualification
                })
            
            # Add datetime for scheduled demos
            context['current_date'] = datetime.now().strftime('%d-%m-%Y')
            context['current_time'] = datetime.now().strftime('%H:%M')
            
            # Render the template with context
            subject, content = template.render_template(**context)
        
        # Create the communication record
        communication = Communication(
            template_id=template.id,
            subject=subject,
            content=content,
            type=template.type,
            recipient=recipient,
            recipient_name=recipient_name,
            student_id=selected_student.id if selected_student else None,
            teacher_id=selected_teacher.id if selected_teacher else None
        )
        
        db.session.add(communication)
        db.session.commit()
        
        # TODO: Implement actual sending of communication
        # For now, just mark it as sent
        communication.status = "Sent"
        communication.sent_at = datetime.utcnow()
        db.session.commit()
        
        flash('Communication sent successfully!', 'success')
        return redirect(url_for('communications'))
    
    return render_template('send_communication.html', title='Send Communication', form=form)

@app.route('/quick-communication/<string:type>/<int:id>', methods=['GET'])
@login_required
def quick_communication(type, id):
    """One-click communication templates for quick lead follow-ups"""
    if type == 'student':
        # Get student and available templates
        student = Student.query.get_or_404(id)
        templates = CommunicationTemplate.query.filter_by(
            is_active=True, 
            type='sms'  # For quick communication, we'll use SMS templates
        ).filter(
            CommunicationTemplate.category.in_(['lead_followup', 'general'])
        ).all()
        
        return render_template(
            'quick_communication.html', 
            title='Quick Communication', 
            recipient=student,
            recipient_type='student',
            templates=templates
        )
    
    elif type == 'teacher':
        # Get teacher and available templates
        teacher = Teacher.query.get_or_404(id)
        templates = CommunicationTemplate.query.filter_by(
            is_active=True, 
            type='sms'  # For quick communication, we'll use SMS templates
        ).filter(
            CommunicationTemplate.category.in_(['general'])
        ).all()
        
        return render_template(
            'quick_communication.html', 
            title='Quick Communication', 
            recipient=teacher,
            recipient_type='teacher',
            templates=templates
        )
    
    else:
        flash('Invalid recipient type for quick communication!', 'danger')
        return redirect(url_for('dashboard'))

@app.route('/quick-communication/send', methods=['POST'])
@login_required
def send_quick_communication():
    """Handle the quick communication form submission"""
    template_id = request.form.get('template_id')
    recipient_type = request.form.get('recipient_type')
    recipient_id = request.form.get('recipient_id')
    
    if not template_id or not recipient_type or not recipient_id:
        flash('Missing required information to send communication!', 'danger')
        return redirect(url_for('dashboard'))
    
    template = CommunicationTemplate.query.get_or_404(template_id)
    
    selected_student = None
    selected_teacher = None
    recipient = ""
    recipient_name = ""
    
    if recipient_type == 'student':
        selected_student = Student.query.get_or_404(recipient_id)
        recipient = selected_student.phone
        recipient_name = selected_student.name
    elif recipient_type == 'teacher':
        selected_teacher = Teacher.query.get_or_404(recipient_id)
        recipient = selected_teacher.phone
        recipient_name = selected_teacher.name
    
    # Prepare context for template rendering
    context = {
        'current_date': datetime.now().strftime('%d-%m-%Y'),
        'current_time': datetime.now().strftime('%H:%M')
    }
    
    if selected_student:
        context.update({
            'student_name': selected_student.name,
            'student_phone': selected_student.phone,
            'student_area': selected_student.area,
            'student_subjects': ', '.join(selected_student.get_subjects_list()),
            'student_fee': selected_student.fee
        })
    
    if selected_teacher:
        context.update({
            'teacher_name': selected_teacher.name,
            'teacher_phone': selected_teacher.phone,
            'teacher_areas': ', '.join(selected_teacher.get_preferred_areas_list()),
            'teacher_subjects': ', '.join(selected_teacher.get_preferred_subjects_list()),
            'teacher_qualification': selected_teacher.qualification
        })
    
    # Render the template
    subject, content = template.render_template(**context)
    
    # Create communication record
    communication = Communication(
        template_id=template.id,
        subject=subject,
        content=content,
        type=template.type,
        recipient=recipient,
        recipient_name=recipient_name,
        student_id=selected_student.id if selected_student else None,
        teacher_id=selected_teacher.id if selected_teacher else None
    )
    
    db.session.add(communication)
    db.session.commit()
    
    # TODO: Implement actual sending of communication
    # For now, just mark it as sent
    communication.status = "Sent"
    communication.sent_at = datetime.utcnow()
    db.session.commit()
    
    flash('Quick communication sent successfully!', 'success')
    
    # Redirect back to appropriate page
    if recipient_type == 'student':
        return redirect(url_for('student_leads'))
    elif recipient_type == 'teacher':
        return redirect(url_for('teachers'))
    else:
        return redirect(url_for('communications'))
