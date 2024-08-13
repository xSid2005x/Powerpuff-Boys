import numpy as np
import logging
import os
from flask import Flask, request, jsonify
from keras.models import load_model
from PIL import Image
import io
from flask_cors import CORS
import json
import sys

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Fix encoding problem
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

with open("config/config.json", "r") as f:
    config = json.load(f)

# Parameters
model_volume = config["model_volume"]
input_shape = tuple(config['input_shape'])

# Initialize Flask app
app = Flask(__name__)
CORS(app)

def load_trained_model(model_path):
    logging.info(f"Loading model from {model_path}")
    model = load_model(model_path)
    logging.info("Model loaded successfully")
    return model

def preprocess_image(image, size=(28, 28, 1)):
    logging.info("Preprocessing the image")
    # Convert the image to grayscale, resize it, and normalize it
    image = image.convert("L")
    image = image.resize((size[0], size[1]))
    image = np.array(image)
    image = image.reshape(1, size[0], size[1], size[2])
    image = image.astype('float32') / 255.0
    logging.info("Image preprocessed successfully")
    return image

def make_prediction(model, image):
    logging.info("Making prediction")
    prediction = model.predict(image)
    logging.info("Prediction completed")
    return np.argmax(prediction)


@app.route("/list_models", methods=["GET"])
def list_data():
    try: 
        models = []
        for file in os.listdir(model_volume):
            if file.endswith(".keras"):
                models.append(file.strip(".keras"))
        return jsonify({"models": models}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 402


@app.route('/predict', methods=['POST'])
def predict():
    # Get the image file from the request
    if 'test_image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    image_file = request.files['test_image']
    print(image_file)

    # Get the model name from the request
    model_name = request.form.get('model_folder')
    if not model_name:
        return jsonify({'error': 'No model name provided'}), 400

    # Open the image file and preprocess it
    image = Image.open(io.BytesIO(image_file.read()))
    processed_image = preprocess_image(image)

    # Load the model
    model_path = f"{model_volume}/{model_name}.keras"
    model = load_trained_model(model_path)

    # Make a prediction
    prediction = make_prediction(model, processed_image)
    logging.info(f"Predicted Digit: {prediction}")

    # Return the prediction as JSON
    return jsonify({'prediction': int(prediction)}), 200

if __name__ == "__main__":
    logging.info("Starting Flask server")
    app.run(host='0.0.0.0', port=5003)
