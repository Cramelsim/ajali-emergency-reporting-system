from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db, celery
from app.models import Incident, User, Notification
from app.utils.decorators import admin_required
from app.utils.helpers import send_status_update_email, send_status_update_sms
from datetime import datetime

admin_bp = Blueprint('admin', __name__)