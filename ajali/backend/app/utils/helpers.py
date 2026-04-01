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

def send_status_update_sms(phone_number, incident, old_status, new_status):
    """Send SMS notification about status change"""
    try:
        account_sid = os.getenv('TWILIO_ACCOUNT_SID')
        auth_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        if not all([account_sid, auth_token, twilio_phone]):
            print("Twilio credentials not configured")
            return
        
        client = Client(account_sid, auth_token)
        
        message = f"Ajali! Update: Your incident '{incident.title[:30]}...' status changed from {old_status} to {new_status}"
        
        client.messages.create(
            body=message,
            from_=twilio_phone,
            to=phone_number
        )
        
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")