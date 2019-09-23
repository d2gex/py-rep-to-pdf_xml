from datetime import datetime
from src.app import db


class Reports(db.Model):
    __tablename__ = 'reports'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    xml_path = db.Column(db.String(200))
    pdf_path = db.Column(db.String(200))
    active = db.Column(db.Integer, default=0)
    processing = db.Column(db.Integer, default=0)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime)
