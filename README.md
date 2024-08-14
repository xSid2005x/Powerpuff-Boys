# AI Solution Deployment Using Flask, Docker, and Kubernetes

## Overview

This project demonstrates the deployment of an AI-based Handwritten Digits Recognition system using Flask, Docker, and Kubernetes. The system is designed to handle data processing, model training, and inference tasks, all orchestrated using Kubernetes and accessible via a web frontend. Each component is containerized using Docker to ensure consistency and scalability.

## Table of Contents

1. [System Architecture](#system-architecture)
2. [Project Structure](#project-structure)
3. [Configurations](#configurations)
   - [ConfigMap](#configmap)
   - [Volumes](#volumes)
4. [Building Docker Images](#building-docker-images)
5. [Kubernetes Deployment](#kubernetes-deployment)
   - [Deployment Instructions](#deployment-instructions)
6. [Detailed Service Descriptions](#detailed-service-descriptions)
   - [Web Frontend](#web-frontend)
   - [Training](#training)
   - [Processing](#processing)
   - [Inference](#inference)
7. [Troubleshooting](#troubleshooting)

## System Architecture

The system is composed of several key components that work together to provide a full-fledged AI solution:

- **Flask API Services:** These are the core backend services responsible for processing data, training models, and performing inference. Each service is containerized to ensure isolated and consistent environments.

- **Docker:** Docker is used to package each Flask service into containers, making them portable and easy to deploy across different environments.

- **Kubernetes:** Kubernetes orchestrates the deployment, scaling, and networking of the Docker containers. It ensures that the services are highly available and can scale based on demand.

- **Ingress:** Ingress is used to manage external access to the services, providing a single entry point to the system.

- **Persistent Storage:** Kubernetes Persistent Volumes are used to store datasets and trained models, ensuring data persistence across pod restarts.

## Project Structure

The project is organized as follows:

```
frontend/
  ├── Dockerfile
  ├── index.html
  ├── scripts.js
  ├── styles.css
  ├── favicon.ico
  ├── loading-icon.gif
  └── web-deployment.yaml

inference/
  ├── Dockerfile
  ├── inference-app.py
  ├── requirements.txt
  └── inference-deployment.yaml

processing/
  ├── Dockerfile
  ├── process-app.py
  ├── requirements.txt
  └── process-deployment.yaml

training/
  ├── Dockerfile
  ├── train-app.py
  ├── requirements.txt
  └── train-deployment.yaml

config/
  └── config.json

kubernetes/
  ├── configmap.yaml
  ├── volumes.yaml
  ├── ingress.yaml
  └── ingress.yaml
```

- **Frontend:** Contains the web interface for interacting with the system.
- **Inference, Processing, Training:** Contains the backend services responsible for inference, data processing, and model training.
- **Config:** Contains the configuration files.
- **Kubernetes:** Contains Kubernetes configuration files, such as ConfigMaps, Volumes, and Ingress settings.

## Configurations

### ConfigMap

A ConfigMap is used to store the configuration details for all services. This includes paths to data and model volumes, model architecture, training parameters, and other essential settings. The ConfigMap ensures that all services use consistent configuration data.

**Key Fields in `config.json`:**

- **`data_volume:`** Path to the volume where datasets are stored.
- **`model_volume:`** Path to the volume where models are stored.
- **`input_shape:`** Input shape of the data (e.g., `[28, 28, 1]` for grayscale images).
- **`split_ratio:`** Ratio for splitting data into training and testing sets.
- **`batch_size:`** Batch size used during model training.
- **`epochs:`** Number of epochs for model training.
- **`lr:`** Learning rate for the optimizer.
- **`architecture:`** List defining the layers and architecture of the neural network.

### Volumes

Persistent Volumes are defined in the `volumes.yaml` file. These volumes store datasets and trained models, ensuring data persistence across container restarts. The Persistent Volume Claims (PVCs) request storage from Kubernetes to be mounted into the containers.

**Key Components:**

- **PersistentVolume (PV):** Specifies the physical storage used for datasets and models.
- **PersistentVolumeClaim (PVC):** Requests storage for use within the containers.

## Building Docker Images

Each service is containerized using Docker. To build and push Docker images, follow these steps:

1. **Navigate to the service directory:**

   ```bash
   cd frontend
   ```

2. **Build the Docker image:**

   ```bash
   docker build -t yourdockerhubusername/frontend:latest .
   ```

3. **Push the Docker image to Docker Hub:**

   ```bash
   docker push yourdockerhubusername/frontend:latest
   ```

4. **Repeat the above steps for the `inference`, `processing`, and `training` services.**

## Kubernetes Deployment

### Deployment Instructions

To deploy the project using Kubernetes, follow these steps:

1. **Delete any existing Minikube setup (start fresh):**

   ```bash
   minikube delete
   ```

2. **Start Minikube:**

   ```bash
   minikube start
   ```

3. **Enable Ingress addon in Minikube:**

   ```bash
   minikube addons enable ingress
   ```

4. **Wait for the Ingress pods to be running:**

   ```bash
   kubectl get pods -n ingress-nginx
   ```

   Ensure that the Ingress controller is running. Other pods may not need to be running.

5. **Apply all Kubernetes configurations:**

   ```bash
   kubectl apply -f .
   ```

   This command applies all YAML files in the current directory, deploying the services, ConfigMaps, and Volumes.

6. **Wait for the pods to be fully up and running:**

   Pods can take a while to start. Monitor their status with:

   ```bash
   kubectl get pods
   ```

7. **Start Minikube tunnel:**

   ```bash
   minikube tunnel
   ```

8. **Modify your `/etc/hosts` file:**

   Add the following line to your `/etc/hosts` file to route traffic to the Minikube IP:

   ```plaintext
   127.0.0.1 power-puff.boys
   ```

   This allows you to access the application using `http://power-puff.boys/`.

9. **Access the web application:**

   Open your web browser and navigate to:

   ```plaintext
   http://power-puff.boys/
   ```

## Detailed Service Descriptions

### Web Frontend

- **Functionality:** 
  - The web frontend allows users to upload datasets, train models, and perform inference.
  - The UI is built using HTML, CSS, and JavaScript, and it communicates with the backend services via REST API calls.

- **Deployment:** 
  - The web frontend is deployed using Kubernetes, and it interacts with the backend services via the Ingress controller.

- **Files:**
  - `index.html`: Main HTML file for the frontend.
  - `styles.css`: Styling for the frontend.
  - `scripts.js`: JavaScript logic for interacting with backend services.

### Training

- **Service:** 
  - Manages model training.
  - More detailed information is provided in the `training/README.md`.

### Processing

- **Service:** 
  - Handles dataset processing.
  - More detailed information is provided in the `processing/README.md`.

### Inference

- **Service:** 
  - Performs inference using the trained models.
  - More detailed information is provided in the `inference/README.md`.

## Troubleshooting

If you encounter issues, here are some troubleshooting steps:

- **Check Pod Status:**
  - Use `kubectl get pods` to see the status of your pods.
  
- **View Logs:**
  - Use `kubectl logs <pod-name>` to view logs and diagnose issues.

- **Ensure Docker Images Are Up-to-Date:**
  - Rebuild and push Docker images if there are changes.
