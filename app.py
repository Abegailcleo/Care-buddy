from flask import Flask, jsonify, request, render_template, redirect, url_for
import spacy
import os
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")

# Load spaCy NLP model
nlp = spacy.load("en_core_web_sm")

# Dictionary to map common symptoms to health advice
symptom_advice = {
    "fever": "You may have an infection. Drink plenty of fluids and rest. If symptoms persist, consult a doctor.",
    "headache": "Headaches can be caused by stress or dehydration. Try drinking water and resting.",
    "cough": "A cough may be a sign of a cold or flu. Rest, stay hydrated, and avoid irritants.",
    "fatigue": "Fatigue can be caused by lack of sleep or stress. Try to rest and take it easy."
}

# Function to check symptoms and return advice
def check_symptoms(user_input):
    doc = nlp(user_input)
    detected_symptoms = []

    for token in doc:
        if token.text.lower() in symptom_advice:
            detected_symptoms.append(token.text.lower())

    if detected_symptoms:
        response = []
        for symptom in detected_symptoms:
            response.append(f"Symptom: {symptom.capitalize()} - {symptom_advice[symptom]}")
        return detected_symptoms, "\n".join(response)
    else:
        return [], "Sorry, I couldn't detect any known symptoms in your input. Please try again."

# Feedback storage
feedback_counts = {}

# Home route

@app.route('/')
def home():
    return render_template('home.html')  # Render the homepage template


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')
# Map route
@app.route('/map')
def map():
    return render_template('map.html', google_maps_api_key=google_maps_api_key)

# Symptom Checker route
@app.route('/symptom-checker', methods=['GET', 'POST'])
def symptom_checker():
    advice = None
    symptoms = []
    if request.method == 'POST':
        user_input = request.form['symptoms']
        symptoms, advice = check_symptoms(user_input)
    return render_template('symptom_checker.html', advice=advice, symptoms=symptoms)

# Feedback route
@app.route('/feedback', methods=['POST'])
def feedback():
    user_feedback = request.form.get('feedback')
    symptom = request.form.get('symptom')

    # Initialize feedback counts for the symptom if not present
    if symptom not in feedback_counts:
        feedback_counts[symptom] = {"yes": 0, "no": 0}

    # Update feedback count for the specific symptom
    if user_feedback == "yes":
        feedback_counts[symptom]["yes"] += 1
    elif user_feedback == "no":
        feedback_counts[symptom]["no"] += 1

    return redirect(url_for('symptom_checker'))

# Feedback Summary route
@app.route('/feedback-summary')
def feedback_summary():
    return render_template('feedback_summary.html', feedback_counts=feedback_counts)

if __name__ == '__main__':
    app.run(debug=True)
