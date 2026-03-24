from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db
from app.models import Incident, MediaFile, User
from app.utils.decorators import validate_incident_ownership
import os
from datetime import datetime
import uuid