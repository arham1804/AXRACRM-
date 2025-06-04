from models import Student, Teacher, TuitionAssignment, Demo, Feedback
from sqlalchemy import func, and_
from app import db
import json
from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any

def calculate_match_score(student: Student, teacher: Teacher) -> int:
    """
    Calculate a match score between a student lead and a teacher
    Returns a percentage (0-100) indicating how good the match is
    """
    score = 0
    max_score = 100
    
    # Check gender preference
    if student.gender_preference == 'ANY' or student.gender_preference == teacher.gender:
        score += 20
    else:
        # If gender preference doesn't match, return 0 immediately
        return 0
    
    # Check if teacher's preferred areas include student's area
    teacher_areas = json.loads(teacher.preferred_areas)
    if student.area.lower() in [area.lower() for area in teacher_areas]:
        score += 30
    else:
        # If area doesn't match at all, return a low score
        score += 5
    
    # Check subject match
    student_subjects = json.loads(student.subjects)
    teacher_subjects = json.loads(teacher.preferred_subjects)
    
    # Count how many of the student's subjects the teacher can teach
    matching_subjects = set(student_subjects).intersection(set(teacher_subjects))
    if matching_subjects:
        # Add score based on the percentage of subjects that match
        subject_match_percentage = len(matching_subjects) / len(student_subjects)
        score += int(30 * subject_match_percentage)
    else:
        # If no subjects match, return a low score
        return 10
    
    # Check for class/education level match
    class_match_score = 0
    if teacher.qualification in ["B.Tech", "B.E.", "M.Tech", "M.E.", "PhD"] and student.class_level in ["Secondary", "Sr. Secondary"]:
        class_match_score = 20
    elif teacher.qualification in ["B.Sc", "M.Sc"] and student.class_level in ["Middle", "Secondary", "Sr. Secondary"]:
        class_match_score = 20
    elif teacher.qualification in ["B.A", "M.A", "B.Com", "M.Com"] and student.class_level in ["Primary", "Middle"]:
        class_match_score = 20
    else:
        class_match_score = 10
    
    score += class_match_score
    
    return score

def generate_dashboard_stats() -> Dict[str, Any]:
    """
    Generate statistics for the admin dashboard
    """
    stats = {}
    
    try:
        # Total counts
        stats['total_leads'] = Student.query.count()
        stats['total_teachers'] = Teacher.query.count()
        stats['total_assignments'] = TuitionAssignment.query.count()
        stats['total_demos'] = Demo.query.count()
        
        # Status breakdowns - ensure all values are integers, not SQLAlchemy result objects
        stats['lead_status'] = {
            'new': int(Student.query.filter_by(status='New').count()),
            'assigned': int(Student.query.filter_by(status='Assigned').count()),
            'converted': int(Student.query.filter_by(status='Converted').count()),
            'lost': int(Student.query.filter_by(status='Lost').count())
        }
        
        stats['assignment_status'] = {
            'pending': int(TuitionAssignment.query.filter_by(status='Pending').count()),
            'demo_scheduled': int(TuitionAssignment.query.filter_by(status='Demo Scheduled').count()),
            'converted': int(TuitionAssignment.query.filter_by(status='Converted').count()),
            'cancelled': int(TuitionAssignment.query.filter_by(status='Cancelled').count())
        }
        
        stats['demo_status'] = {
            'scheduled': int(Demo.query.filter_by(status='Scheduled').count()),
            'completed': int(Demo.query.filter_by(status='Completed').count()),
            'cancelled': int(Demo.query.filter_by(status='Cancelled').count())
        }
    except Exception as e:
        # If there's an error, log it and return empty stats
        logging.error(f"Error generating dashboard stats: {str(e)}")
        stats['lead_status'] = {'new': 0, 'assigned': 0, 'converted': 0, 'lost': 0}
        stats['assignment_status'] = {'pending': 0, 'demo_scheduled': 0, 'converted': 0, 'cancelled': 0}
        stats['demo_status'] = {'scheduled': 0, 'completed': 0, 'cancelled': 0}
    
    # Conversion rates
    if stats['total_leads'] > 0:
        stats['lead_to_demo_rate'] = round((stats['total_demos'] / stats['total_leads']) * 100, 2)
    else:
        stats['lead_to_demo_rate'] = 0
    
    if stats['total_demos'] > 0:
        converted_count = TuitionAssignment.query.filter_by(status='Converted').count()
        stats['demo_to_conversion_rate'] = round((converted_count / stats['total_demos']) * 100, 2)
    else:
        stats['demo_to_conversion_rate'] = 0
    
    # Calculate monthly lead trends (last 6 months)
    try:
        from calendar import monthrange
        months = []
        lead_counts = []
        conversion_counts = []
        now = datetime.utcnow()
        
        for i in range(5, -1, -1):
            year = (now.year if now.month - i > 0 else now.year - 1)
            month = (now.month - i) % 12 or 12
            start_date = datetime(year, month, 1)
            last_day = monthrange(year, month)[1]
            end_date = datetime(year, month, last_day, 23, 59, 59)
            
            month_name = start_date.strftime('%b')
            months.append(month_name)
            
            # Count leads created in this month
            month_leads = Student.query.filter(
                and_(
                    Student.created_at >= start_date,
                    Student.created_at <= end_date
                )
            ).count()
            lead_counts.append(int(month_leads))
            
            # Count conversions in this month
            month_conversions = TuitionAssignment.query.filter(
                and_(
                    TuitionAssignment.status == 'Converted',
                    TuitionAssignment.assigned_date >= start_date,
                    TuitionAssignment.assigned_date <= end_date
                )
            ).count()
            conversion_counts.append(int(month_conversions))
        
        stats['trend_months'] = months
        stats['trend_leads'] = lead_counts
        stats['trend_conversions'] = conversion_counts
    except Exception as e:
        logging.error(f"Error generating trend data: {str(e)}")
        # Provide fallback trend data
        stats['trend_months'] = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        stats['trend_leads'] = [0, 0, 0, 0, 0, 0]
        stats['trend_conversions'] = [0, 0, 0, 0, 0, 0]
    
    # Top performing teachers (based on conversion rate)
    from sqlalchemy.sql import case
    
    top_teachers = db.session.query(
        Teacher.id,
        Teacher.name,
        Teacher.teacher_id,
        func.count(TuitionAssignment.id).label('total_assignments'),
        func.sum(case((TuitionAssignment.status == 'Converted', 1), else_=0)).label('conversions')
    ).join(TuitionAssignment).group_by(Teacher.id).order_by(
        func.sum(case((TuitionAssignment.status == 'Converted', 1), else_=0)).desc()
    ).limit(5).all()
    
    stats['top_teachers'] = [{
        'name': teacher.name,
        'teacher_id': teacher.teacher_id,
        'total_assignments': teacher.total_assignments,
        'conversions': teacher.conversions,
        'conversion_rate': round((teacher.conversions / teacher.total_assignments * 100), 2) if teacher.total_assignments > 0 else 0
    } for teacher in top_teachers]
    
    # Recent activity
    recent_demos = Demo.query.order_by(Demo.created_at.desc()).limit(5).all()
    stats['recent_demos'] = [{
        'id': demo.id,
        'student_name': demo.assignment.student.name,
        'teacher_name': demo.assignment.teacher.name,
        'scheduled_date': demo.scheduled_date.strftime('%Y-%m-%d %H:%M'),
        'status': demo.status
    } for demo in recent_demos]
    
    recent_leads = Student.query.order_by(Student.created_at.desc()).limit(5).all()
    stats['recent_leads'] = [{
        'id': lead.id,
        'name': lead.name,
        'area': lead.area,
        'class_level': lead.class_level,
        'created_at': lead.created_at.strftime('%Y-%m-%d'),
        'status': lead.status
    } for lead in recent_leads]

    # New stats for Axra Funnel and Service Overview

    # Call to lead rate - no call data available, set to 0
    stats['call_to_lead_rate'] = 0

    # Conversion to payment rate - total payments / conversions
    total_conversions = TuitionAssignment.query.filter_by(status='Converted').count()
    total_payments = db.session.query(func.sum(Student.fee)).filter(Student.status == 'Converted').scalar() or 0.0
    if total_conversions > 0:
        stats['conversion_to_payment_rate'] = round((total_payments / total_conversions), 2)
    else:
        stats['conversion_to_payment_rate'] = 0.0

    # Sales overview and total sale (sum of fees for converted students)
    stats['sales_overview'] = total_payments
    stats['total_sale'] = total_payments

    # Demo conversion average time (average time from demo scheduled to demo completed)
    demo_times = db.session.query(
        func.avg(
            (func.extract('epoch', Demo.created_at) - func.extract('epoch', Demo.scheduled_date)) / 86400.0
        )
    ).filter(Demo.status == 'Completed').scalar()
    if demo_times is not None:
        # Convert days to hours
        stats['demo_conversion_avg_time'] = round(demo_times * 24, 2)
    else:
        stats['demo_conversion_avg_time'] = 0.0

    # Average fees per conversion
    if total_conversions > 0:
        avg_fee = total_payments / total_conversions
        stats['avg_fees_per_conversion'] = round(avg_fee, 2)
    else:
        stats['avg_fees_per_conversion'] = 0.0

    return stats
