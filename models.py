# models.py
from flask_sqlalchemy import SQLAlchemy

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
