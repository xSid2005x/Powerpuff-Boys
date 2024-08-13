from flask import Flask, request, jsonify
import numpy as np
import json
import io
import os
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
from flask_cors import CORS

# Load configs
with open("config/config.json", "r") as f:
    config = json.load(f)
data_volume = config["data_volume"]
split_ratio = config["split_ratio"]
input_shape = tuple(config['input_shape'])


app = Flask(__name__)
CORS(app)


@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file was properly uploaded
    if 'dataset_file' not in request.files:
        return jsonify({"Missing Data": "File field missing"}), 401

    file = request.files['dataset_file']
    if file.filename == '' or not file:
        return jsonify({"Invalid Data": "Invalid file"}), 402

    # Check if dataset name is present
    dataset_name = request.form.get('dataset_name')
    if not dataset_name:
        return jsonify({"Missing Data": "Name missing"}), 401

    # Process the dataset
    message = process_data(file, dataset_name)
    
    return jsonify(message), 200

def process_data(file, dataset_name):

    # Cook This --------------------------------------------------------------------------------------------
    
    # Load different file types. Either npy, npz or zip folder containing images
    # Also state the assumptions, for example the npz file alread had the 4 (x_train, x_test, etc.)

    pass
    # if filename.endswith('.npz'):
    #     data = np.load(filename)
    #     keys = list(data.keys())
    #     if len(keys) == 0:
    #         raise ValueError("No data found in the .npz file.")
    #     X = data[keys[0]]
    # elif filename.endswith('.npy'):
    #     X = np.load(filename)
    # else:
    #     raise ValueError("Unsupported file format. Please upload a .npz, .npy, or .csv file.")
    

    # Depending on the file assumption, there may or may not need to be a data split part
    # There is a config split ratio, use that if u need to split data
    pass



    # Look into image transformations to normalize and resize the images
    # Something like pytorch maybe?
    pass
    



    # ------------------------------------------------------------------------------------------------------

    
    # Assuming npz file has 4 keys for the 4 datasets
    if file.filename.endswith('.npz'):
        file_stream = io.BytesIO(file.read())
        data = np.load(file_stream)
    else:
        return jsonify({"Invalid Data": "Invalid file"}), 402

    # Obtain each data split
    x_train = data["x_train"]
    x_test = data["x_test"]
    y_train = data["y_train"]
    y_test = data["y_test"]

    # Normalize the data
    x_train, x_test = x_train / 255.0, x_test / 255.0

    # One-hot encode the labels
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)
    
    # Save the processed data into separate .npy files
    data_path = os.path.join(data_volume, dataset_name)
    os.makedirs(data_path, exist_ok=True)
    np.save(os.path.join(data_path, 'x_train.npy'), x_train)
    np.save(os.path.join(data_path, 'x_test.npy'), x_test)
    np.save(os.path.join(data_path, 'y_train.npy'), y_train)
    np.save(os.path.join(data_path, 'y_test.npy'), y_test)

    message = {
        'x_train': x_train.shape,
        'x_test': x_test.shape,
        'y_train': y_train.shape,
        'y_test': x_test.shape,
    }
    return message


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)