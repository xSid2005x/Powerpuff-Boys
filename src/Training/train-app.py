from flask import Flask, request, jsonify
import numpy as np
import keras as keras
from keras import models, layers
import os
import io
import sys
import base64
import json

# Fix encoding problem
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")

with open("/app/config/config.json", "r") as f:
    config = json.load(f)

# Parameters
input_shape = tuple(config['input_shape'])
batch_size = config['batch_size']
epochs = config['epochs']
lr = config['lr']
architecture = config['architecture']

app = Flask(__name__)

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
        param = layer[1]
        if layer[0] == "conv":
            model.add(layers.Conv2D(param[0], (param[1], param[2]), activation=param[3]))
        elif layer[0] == "pool":
            model.add(layers.MaxPooling2D((param[0], param[1])))
        elif layer[0] == "flatten":
            model.add(layers.Flatten())
        elif layer[0] == "dense":
            model.add(layers.Dense(param[0], activation=param[1]))
    
    opt = keras.optimizers.Adam(learning_rate=lr)
    model.compile(
        optimizer=opt,
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model


# If loss image is used
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def create_loss_plot(history):
    """Create loss plot image from the training history"""
    img_buffer = io.BytesIO()
    plt.figure()
    plt.plot(history.history['loss'], label='loss')
    plt.plot(history.history['val_loss'], label='val_loss')
    plt.xlabel('Epoch')
    plt.ylabel('Loss')
    plt.legend()
    plt.savefig(img_buffer, format='png')
    img_buffer.seek(0)
    plt.close()
    img = base64.b64encode(img_buffer.getvalue()).decode('utf-8')
    return img


@app.route("/train", methods=["POST"])
def train():
    try:
        data = request.json

        # Check if required fields are present
        if not data or "data" not in data or "model" not in data:
            return jsonify({"Missing data": "Request fields missing"}), 401
        else:
            data_path = data.get("data")
            model_name = data.get("model")
        
        # Check if data folder exists
        if not os.path.exists(data_path):
            return jsonify({"Mising data": "Data folder not found"}), 401

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
            return jsonify({"Failed to train model": str(e)}), 402
        
        # Get model metrics
        try:
            acc = f"{history.history['val_accuracy'][-1] * 100:.2f}"
            img = create_loss_plot(history)
        except Exception as e:
            return jsonify({"Failed to evaluate model": str(e)}), 402
        
        # Save model
        try:
            model.save(f"volume/models/{model_name}.keras")
        except Exception as e:
            return jsonify({"Failed to save model": str(e)}), 402

        # Success message
        message = {
            "Accuracy": acc,
            "Loss": img
        }
        return jsonify(message), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 402

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
