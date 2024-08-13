# Configure matplotlib to use non-interactive backend
import matplotlib
matplotlib.use('Agg')

from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import keras as keras
from keras import models, layers
import matplotlib.pyplot as plt
import io
import os
import sys
import base64
import json

# Fix encoding problem
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

# Read config file
with open("config/config.json", "r") as f:
    config = json.load(f)

# Load the needed configs
data_volume = config["data_volume"]
model_volume = config["model_volume"]
input_shape = tuple(config['input_shape'])
batch_size = config['batch_size']
epochs = config['epochs']
lr = config['lr']
architecture = config['architecture']

app = Flask(__name__)
CORS(app)

def load_data(data_path):
    """Load individual data from data folder."""
    x_train = np.load(os.path.join(data_path, "x_train.npy"))
    x_test = np.load(os.path.join(data_path, "x_test.npy"))
    y_train = np.load(os.path.join(data_path, "y_train.npy"))
    y_test = np.load(os.path.join(data_path, "y_test.npy"))
    return x_train, x_test, y_train, y_test


def CNN_model(input_shape, lr):
    """Create a CNN model based on configurations."""
    model = models.Sequential()
    model.add(layers.Input(shape=input_shape))

    # Create architecture based on config map
    for layer in architecture:
        if layer["type"] == "conv":
            model.add(layers.Conv2D(
                filters=layer["filters"],
                kernel_size=layer["size"],
                strides=layer["strides"],
                padding=layer["padding"],
                activation=layer["activation"]
            ))
        elif layer["type"] == "max_pool":
            model.add(layers.MaxPooling2D(
                pool_size=layer["size"],
                strides=layer["strides"]
            ))
        elif layer["type"] == "flatten":
            model.add(layers.Flatten())
        elif layer["type"] == "dense":
            model.add(layers.Dense(
                units=layer["units"],
                activation=layer["activation"]
            ))
        elif layer["type"] == "dropout":
            model.add(layers.Dropout(rate=layer["rate"]))
        elif layer["type"] == "batch_norm":
            model.add(layers.BatchNormalization(axis=layer["axis"]))
    
    opt = keras.optimizers.Adam(learning_rate=lr)
    model.compile(
        optimizer=opt,
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


def create_loss_plot(history):
    """Create loss plot image from the training history"""
    img_buffer = io.BytesIO()
    plt.figure()
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.title('Loss vs Epochs')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close()
    img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return img


@app.route("/list_data", methods=["GET"])
def list_data():
    """Return all saved datasets in data folder"""
    try: 
        datasets = []
        for file in os.listdir(data_volume):
            if os.path.isdir(os.path.join(data_volume, file)):
                datasets.append(file)
        return jsonify({"datasets": datasets}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400


@app.route("/train", methods=["POST"])
def train():
    """Load the data, train the model and save in models folder"""
    try:
        data = request.json

        # Check if required fields are present
        if not data or "data_folder" not in data or "model_name" not in data:
            return jsonify({"Missing data": "Request fields missing"}), 400
        else:
            data_folder = data.get("data_folder")
            model_name = data.get("model_name")
        
        # Check if dataset folder exists
        data_path = os.path.join(data_volume, data_folder)
        if not os.path.exists(data_path):
            return jsonify({"Mising data": "Data folder not found"}), 400

        # Load data and create CNN model
        x_train, x_test, y_train, y_test = load_data(data_path)
        model = CNN_model(input_shape, lr)

        # Train model
        try:
            history = model.fit(
                x_train, y_train, 
                epochs=epochs, 
                batch_size=batch_size, 
                validation_data=(x_test, y_test)
            )
        except Exception as e:
            return jsonify({"Failed to train model": str(e)}), 400
        
        # Get model accuracy and loss
        try:
            acc = f"{history.history['val_accuracy'][-1] * 100:.2f}"
            loss_img = create_loss_plot(history)
        except Exception as e:
            return jsonify({"Failed to evaluate model": str(e)}), 400
        
        # Save model
        try:
            model.save(f"{model_volume}/{model_name}.keras")
        except Exception as e:
            return jsonify({"Failed to save model": str(e)}), 400

        # Success message
        message = {
            "accuracy": acc,
            "loss": loss_img
        }
        return jsonify(message), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
