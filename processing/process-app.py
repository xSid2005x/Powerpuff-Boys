import os
import io
import json
import numpy as np
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS
from sklearn.model_selection import train_test_split
from keras.utils import to_categorical
import zipfile
import cv2
import shutil

# Load configurations from JSON file
with open("config/config.json", "r") as f:
    config = json.load(f)

data_folder = config["data_volume"]  # Directory to save processed data
split_ratio = config["split_ratio"]  # Ratio to split data into train and test sets
input_shape = tuple(config['input_shape'])  # Desired shape of input data (should be (28, 28, 1) for grayscale)

# Setup logging to track processing
logging.basicConfig(level=logging.INFO)

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if file is provided in the request
    if 'dataset_file' not in request.files:
        return jsonify({"Missing Data": "File field missing"}), 401

    file = request.files['dataset_file']
    if file.filename == '' or not file:
        return jsonify({"Invalid Data": "Invalid file"}), 402

    # Get dataset name from the request
    dataset_name = request.form.get('dataset_name')
    if not dataset_name:
        return jsonify({"Missing Data": "Name missing"}), 401

    try:
        # Process the uploaded data
        message = process_data(file, dataset_name)
    except Exception as e:
        logging.error(f"Error processing data: {e}")
        return jsonify({"Error": str(e)}), 500
    finally:
        # Ensure temporary directory is cleaned up
        cleanup_tmp_directory()

    return jsonify(message), 200

def process_data(file, dataset_name):
    # Determine the file extension to decide processing method
    file_ext = os.path.splitext(file.filename)[1]

    if file_ext == '.npz' or file_ext == '.npy':
        x_train, x_test, y_train, y_test = handle_np_file(file, file_ext)
    elif file_ext == '.zip':
        x_train, x_test, y_train, y_test = handle_zip_file(file)
    else:
        raise ValueError("Unsupported file format")

    # Find the maximum pixel value in the training and testing data
    max_pixel_value = max(np.max(x_train), np.max(x_test))

    # Normalize image data to the range [0, 1]
    x_train, x_test = x_train / max_pixel_value, x_test / max_pixel_value

    # One-hot encode labels for classification tasks
    y_train = to_categorical(y_train)
    y_test = to_categorical(y_test)

    # Log the shapes of the processed data
    logging.info(f"x_train shape: {x_train.shape}")
    logging.info(f"x_test shape: {x_test.shape}")
    logging.info(f"y_train shape: {y_train.shape}")
    logging.info(f"y_test shape: {y_test.shape}")

    # Save the processed data into separate .npy files
    data_path = os.path.join(data_folder, dataset_name)
    os.makedirs(data_path, exist_ok=True)
    np.save(os.path.join(data_path, 'x_train.npy'), x_train)
    np.save(os.path.join(data_path, 'x_test.npy'), x_test)
    np.save(os.path.join(data_path, 'y_train.npy'), y_train)
    np.save(os.path.join(data_path, 'y_test.npy'), y_test)

    return {
        'x_train': x_train.shape,
        'x_test': x_test.shape,
        'y_train': y_train.shape,
        'y_test': y_test.shape,
    }

def handle_np_file(file, file_ext):
    """Process .npz or .npy file and return train and test datasets."""
    file_stream = io.BytesIO(file.read())
    
    # Check if it's a .npz or .npy file
    if file_ext == '.npz':
        data = np.load(file_stream)
    elif file_ext == '.npy':
        data = np.load(file_stream, allow_pickle=True).item()
    
    x_train, x_test, y_train, y_test = check_and_split_data(data)
    x_train, x_test = reshape_data(x_train), reshape_data(x_test)

    return x_train, x_test, y_train, y_test

def check_and_split_data(data):
    """Check for existing splits or perform a split if necessary."""
    # For .npz files, data is a dictionary-like object, use dictionary indexing
    if isinstance(data, dict) or isinstance(data, np.lib.npyio.NpzFile):
        if "x_train" in data and "x_test" in data and "y_train" in data and "y_test" in data:
            x_train = data["x_train"]
            x_test = data["x_test"]
            y_train = data["y_train"]
            y_test = data["y_test"]
        else:
            x = data["x"]
            y = data["y"]
            x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=split_ratio)
    else:
        raise ValueError("Unexpected data format. Expected dictionary-like object for .npz files.")

    validate_data(x_train, x_test, y_train, y_test)
    return x_train, x_test, y_train, y_test

def handle_zip_file(file):
    """Process .zip file containing images and return train and test datasets."""
    extract_path = "tmp"  # Directory to extract the zip file
    if not os.path.exists(extract_path):
        os.makedirs(extract_path)
    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(extract_path)

    # Find and process all image files in the extracted directory
    image_files = [os.path.join(root, file) for root, dirs, files in os.walk(extract_path) for file in files if file.endswith(('png', 'jpg', 'jpeg'))]
    
    if not image_files:
        raise ValueError("No image files found in the zip archive.")

    images = []
    labels = []
    for image_file in image_files:
        try:
            # Read and process image file
            img = cv2.imread(image_file, cv2.IMREAD_GRAYSCALE)
            img = cv2.resize(img, input_shape[:2])  # Resize to (28, 28)

            # Ensure correct shape: (28, 28, 1)
            img = img[:, :, np.newaxis]  # Add the channel dimension to make it (28, 28, 1)
            
            images.append(img)
            labels.append(get_label_from_filename(image_file))
        except Exception as e:
            logging.error(f"Error processing file {image_file}: {e}")

    if not images or not labels:
        raise ValueError("No images processed or no labels extracted")

    images = np.array(images)
    labels = np.array(labels)
    
    # Convert labels to integers if necessary
    if not np.issubdtype(labels.dtype, np.integer):
        unique_labels = np.unique(labels)
        label_to_int = {label: i for i, label in enumerate(unique_labels)}
        labels = np.array([label_to_int[label] for label in labels])

    # Split data
    x_train, x_test, y_train, y_test = train_test_split(images, labels, test_size=split_ratio)
    
    return x_train, x_test, y_train, y_test

def get_label_from_filename(filename):
    """Extract label from directory structure or filename."""
    # Try to extract label from the directory structure
    directory_label = os.path.basename(os.path.dirname(filename))
    
    # If directory name is not empty, use it as the label
    if directory_label:
        return directory_label
    
    # Otherwise, extract label from the filename
    return os.path.basename(filename).split('_')[0]

def validate_data(x_train, x_test, y_train, y_test):
    """Validate that all required data arrays are present."""
    if x_train is None or x_test is None or y_train is None or y_test is None:
        raise ValueError("Missing keys in data file")

def reshape_data(data):
    """Resize and reshape data to match the input shape."""
    resized_data = []
    for img in data:
        # Ensure the image data is in uint8 format for OpenCV compatibility
        if img.dtype != np.uint8:
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

        # Resize each image to match the first two dimensions of input_shape
        resized_img = cv2.resize(img, input_shape[:2])

        # Ensure the resized image matches the input shape (28, 28, 1)
        if len(resized_img.shape) == 2:  # if it's grayscale, add the channel dimension
            resized_img = resized_img[:, :, np.newaxis]

        resized_data.append(resized_img)

    return np.array(resized_data)

def cleanup_tmp_directory():
    """Remove the temporary directory and its contents."""
    if os.path.exists("tmp"):
        shutil.rmtree("tmp")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
