from flask import Flask, jsonify, request,render_template
import os
from dotenv import load_dotenv



app = Flask(__name__)

load_dotenv()  # Load environment variables
google_maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY")



@app.route('/')
def home():
    return "Welcome to the Care Buddy!"



@app.route('/map')
def map():
    return render_template('map.html', google_maps_api_key=google_maps_api_key)



if __name__ == '__main__':
    app.run(debug=True)