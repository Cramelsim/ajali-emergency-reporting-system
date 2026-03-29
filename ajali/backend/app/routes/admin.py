from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, celery
from app.models import Incident, User, Notification
from app.utils.decorators import admin_required
from app.utils.helpers import send_status_update_email, send_status_update_sms
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/incidents', methods=['GET'])
@jwt_required()
@admin_required
def get_all_incidents():
    try:
        # Pagination
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filtering
        status = request.args.get('status')
        incident_type = request.args.get('type')
        
        query = Incident.query
        
        if status:
            query = query.filter_by(status=status)
        
        if incident_type:
            query = query.filter_by(incident_type=incident_type)
        
        paginated = query.order_by(Incident.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'incidents': [incident.to_dict() for incident in paginated.items],
            'total': paginated.total,
            'pages': paginated.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500