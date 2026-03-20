from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    phone_number = db.Column(db.String(20))
    is_admin = db.Column(db.Boolean, default=False)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    incidents = db.relationship('Incident', backref='author', lazy=True)
    
        def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'username': self.username,
            'phone_number': self.phone_number,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Incident(db.Model):
    __tablename__ = 'incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    incident_type = db.Column(db.String(50), nullable=False)  # 'accident', 'fire', 'crime', etc.
    status = db.Column(db.String(50), default='pending')  # pending, under_investigation, rejected, resolved
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    location_address = db.Column(db.String(500))
    severity = db.Column(db.String(50))  # low, medium, high, critical
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    media_files = db.relationship('MediaFile', backref='incident', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='incident', lazy=True, cascade='all, delete-orphan')
