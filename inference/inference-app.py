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

# Fix encoding problem for stdout and stderr
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Load configuration parameters from config.json
with open("config/config.json", "r") as f:
    config = json.load(f)

# Extract parameters from the config file
model_volume = config["model_volume"]  # Directory where models are stored
input_shape = tuple(config['input_shape'])  # Expected input shape for the model

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing (CORS)

def load_trained_model(model_path):
    """
    Load the trained model from the specified path.
    """
    logging.info(f"Loading model from {model_path}")
    model = load_model(model_path)
    logging.info("Model loaded successfully")
    return model

def preprocess_image(image, size=(28, 28, 1)):
    """
    Preprocess the image to match the input requirements of the model:
    - Convert to grayscale
    - Resize to the specified size
    - Normalize pixel values to [0, 1]
    """
    logging.info("Preprocessing the image")
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)  # Convert to grayscale
    image = cv2.resize(image, (size[0], size[1]))  # Resize the image
    image = np.array(image)
    image = image.reshape(1, size[0], size[1], size[2])  # Reshape to match model input
    image = image.astype('float32') / 255.0  # Normalize pixel values
    logging.info("Image preprocessed successfully")
    return image

def make_prediction(model, image):
    """
    Make a prediction using the provided model and preprocessed image.
    Returns the predicted class and the confidence level.
    """
    logging.info("Making prediction")
    prediction_probs = model.predict(image)  # Get prediction probabilities for all classes
    predicted_class = np.argmax(prediction_probs)  # Find the class with the highest probability
    confidence = np.max(prediction_probs)  # Find the highest probability (confidence level)
    logging.info(f"Prediction completed with confidence {confidence:.2f}")
    return predicted_class, confidence

@app.route("/list_models", methods=["GET"])
def list_data():
    """
    Endpoint to list all available models in the model volume.
    """
    try: 
        models = []
        for file in os.listdir(model_volume):
            if file.endswith(".keras"):  # Only consider .keras model files
                models.append(file.strip(".keras"))
        return jsonify({"models": models}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 402

@app.route('/predict', methods=['POST'])
def predict():
    """
    Endpoint to handle prediction requests:
    - Accepts an image file and model name
    - Preprocesses the image
    - Loads the specified model
    - Returns the predicted class and confidence level as JSON
    """
    # Check if image is provided in the request
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
    app.run(host='0.0.0.0', port=5003)  # Start the Flask server
