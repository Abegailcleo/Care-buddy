# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    clinic_name = db.Column(db.String(100), nullable=False)
    doctor_name = db.Column(db.String(100), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    reason_for_visit = db.Column(db.String(100), nullable=False)
    appointment_type = db.Column(db.String(50), nullable=False)  # clinic, hospital, pharmacy

    def __repr__(self):
        return f'<Appointment {self.clinic_name} with Dr. {self.doctor_name}>'

db = SQLAlchemy()

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    description = db.Column(db.String(500))
    event_date = db.Column(db.Date, nullable=False)  # Check this
    event_time = db.Column(db.Time, nullable=False)  # Check this

    def __repr__(self):
        return f"<Event {self.title}>"


# In models.py
class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)  # Use your User model's ID
    message = db.Column(db.String(200), nullable=False)
    seen = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
