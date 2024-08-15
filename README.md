# AI Solution Deployment Using Flask, Docker, and Kubernetes

## Overview

This project demonstrates the deployment of an AI-based Handwritten Digits Recognition system using Flask, Docker, and Kubernetes. The system is designed to handle data processing, model training, and inference tasks, all orchestrated using Kubernetes and accessible via a web frontend. Each component is containerized using Docker to ensure consistency and scalability.

## Table of Contents

1. [Folder Structure](#folder-structure)
2. [System Architecture](#system-architecture)
3. [Deployment Instructions](#deployment-instructions)
4. [Configurations](#configurations)
   - [ConfigMap](#configmap)
   - [Volumes](#volumes)
   - [Deployments](#deployments)
   - [Customizing Service Images](#customizing-service-images)
6. [Detailed Service Descriptions](#detailed-service-descriptions)
   - [Web Frontend](#web-frontend)
   - [Training](#training)
   - [Processing](#processing)
   - [Inference](#inference)
7. [Troubleshooting](#troubleshooting)

## Folder Structure

```
/powerpuff-boys
├── frontend
│   ├── css
│   │   └── styles.css
│   ├── images
│   │   ├── background.jpg
│   │   ├── favicon.ico
│   │   ├── loading-icon.gif
│   │   └── logo.png
│   ├── Dockerfile
│   ├── index.html
│   └── script.js
├── inference
│   ├── Dockerfile
│   ├── inference-app.py
│   └── requirements.txt
├── processing
│   ├── Dockerfile
│   ├── process-app.py
│   └── requirements.txt
├── training
│   ├── Dockerfile
│   ├── requirements.txt
│   └── train-app.py
├── configmap.yaml
├── inference-deployment.yaml
├── ingress.yaml
├── process-deployment.yaml
├── train-deployment.yaml
├── volumes.yaml
├── web-deployment.yaml
└── README.md
```

## System Architecture

The system is composed of several key components that work together to provide a full-fledged AI solution. Below is an overview of the system architecture:

![architecture overview](https://github.com/user-attachments/assets/efc09838-7572-4cc9-a3a7-1ca19ee7697b)

### Architecture Overview

At the core of the system, several specialized components are designed to manage different aspects of the AI workflow, from data preprocessing to model inference:

1. **Secret & ConfigMap:**
   - The **ConfigMap** is a centralized configuration manager that stores all essential settings used by the services, such as paths to data and model volumes, model architecture details, and training parameters. This ensures that all services operate with consistent configuration data, enhancing the system's reliability.
   - **Secrets** are used to store and manage sensitive information securely, such as API keys or passwords that the applications require.

2. **Data-Volume & Model-Volume:**
   - **Data-Volume:** This is where the datasets are stored. The processing and training services access this volume to read and write data.
   - **Model-Volume:** This volume stores the trained models. The training service writes models to this volume, while the inference service reads from it to perform predictions.

3. **Train-App, Process-App, Inference-App:**
   - **Train-App:** This application handles the training of machine learning models. It reads data from the Data-Volume, processes it, and stores the trained model in the Model-Volume.
   - **Process-App:** Responsible for preprocessing and preparing the data before it is used for training or inference. It ensures the data is in the correct format and structure required by the models.
   - **Inference-App:** This application uses the trained models stored in the Model-Volume to perform predictions on new data. The results are then sent to the Web-App.

4. **Web-App:**
   - The Web-App serves as the user interface, allowing users to interact with the system. Users can upload datasets, initiate model training, and request predictions. The Web-App communicates with the backend services (Train-App, Process-App, Inference-App) via RESTful APIs.

5. **Services (svc):**
   - Kubernetes Services are used to ensure that each application (Train-App, Process-App, Inference-App, Web-App) is reachable within the cluster. These services manage the internal routing of requests between different components, ensuring that they can communicate efficiently and reliably.

6. **Ingress:**
   - The Ingress controller manages external access to the services, providing a single point of entry to the system. It routes incoming requests to the appropriate service within the Kubernetes cluster, ensuring that the system is accessible from outside the cluster.

### How It All Comes Together

The data flows from the Data-Volume through the Process-App, where it is preprocessed and prepared for model training. The Train-App then takes this processed data, trains a machine learning model, and stores the resulting model in the Model-Volume. The Inference-App accesses these stored models to perform predictions on new input data, which are then sent back to the user via the Web-App. This modular approach ensures that each component is specialized and can be independently scaled, updated, or redeployed without affecting the overall system.

## Deployment Instructions

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

## Configurations

### ConfigMap

The ConfigMap is defined in the `configmap.yaml` file. A ConfigMap is used to store the configuration details and ensure consistent configurations for all services. This map will be mounted inside /app/config/config.json for all services.

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

### Deployments

Deployments are defined in the `*-deployment.yaml` file. These deployments store the desired state of the pods like the number of replica sets, their update strategy and what image they will run on each container.

### Customizing Service Images

Each service is containerized into an image using Docker. To edit the services, a new image has to be built and used.

To build and push Docker images, follow these steps:

1. **Navigate to the service directory:**

   ```bash
   cd frontend
   ```

2. **Build and push the Docker image to Docker Hub:**

   ```bash
   docker build -t yourdockerhubusername/frontend:latest .
   docker push yourdockerhubusername/frontend:latest
   ```

3. **Edit deployment file to use new image:**
   
   ```plaintext
   image: yourdockerhubusername/frontend:latest
   ```

4. **Repeat the above steps for the `inference`, `processing`, and `training` services.**

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

## Troubleshooting

If you encounter issues, here are some troubleshooting steps:

- **Check Pod Status:**
  - Use `kubectl get pods` to see the status of your pods.
  
- **View Logs:**
  - Use `kubectl logs <pod-name>` to view logs and diagnose issues.

- **Ensure Docker Images Are Up-to-Date:**
  - Rebuild and push Docker images if there are changes.
