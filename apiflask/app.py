import sys
from flask import Flask, request, jsonify, render_template, redirect
from flask_sqlalchemy import SQLAlchemy
import base64
import numpy as np
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import img_to_array
from PIL import Image
import io
import os

# Update the import path to reflect your directory structure
sys.path.append(r'C:\Users\raymond\Downloads\django-main\django-main')
from dashboard.models import Flower  # Correct path to models.py

app = Flask(__name__, template_folder=r'C:\Users\raymond\Downloads\django-main\django-main\dashboard\templates\dashboard')

# Configure SQLite database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flowers.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Define the Flower model
class Flower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)

# Ensure the database and table exist
with app.app_context():
    db.create_all()

# Define model file path
model_path = r'C:\Users\raymond\Downloads\django-main\django-main\model\best_trained_model.keras'

if os.path.exists(model_path):
    model = load_model(model_path)
else:
    raise FileNotFoundError(f"Model file not found at {model_path}. Please ensure the file exists.")

# Define flower labels and descriptions
flower_labels = ['astilbe', 'bellflower', 'black eyed susan', 'coreopsies', 'dandelion', 
                 'iris', 'rose', 'sunflower', 'tulip', 'water lily']
flower_descriptions = {
    'astilbe': "Astilbe is a genus of plants in the family Saxifragaceae, known for its feathery flowers and attractive foliage.",
    'bellflower': "Bellflowers are known for their bell-shaped flowers and are often used in gardens.",    
    'black eyed susan': "A wildflower with bright yellow petals and a dark brown center, often found in North America.",
    'coreopsies': "Coreopsis is a genus of flowering plants, known for its bright yellow, daisy-like flowers.",
    'dandelion': "Dandelions are bright yellow flowers that bloom in early spring, known for their puffball seed heads.",
    'iris': "Iris flowers are known for their wide range of colors and distinctive, sword-like leaves.",
    'rose': "Roses are a symbol of love, known for their fragrant and beautiful layered petals.",
    'sunflower': "Sunflowers are known for their large, bright yellow blooms that follow the sun's movement.",
    'tulip': "Tulips are bulbous flowers that come in a variety of colors and are associated with spring.",
    'water lily': "Water lilies are aquatic flowers with large, round leaves and colorful blooms floating on the water."
}

@app.route('/')
def index():
    return render_template('dashboard.html')


@app.route('/flowers', methods=['GET'])
def get_flowers():
    try:
        flowers = list(Flower.query.all())  # Convert the query result to a list
        return render_template('flowers.html', flowers=flowers)
    except Exception as e:
        print(f"Error occurred in get_flowers route: {str(e)}")  # Log error details
        return jsonify({"error": f"Error fetching data: {str(e)}"}), 500

@app.route('/delete/<int:flower_id>', methods=['POST'])
def delete_flower(flower_id):
    try:
        flower = Flower.query.get_or_404(flower_id)
        db.session.delete(flower)
        db.session.commit()
        return redirect('/flowers')  # Redirect back to the records page
    except Exception as e:
        return jsonify({"error": f"Error deleting flower: {str(e)}"}), 500

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # Parse the incoming JSON
        data = request.json
        image_data = data['image']

        # Decode the base64 image
        image_data = image_data.split(',')[1]
        image_bytes = base64.b64decode(image_data)

        # Open and resize the image
        image = Image.open(io.BytesIO(image_bytes)).resize((224, 224))

        # Preprocess the image
        image_array = img_to_array(image) / 255.0
        image_array = np.expand_dims(image_array, axis=0)

        # Predict using the model
        predictions = model.predict(image_array)
        predicted_label = flower_labels[np.argmax(predictions)]
        flower_description = flower_descriptions.get(predicted_label, "Description not available.")

        # Ensure the static directory exists
        static_dir = os.path.join(os.path.dirname(__file__), "static")
        os.makedirs(static_dir, exist_ok=True)

        # Save image to the server
        image_name = f"{predicted_label}.jpg"
        image_path = os.path.join(static_dir, image_name)
        image.save(image_path)

        # Save to database
        flower = Flower(image_name=image_name, description=flower_description)
        db.session.add(flower)
        db.session.commit()

        # Return the prediction and description
        return jsonify({
            "flowerType": predicted_label,
            "description": flower_description
        })

    except Exception as e:
        # Log the error for debugging
        print(f"Error occurred: {str(e)}")
        return jsonify({"error": f"Error detecting flower. Details: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True)
