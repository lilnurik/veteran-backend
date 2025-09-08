from models import db
from datetime import datetime

class News(db.Model):
    __tablename__ = 'news'
    
    id = db.Column(db.Integer, primary_key=True)
    title_ru = db.Column(db.Text, nullable=False)
    title_uz = db.Column(db.Text, nullable=False)
    title_en = db.Column(db.Text, nullable=False)
    content_ru = db.Column(db.Text, nullable=False)
    content_uz = db.Column(db.Text, nullable=False)
    content_en = db.Column(db.Text, nullable=False)
    summary_ru = db.Column(db.Text, nullable=False)
    summary_uz = db.Column(db.Text, nullable=False)
    summary_en = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, nullable=False)
    image_url = db.Column(db.String(500))
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
            'content': {
                'ru': self.content_ru,
                'uz': self.content_uz,
                'en': self.content_en
            },
            'summary': {
                'ru': self.summary_ru,
                'uz': self.summary_uz,
                'en': self.summary_en
            },
            'date': self.date.isoformat() if self.date else None,
            'imageUrl': self.image_url,
            'createdAt': self.created_at.isoformat() + 'Z',
            'updatedAt': self.updated_at.isoformat() + 'Z'
        }