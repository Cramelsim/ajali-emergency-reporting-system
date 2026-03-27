from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import Incident, MediaFile, User
from app.utils.decorators import validate_incident_ownership
import os
from datetime import datetime
import uuid

incidents_bp = Blueprint('incidents', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'mov', 'avi'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@incidents_bp.route('/', methods=['POST'])
@jwt_required()
def create_incident():
    try:
        user_id = get_jwt_identity()
        data = request.form
        
        # Validate required fields
        required_fields = ['title', 'description', 'incident_type', 'latitude', 'longitude']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Create incident
        incident = Incident(
            title=data['title'],
            description=data['description'],
            incident_type=data['incident_type'],
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            location_address=data.get('location_address'),
            severity=data.get('severity', 'medium'),
            user_id=user_id
        )
        
        db.session.add(incident)
        db.session.flush()  # Get incident ID
        
        # Handle file uploads
        files = request.files.getlist('media')
        for file in files:
            if file and allowed_file(file.filename):
                if file.content_length and file.content_length > MAX_FILE_SIZE:
                    return jsonify({'error': f'File {file.filename} exceeds size limit'}), 400
                
                # Generate unique filename
                ext = file.filename.rsplit('.', 1)[1].lower()
                filename = f"{uuid.uuid4()}.{ext}"
                
                # Determine file type
                file_type = 'image' if ext in {'png', 'jpg', 'jpeg', 'gif'} else 'video'
                
                # Save file
                file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # Create media record
                media = MediaFile(
                    incident_id=incident.id,
                    file_type=file_type,
                    file_url=f"/uploads/{filename}"
                )
                db.session.add(media)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Incident created successfully',
            'incident': incident.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/', methods=['GET'])
def get_incidents():
    try:
        # Query parameters for filtering
        status = request.args.get('status')
        incident_type = request.args.get('type')
        severity = request.args.get('severity')
        lat = request.args.get('lat')
        lng = request.args.get('lng')
        radius = request.args.get('radius', 10)  # Radius in km
        
        query = Incident.query
        
        if status:
            query = query.filter_by(status=status)
        
        if incident_type:
            query = query.filter_by(incident_type=incident_type)
        
        if severity:
            query = query.filter_by(severity=severity)
        
        # Filter by location if coordinates provided
        if lat and lng:
            # Simple bounding box filter (for demo purposes)
            # In production, use PostGIS for proper geospatial queries
            lat = float(lat)
            lng = float(lng)
            radius = float(radius)
            
            # Approximate conversion: 1 degree latitude = 111 km
            lat_delta = radius / 111
            lng_delta = radius / (111 * abs(math.cos(math.radians(lat))) + 0.01)
            
            query = query.filter(
                Incident.latitude.between(lat - lat_delta, lat + lat_delta),
                Incident.longitude.between(lng - lng_delta, lng + lng_delta)
            )
        
        incidents = query.order_by(Incident.created_at.desc()).all()
        
        return jsonify({
            'incidents': [incident.to_dict() for incident in incidents]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<int:incident_id>', methods=['GET'])
def get_incident(incident_id):
    try:
        incident = Incident.query.get(incident_id)
        
        if not incident:
            return jsonify({'error': 'Incident not found'}), 404
        
        return jsonify({'incident': incident.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<int:incident_id>', methods=['PUT'])
@jwt_required()
@validate_incident_ownership
def update_incident(incident_id):
    try:
        incident = Incident.query.get(incident_id)
        data = request.get_json()
        
        # Update fields
        updatable_fields = ['title', 'description', 'incident_type', 'latitude', 
                           'longitude', 'location_address', 'severity']
        
        for field in updatable_fields:
            if field in data:
                setattr(incident, field, data[field])
        
        incident.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Incident updated successfully',
            'incident': incident.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<int:incident_id>', methods=['DELETE'])
@jwt_required()
@validate_incident_ownership
def delete_incident(incident_id):
    try:
        incident = Incident.query.get(incident_id)
        
        # Delete associated media files
        for media in incident.media_files:
            file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                    os.path.basename(media.file_url))
            if os.path.exists(file_path):
                os.remove(file_path)
        
        db.session.delete(incident)
        db.session.commit()
        
        return jsonify({'message': 'Incident deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/<int:incident_id>/media', methods=['POST'])
@jwt_required()
@validate_incident_ownership
def add_media(incident_id):
    try:
        incident = Incident.query.get(incident_id)
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed'}), 400
        
        if file.content_length and file.content_length > MAX_FILE_SIZE:
            return jsonify({'error': 'File exceeds size limit'}), 400
        
        # Generate unique filename
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4()}.{ext}"
        
        # Determine file type
        file_type = 'image' if ext in {'png', 'jpg', 'jpeg', 'gif'} else 'video'
        
        # Save file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        # Create media record
        media = MediaFile(
            incident_id=incident.id,
            file_type=file_type,
            file_url=f"/uploads/{filename}"
        )
        
        db.session.add(media)
        db.session.commit()
        
        return jsonify({
            'message': 'Media added successfully',
            'media': media.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/media/<int:media_id>', methods=['DELETE'])
@jwt_required()
def delete_media(media_id):
    try:
        user_id = get_jwt_identity()
        media = MediaFile.query.get(media_id)
        
        if not media:
            return jsonify({'error': 'Media not found'}), 404
        
        # Check if user owns the incident
        if media.incident.user_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Delete file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 
                                os.path.basename(media.file_url))
        if os.path.exists(file_path):
            os.remove(file_path)
        
        db.session.delete(media)
        db.session.commit()
        
        return jsonify({'message': 'Media deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@incidents_bp.route('/user/me', methods=['GET'])
@jwt_required()
def get_user_incidents():
    try:
        user_id = get_jwt_identity()
        incidents = Incident.query.filter_by(user_id=user_id).order_by(Incident.created_at.desc()).all()
        
        return jsonify({
            'incidents': [incident.to_dict() for incident in incidents]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500