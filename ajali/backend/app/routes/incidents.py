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

    incidents_bp.route('/', methods=['POST'])
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
            query = query.filter_by(severity=severity