from flask import Flask, request, jsonify
import numpy as np
import keras as keras
from keras import models, layers
import os
import io
import sys


# Fix encoding problem
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Parameters
input_shape = (28, 28, 1)
batch_size = 128
epochs = 3
lr = 0.001

app = Flask(__name__)


def load_data_from_folder(folder_path):
    x_train = np.load(os.path.join(folder_path, 'x_train.npy'))
    x_test = np.load(os.path.join(folder_path, 'x_test.npy'))
    y_train = np.load(os.path.join(folder_path, 'y_train.npy'))
    y_test = np.load(os.path.join(folder_path, 'y_test.npy'))
    return x_train, x_test, y_train, y_test


def CNN_model(input_shape, lr):
    model = models.Sequential()
    model.add(layers.Input(shape=input_shape)) 
    model.add(layers.Conv2D(32, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation = 'relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(64, activation='relu'))
    model.add(layers.Dense(10, activation='softmax'))
    opt = keras.optimizers.Adam(learning_rate=lr)
    model.compile(optimizer=opt, loss='categorical_crossentropy', metrics=['accuracy'])
    return model


@app.route('/train', methods=['GET'])
def train():
    folder = request.args.get('data')
    model_name = request.args.get('model')
    
    # Check if folder exists
    folder_path = os.path.join('volume/data', folder)
    if not os.path.exists(folder_path):
        return jsonify({"error": "Folder not found"}), 400

    # Load data and create CNN model
    x_train, x_test, y_train, y_test = load_data_from_folder(folder_path)
    model = CNN_model(input_shape, lr)

    # Train model
    try:
        model.fit(
            x_train, y_train, 
            epochs=epochs, 
            batch_size=batch_size, 
            validation_data=(x_test, y_test)
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Save model
    model.save(f'volume/models/{model_name}.keras')

    return jsonify({"Message": "Model trained and saved successfully"}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
