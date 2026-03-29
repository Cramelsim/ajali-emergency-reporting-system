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
@admin_bp.route('/incidents/<int:incident_id>/status', methods=['PUT'])
@jwt_required()
@admin_required
def update_incident_status(incident_id):
    try:
        incident = Incident.query.get(incident_id)
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        data = request.get_json()
        new_status = data.get('status')
        
        valid_statuses = ['pending', 'under_investigation', 'rejected', 'resolved']
        if new_status not in valid_statuses:
            return jsonify({'error': 'Invalid status'}), 400
        
        old_status = incident.status
        incident.status = new_status
        incident.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        # Send notifications asynchronously
        if new_status != old_status:
            send_status_notifications.delay(incident_id, old_status, new_status)
        
        return jsonify({
            'message': 'Incident status updated successfully',
            'incident': incident.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
    
@admin_bp.route('/incidents/stats', methods=['GET'])
@jwt_required()
@admin_required
def get_incident_stats():
    try:
        total_incidents = Incident.query.count()
        pending = Incident.query.filter_by(status='pending').count()
        under_investigation = Incident.query.filter_by(status='under_investigation').count()
        resolved = Incident.query.filter_by(status='resolved').count()
        rejected = Incident.query.filter_by(status='rejected').count()
        
        # Incidents by type
        incidents_by_type = db.session.query(
            Incident.incident_type, db.func.count(Incident.id)
        ).group_by(Incident.incident_type).all()
        
        return jsonify({
            'total': total_incidents,
            'pending': pending,
            'under_investigation': under_investigation,
            'resolved': resolved,
            'rejected': rejected,
            'by_type': dict(incidents_by_type)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500