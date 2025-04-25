from models import Student, Teacher, TuitionAssignment, Demo, Feedback
from sqlalchemy import func, and_
from app import db
import json
from datetime import datetime, timedelta

def calculate_match_score(student, teacher):
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

def generate_dashboard_stats():
    """
    Generate statistics for the admin dashboard
    """
    stats = {}
    
    # Total counts
    stats['total_leads'] = Student.query.count()
    stats['total_teachers'] = Teacher.query.count()
    stats['total_assignments'] = TuitionAssignment.query.count()
    stats['total_demos'] = Demo.query.count()
    
    # Status breakdowns
    stats['lead_status'] = {
        'new': Student.query.filter_by(status='New').count(),
        'assigned': Student.query.filter_by(status='Assigned').count(),
        'converted': Student.query.filter_by(status='Converted').count(),
        'lost': Student.query.filter_by(status='Lost').count()
    }
    
    stats['assignment_status'] = {
        'pending': TuitionAssignment.query.filter_by(status='Pending').count(),
        'demo_scheduled': TuitionAssignment.query.filter_by(status='Demo Scheduled').count(),
        'converted': TuitionAssignment.query.filter_by(status='Converted').count(),
        'cancelled': TuitionAssignment.query.filter_by(status='Cancelled').count()
    }
    
    stats['demo_status'] = {
        'scheduled': Demo.query.filter_by(status='Scheduled').count(),
        'completed': Demo.query.filter_by(status='Completed').count(),
        'cancelled': Demo.query.filter_by(status='Cancelled').count()
    }
    
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
    months = []
    lead_counts = []
    conversion_counts = []
    
    for i in range(5, -1, -1):
        start_date = (datetime.utcnow() - timedelta(days=30 * i)).replace(day=1, hour=0, minute=0, second=0)
        if i > 0:
            end_date = (datetime.utcnow() - timedelta(days=30 * (i-1))).replace(day=1, hour=0, minute=0, second=0)
        else:
            end_date = datetime.utcnow()
        
        month_name = start_date.strftime('%b')
        months.append(month_name)
        
        # Count leads created in this month
        month_leads = Student.query.filter(
            and_(
                Student.created_at >= start_date,
                Student.created_at < end_date
            )
        ).count()
        lead_counts.append(month_leads)
        
        # Count conversions in this month
        month_conversions = TuitionAssignment.query.filter(
            and_(
                TuitionAssignment.status == 'Converted',
                TuitionAssignment.assigned_date >= start_date,
                TuitionAssignment.assigned_date < end_date
            )
        ).count()
        conversion_counts.append(month_conversions)
    
    stats['trend_months'] = months
    stats['trend_leads'] = lead_counts
    stats['trend_conversions'] = conversion_counts
    
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
    
    return stats

# Helper function for SQL case statements
def case(whens, else_=None):
    """Helper for building case statements in SQL"""
    from sqlalchemy.sql import case
    # In newer SQLAlchemy versions, case() expects individual tuples, not a list of tuples
    whens_list = list(whens)  # Convert to list to ensure it's iterable
    return case(*whens_list, else_=else_)
