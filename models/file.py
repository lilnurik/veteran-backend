from models import db
from datetime import datetime
import uuid

class File(db.Model):
    __tablename__ = 'files'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.String(255), nullable=False)
    original_name = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)  # pdf, image
    category = db.Column(db.String(50))  # law, news, photo, other
    size = db.Column(db.Integer, nullable=False)  # file size in bytes
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'originalName': self.original_name,
            'url': self.url,
            'type': self.file_type,
            'category': self.category,
            'size': self.size,
            'uploadedAt': self.uploaded_at.isoformat() + 'Z'
        }