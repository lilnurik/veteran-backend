from models import db
from datetime import datetime
import json

class Comrade(db.Model):
    __tablename__ = 'comrades'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    middle_name = db.Column(db.String(100))
    unit = db.Column(db.String(255), nullable=False)
    region = db.Column(db.String(255), nullable=False)
    year_of_service_from = db.Column(db.Integer, nullable=False)
    year_of_service_to = db.Column(db.Integer)
    rank = db.Column(db.String(100))
    photo_url = db.Column(db.String(500))
    contact_info = db.Column(db.Text)  # JSON string with phone, email, address
    additional_info = db.Column(db.Text)
    is_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_contact_info(self):
        """Parse contact info from JSON string"""
        if self.contact_info:
            try:
                return json.loads(self.contact_info)
            except (json.JSONDecodeError, TypeError):
                return {}
        return {}
    
    def set_contact_info(self, contact_data):
        """Set contact info as JSON string"""
        if contact_data:
            self.contact_info = json.dumps(contact_data)
        else:
            self.contact_info = None
    
    def to_dict(self):
        return {
            'id': self.id,
            'firstName': self.first_name,
            'lastName': self.last_name,
            'middleName': self.middle_name,
            'unit': self.unit,
            'region': self.region,
            'yearOfServiceFrom': self.year_of_service_from,
            'yearOfServiceTo': self.year_of_service_to,
            'rank': self.rank,
            'photoUrl': self.photo_url,
            'contactInfo': self.get_contact_info(),
            'additionalInfo': self.additional_info,
            'isVerified': self.is_verified,
            'createdAt': self.created_at.isoformat() + 'Z',
            'updatedAt': self.updated_at.isoformat() + 'Z'
        }