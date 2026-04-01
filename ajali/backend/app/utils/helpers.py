from flask_mail import Message
from flask import current_app
from app import mail
import os
from twilio.rest import Client

def send_status_update_email(user_email, incident, old_status, new_status):
    """Send email notification about status change"""
    try:
        msg = Message(
            subject=f'Incident Status Update - {incident.title}',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[user_email]
        )
        
        msg.body = f"""
        Your incident report has been updated.
        
        Incident: {incident.title}
        Old Status: {old_status}
        New Status: {new_status}
        
        View your incident: {current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/incidents/{incident.id}
        
        Thank you for using Ajali!
        """
        
        msg.html = f"""
        <h2>Incident Status Update</h2>
        <p>Your incident report has been updated.</p>
        <ul>
            <li><strong>Incident:</strong> {incident.title}</li>
            <li><strong>Old Status:</strong> {old_status}</li>
            <li><strong>New Status:</strong> {new_status}</li>
        </ul>
        <p>
            <a href="{current_app.config.get('FRONTEND_URL', 'http://localhost:3000')}/incidents/{incident.id}">
                View your incident
            </a>
        </p>
        <p>Thank you for using Ajali!</p>
        """
        
        mail.send(msg)
        
    except Exception as e:
        print(f"Error sending email: {str(e)}")

