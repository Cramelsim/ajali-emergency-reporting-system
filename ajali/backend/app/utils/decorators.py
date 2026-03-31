from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity
from app.models import User, Incident

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user or not user.is_admin:
            return jsonify({'error': 'Admin access required'}), 403
        
        return f(*args, **kwargs)
    return decorated_function

def validate_incident_ownership(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = get_jwt_identity()
        incident_id = kwargs.get('incident_id')
                if not incident_id:
            return jsonify({'error': 'Incident ID required'}), 400
        
        incident = Incident.query.get(incident_id)