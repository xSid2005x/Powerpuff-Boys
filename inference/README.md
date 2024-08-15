# Inference Service

## Overview

The `inference` service is a Flask-based API that performs image classification tasks using a pre-trained Convolutional Neural Network (CNN). This service loads a trained model, preprocesses an input image, and returns both the predicted class and its associated confidence level.

## Project Structure

```
inference/
├── Dockerfile
├── inference-app.py
├── requirements.txt
inference-deployment.yaml
```

- **`Dockerfile:`** Defines the Docker image for the inference service.
- **`inference-app.py:`** The main Flask application for handling inference requests.
- **`requirements.txt:`** Python dependencies required by the service.
- **`inference-deployment.yaml:`** Kubernetes deployment configuration for the inference service (located outside the folder).

## Service Functionality

- **Model Loading:** The service dynamically loads a pre-trained model from a model chosen from the Model Volume.
- **Image Preprocessing:** Images are converted to grayscale, resized, and normalized to match the input requirements of the model.
- **Prediction:** The service returns the class with the highest predicted probability and the associated confidence level.

## Integration and Outputs

When merged with the other files and deployed as part of the full system:

- **Model Inference Page:** The user interface (UI) allows users to either upload an image file or draw a digit directly on the website.
- **Prediction Output:** The page displays the predicted digit along with the confidence level of the prediction.
- **Model Usage:** The inference service uses the model trained and provided by the `train-app.py` service, ensuring consistency in predictions across the platform.

This setup enables users to interact with the AI model in a straightforward and intuitive way, either by uploading an image or by drawing a digit themselves. The system then predicts the digit and shows how confident it is in that prediction, all integrated seamlessly with the provided HTML, CSS, and JavaScript.
