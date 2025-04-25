import os
import sys
import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content

def send_email(to_email, subject, html_content=None, text_content=None, from_email="axra.tutors@gmail.com"):
    """
    Send an email using SendGrid
    
    Parameters:
    - to_email: Recipient email address
    - subject: Email subject
    - html_content: HTML content of the email (optional)
    - text_content: Plain text content of the email (optional)
    - from_email: Sender email address (default is axra.tutors@gmail.com)
    
    Returns:
    - True if email was sent successfully, False otherwise
    """
    # Check if SendGrid API key exists
    sendgrid_key = os.environ.get('SENDGRID_API_KEY')
    if not sendgrid_key:
        logging.error("SENDGRID_API_KEY environment variable must be set")
        return False
    
    message = Mail(
        from_email=Email(from_email),
        to_emails=To(to_email),
        subject=subject
    )
    
    # Set content (prefer HTML if both are provided)
    if html_content:
        message.content = Content("text/html", html_content)
    elif text_content:
        message.content = Content("text/plain", text_content)
    else:
        logging.error("Either html_content or text_content must be provided")
        return False
    
    try:
        sg = SendGridAPIClient(sendgrid_key)
        sg.send(message)
        logging.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logging.error(f"SendGrid error: {e}")
        return False

def send_demo_reminder(student_name, student_email, teacher_name, demo_date_time, location=None):
    """
    Send a demo reminder email to a student
    
    Parameters:
    - student_name: Name of the student
    - student_email: Email address of the student
    - teacher_name: Name of the teacher
    - demo_date_time: Date and time of the demo (formatted string)
    - location: Location of the demo (optional)
    
    Returns:
    - True if email was sent successfully, False otherwise
    """
    subject = f"Reminder: Tuition Demo with {teacher_name} on {demo_date_time}"
    
    # Create HTML content
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #4a6baf;">Demo Session Reminder</h2>
            <p>Dear <strong>{student_name}</strong>,</p>
            <p>This is a friendly reminder about your upcoming tuition demo session:</p>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Teacher:</strong> {teacher_name}</p>
                <p><strong>Date & Time:</strong> {demo_date_time}</p>
                {f'<p><strong>Location:</strong> {location}</p>' if location else ''}
            </div>
            <p>Please ensure you're prepared and on time for the session. This demo will help determine if the teacher is a good fit for your learning needs.</p>
            <p>If you need to reschedule or have any questions, please contact us immediately.</p>
            <p>Best regards,<br>Axra Tutors Team</p>
        </div>
    </body>
    </html>
    """
    
    # Create plain text content as fallback
    text_content = f"""
    Demo Session Reminder
    
    Dear {student_name},
    
    This is a friendly reminder about your upcoming tuition demo session:
    
    Teacher: {teacher_name}
    Date & Time: {demo_date_time}
    {f'Location: {location}' if location else ''}
    
    Please ensure you're prepared and on time for the session. This demo will help determine if the teacher is a good fit for your learning needs.
    
    If you need to reschedule or have any questions, please contact us immediately.
    
    Best regards,
    Axra Tutors Team
    """
    
    return send_email(student_email, subject, html_content, text_content)

def send_teacher_demo_notification(teacher_name, teacher_email, student_name, demo_date_time, location=None):
    """
    Send a demo notification email to a teacher
    
    Parameters:
    - teacher_name: Name of the teacher
    - teacher_email: Email address of the teacher
    - student_name: Name of the student
    - demo_date_time: Date and time of the demo (formatted string)
    - location: Location of the demo (optional)
    
    Returns:
    - True if email was sent successfully, False otherwise
    """
    subject = f"Tuition Demo Assignment: {student_name} on {demo_date_time}"
    
    # Create HTML content
    html_content = f"""
    <html>
    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #ddd; border-radius: 5px;">
            <h2 style="color: #4a6baf;">Demo Session Assignment</h2>
            <p>Dear <strong>{teacher_name}</strong>,</p>
            <p>You have been assigned to conduct a tuition demo session:</p>
            <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0;">
                <p><strong>Student:</strong> {student_name}</p>
                <p><strong>Date & Time:</strong> {demo_date_time}</p>
                {f'<p><strong>Location:</strong> {location}</p>' if location else ''}
            </div>
            <p>Please ensure you're well-prepared and punctual for this session. This demo is crucial for converting the lead into a regular student.</p>
            <p>If you cannot make it at the scheduled time, please inform us immediately so we can make alternative arrangements.</p>
            <p>Best regards,<br>Axra Tutors Team</p>
        </div>
    </body>
    </html>
    """
    
    # Create plain text content as fallback
    text_content = f"""
    Demo Session Assignment
    
    Dear {teacher_name},
    
    You have been assigned to conduct a tuition demo session:
    
    Student: {student_name}
    Date & Time: {demo_date_time}
    {f'Location: {location}' if location else ''}
    
    Please ensure you're well-prepared and punctual for this session. This demo is crucial for converting the lead into a regular student.
    
    If you cannot make it at the scheduled time, please inform us immediately so we can make alternative arrangements.
    
    Best regards,
    Axra Tutors Team
    """
    
    return send_email(teacher_email, subject, html_content, text_content)