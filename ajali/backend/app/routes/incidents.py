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