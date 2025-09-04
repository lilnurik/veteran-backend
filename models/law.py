from models import db
from datetime import datetime
import json

class Law(db.Model):
    __tablename__ = 'laws'
    
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.Text, nullable=False)
    title_uz = db.Column(db.Text, nullable=False)
    title_en = db.Column(db.Text, nullable=False)
    description_ru = db.Column(db.Text, nullable=False)
    description_uz = db.Column(db.Text, nullable=False)
    description_en = db.Column(db.Text, nullable=False)
    category_ru = db.Column(db.String(255), nullable=False)
    category_uz = db.Column(db.String(255), nullable=False)
    category_en = db.Column(db.String(255), nullable=False)
    date = db.Column(db.Date, nullable=False)
    pdf_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': {
                'ru': self.title_ru,
                'uz': self.title_uz,
                'en': self.title_en
            },
            'description': {
                'ru': self.description_ru,
                'uz': self.description_uz,
                'en': self.description_en
            },
            'category': {
                'ru': self.category_ru,
                'uz': self.category_uz,
                'en': self.category_en
            },
            'date': self.date.isoformat() if self.date else None,
            'pdfUrl': self.pdf_url,
            'createdAt': self.created_at.isoformat() + 'Z',
            'updatedAt': self.updated_at.isoformat() + 'Z'
        }