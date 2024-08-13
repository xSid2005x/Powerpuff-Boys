import numpy as np
import logging
import os
from flask import Flask, request, jsonify
from keras.models import load_model
import cv2
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
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    image = cv2.resize(image, (size[0], size[1]))  # Resize the image
    image = np.array(image)
    image = image.reshape(1, size[0], size[1], size[2])
    image = image.astype('float32') / 255.0  # Normalize the image
    logging.info("Image preprocessed successfully")
    return image

def make_prediction(model, image):
    logging.info("Making prediction")
    prediction_probs = model.predict(image)
    predicted_class = np.argmax(prediction_probs)
    confidence = np.max(prediction_probs)
    logging.info(f"Prediction completed with confidence {confidence:.2f}")
    return predicted_class, confidence

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
    
    try:
        # Convert the uploaded image to a numpy array and decode it with OpenCV
        image_bytes = np.frombuffer(image_file.read(), np.uint8)
        image = cv2.imdecode(image_bytes, cv2.IMREAD_COLOR)
    except Exception as e:
        return jsonify({'error': f'Failed to decode image: {str(e)}'}), 400

    # Get the model name from the request
    model_name = request.form.get('model_folder')
    if not model_name:
        return jsonify({'error': 'No model name provided'}), 400

    # Preprocess the image
    processed_image = preprocess_image(image, size=input_shape)

    try:
        # Load the model
        model_path = f"{model_volume}/{model_name}.keras"
        model = load_trained_model(model_path)
    except Exception as e:
        return jsonify({'error': f'Failed to load model: {str(e)}'}), 400

    # Make a prediction
    predicted_class, confidence = make_prediction(model, processed_image)
    logging.info(f"Predicted Digit: {predicted_class} with confidence: {confidence:.2f}")

    # Return the prediction and confidence as JSON
    return jsonify({'prediction': int(predicted_class), 'confidence': float(confidence)}), 200

if __name__ == "__main__":
    logging.info("Starting Flask server")
    app.run(host='0.0.0.0', port=5003)
