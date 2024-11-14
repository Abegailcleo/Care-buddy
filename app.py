from flask import Flask, jsonify, request, render_template, redirect, url_for, flash
import spacy
import os
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from models import db, Event
from flask_mail import Mail, Message

# Initialize Flask app
app = Flask(__name__)
load_dotenv()

# Configure the Google Maps and Secret Key from the .env file
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY", "default_secret_key")
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv("EMAIL_USER")
app.config['MAIL_PASSWORD'] = os.getenv("EMAIL_PASS")

# Initialize Extensions
db.init_app(app)
mail = Mail(app)

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Symptom advice dictionary
symptom_advice = {
    "fever": "You may have an infection. Drink plenty of fluids and rest. If symptoms persist, consult a doctor.",
    "headache": "Headaches can be caused by stress or dehydration. Try drinking water and resting.",
    "cough": "A cough may be a sign of a cold or flu. Rest, stay hydrated, and avoid irritants.",
    "fatigue": "Fatigue can be caused by lack of sleep or stress. Try to rest and take it easy.",
    "sore throat": "A sore throat can be due to a viral infection or irritation. Gargle with warm salt water and stay hydrated.",
    "chills": "Chills can indicate an infection or fever. If accompanied by a fever, rest and monitor symptoms. Seek medical advice if needed.",
    "nausea": "Nausea can be caused by a variety of factors such as infections, stress, or indigestion. Try to rest, drink ginger tea, or eat bland foods.",
    "dizziness": "Dizziness can be caused by dehydration, low blood pressure, or other medical conditions. Drink water, rest, and avoid sudden movements.",
    "shortness of breath": "If you experience shortness of breath, it could be a sign of a respiratory issue. Seek medical attention immediately.",
    "chest pain": "Chest pain may be related to heart problems or muscle strain. If persistent or severe, seek emergency medical attention.",
    "stomach ache": "Stomach aches can be caused by indigestion, stress, or infections. Rest, drink water, and avoid heavy foods.",
    "joint pain": "Joint pain can be a result of overexertion or inflammation. Rest the affected area, apply ice, and consider using over-the-counter pain relievers.",
    "rash": "A rash could be a sign of an allergic reaction or infection. Keep the area clean, avoid scratching, and consult a doctor if it worsens.",
    "vomiting": "Vomiting may be a symptom of infection, food poisoning, or other conditions. Stay hydrated and rest. If it persists, seek medical attention.",
    "runny nose": "A runny nose is often caused by a cold or allergies. Drink fluids, use a saline nasal spray, and rest.",
    "muscle pain": "Muscle pain can result from physical activity or overexertion. Rest, hydrate, and use ice or heat as needed.",
    "diarrhea": "Diarrhea can be caused by infections or food intolerances. Stay hydrated, and avoid solid foods until it improves. Seek medical advice if it persists.",
    "constipation": "Constipation may be caused by lack of fiber, dehydration, or stress. Increase fiber intake and drink plenty of water.",
    "swollen glands": "Swollen glands can be a sign of infection or an immune response. Rest, stay hydrated, and seek medical advice if it worsens.",
    "blurred vision": "Blurred vision can be caused by eye strain or underlying health issues. Rest your eyes, and if persistent, consult an eye specialist.",
    "back pain": "Back pain may result from poor posture or muscle strain. Rest, apply heat or ice, and avoid heavy lifting.",
    "leg swelling": "Swelling in the legs could be due to poor circulation, standing for long periods, or an underlying condition. Elevate your legs and consider wearing compression socks.",
    "insomnia": "Difficulty sleeping may be caused by stress, anxiety, or poor sleep habits. Try relaxing activities like meditation or reading before bed.",
    "appetite loss": "Loss of appetite can be due to illness or emotional stress. Eat small meals throughout the day and consult a doctor if it continues.",
    "weight loss": "Unintentional weight loss can be a sign of several conditions. See a healthcare professional to rule out any underlying issues.",
    "leg cramps": "Leg cramps may occur due to dehydration, overexertion, or lack of potassium. Stretch the muscle gently and hydrate.",
    "earache": "Earaches can be caused by infections or pressure changes. Apply a warm compress and consult a doctor if pain persists.",
    "sinus pressure": "Sinus pressure can be caused by a cold or sinus infection. Use a humidifier, nasal saline spray, or consult a doctor.",
    "sweating": "Excessive sweating could be due to physical activity, heat, or stress. Stay cool and hydrated.",
    "hives": "Hives can be caused by allergies or an underlying infection. Avoid known allergens and consult a doctor if it doesn't improve.",
    "dry mouth": "Dry mouth can be a side effect of medications or dehydration. Drink water regularly and avoid caffeine or alcohol.",
    "hair loss": "Hair loss can be caused by stress, hormonal changes, or nutritional deficiencies. Maintain a balanced diet and consider consulting a dermatologist.",
    "numbness": "Numbness could indicate nerve compression or poor circulation. Avoid prolonged pressure and see a doctor if it persists.",
    "anxiety": "Anxiety can cause physical symptoms like shortness of breath and dizziness. Try relaxation techniques such as deep breathing and meditation.",
    "dehydration": "Dehydration can cause dry skin, dizziness, and fatigue. Drink water and electrolytes to rehydrate, and avoid caffeinated beverages.",
    "allergic reaction": "An allergic reaction can cause symptoms like swelling, rash, or difficulty breathing. If severe, seek emergency medical attention immediately.",
    "blisters": "Blisters can occur due to friction or burns. Keep the area clean and covered, and avoid popping the blister.",
    "pale skin": "Pale skin could indicate anemia, dehydration, or poor circulation. Consider increasing iron intake and consulting a doctor.",
    "swollen feet": "Swollen feet can be a result of standing for long periods, injury, or poor circulation. Elevate your feet and consider wearing comfortable shoes.",
    "cold sweats": "Cold sweats may be a symptom of shock or infection. Rest in a cool environment, drink water, and seek medical advice if needed.",
    "increased thirst": "Increased thirst can be a sign of dehydration or high blood sugar levels. Drink water and consult a doctor if the thirst persists.",
    "itchy skin": "Itchy skin can be caused by dry skin, allergies, or infections. Use soothing lotions and avoid hot showers.",
    "urinary discomfort": "Pain or discomfort while urinating can be a symptom of a urinary tract infection. Stay hydrated and see a doctor for treatment.",
    "bloody stool": "Blood in the stool can be a sign of a serious condition such as hemorrhoids, ulcers, or colorectal cancer. Seek medical attention immediately.",
    "yellowing skin": "Yellowing of the skin (jaundice) can indicate liver or gallbladder issues. Seek immediate medical attention if you notice yellowing of the skin or eyes.",
    "hiccups": "Hiccups can be caused by overeating or swallowing air. Hold your breath, drink water, or gently massage your throat to stop them.",
    "sensitivity to light": "Sensitivity to light may occur due to eye strain, migraines, or an eye infection. Rest your eyes in a dark, quiet room and avoid screen time.",
    "burning sensation": "A burning sensation could be due to nerve issues, infections, or inflammation. If persistent, consult a doctor.",
    "muscle weakness": "Muscle weakness can result from a variety of causes, including overexertion or neurological conditions. Rest and consult a healthcare professional if needed.",
    "itchy eyes": "Itchy eyes are commonly caused by allergies or dryness. Use eye drops, avoid allergens, and rest your eyes.",
    "puffy eyes": "Puffy eyes can be a result of lack of sleep or an allergic reaction. Apply cold compresses or use an anti-inflammatory cream."
}


# Function to check symptoms and return advice
def check_symptoms(user_input):
    doc = nlp(user_input)
    detected_symptoms = [token.text.lower() for token in doc if token.text.lower() in symptom_advice]
    if detected_symptoms:
        response = [f"Symptom: {symptom.capitalize()} - {symptom_advice[symptom]}" for symptom in detected_symptoms]
        return detected_symptoms, "\n".join(response)
    else:
        return [], "Sorry, I couldn't detect any known symptoms in your input. Please try again."

feedback_counts = {}  # Feedback storage

# Routes
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/map')
def map():
    return render_template('map.html', google_maps_api_key=google_maps_api_key)

@app.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    advice, symptoms = None, []
    if request.method == 'POST':
        user_input = request.form['symptoms']
        symptoms, advice = check_symptoms(user_input)
    return render_template('symptom_checker.html', advice=advice, symptoms=symptoms)

@app.route('/feedback', methods=['POST'])
def feedback():
    user_feedback = request.form.get('feedback')
    symptom = request.form.get('symptom')
    feedback_counts.setdefault(symptom, {"yes": 0, "no": 0})
    feedback_counts[symptom][user_feedback] += 1 if user_feedback in ["yes", "no"] else 0
    return redirect(url_for('symptom_checker'))

@app.route('/feedback-summary')
def feedback_summary():
    return render_template('feedback_summary.html', feedback_counts=feedback_counts)

@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['event_date']
        time = request.form['event_time']
        description = request.form.get('description', '')

        new_event = Event(
            title=title, 
            event_date=datetime.strptime(date, '%Y-%m-%d').date(),
            event_time=datetime.strptime(time, '%H:%M').time(),
            description=description
        )

        db.session.add(new_event)
        db.session.commit()

        flash("Event added successfully!", "success")
        return redirect(url_for('show_events'))  # Redirect to events page after adding
    
    return render_template('add_event.html')

@app.route('/events', methods=['GET'])
def show_events():
    events = Event.query.order_by(Event.event_date).all()
    return render_template('events.html', events=events)

def send_event_invite(email, event_title, event_date, event_time):
    msg = Message(
        'You’re Invited to an Event!',
        sender=app.config['MAIL_USERNAME'],
        recipients=[email]
    )
    msg.body = f"""
    You are invited to the event: {event_title}
    Date: {event_date}
    Time: {event_time}

    Please log in to your dashboard for more details.
    """
    mail.send(msg)
    
@app.route('/test_email')
def test_email():
    try:
        msg = Message(
            'Test Email from Flask',
            sender=app.config['MAIL_USERNAME'],
            recipients=['abegailcleo3@gmail.com']  # Replace with your email
        )
        msg.body = 'This is a test email sent from your Flask app.'
        mail.send(msg)
        return 'Test email sent successfully!'
    except Exception as e:
        return f'Failed to send test email: {str(e)}'


if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Create tables within app context
    app.run(debug=True)
