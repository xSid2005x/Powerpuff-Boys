// Function to load dataset names from the server
function listData() {
    const dataSelect = document.getElementById('data_folder');
    dataSelect.innerHTML = '';
    const option = document.createElement('option');
    option.disabled = true;
    option.selected = true;
    option.textContent = 'Select Dataset';
    dataSelect.appendChild(option);
    fetch('http://power-puff.boys/train/list_data')
        .then(response => response.json())
        .then(data => {
            data.datasets.forEach(dataset => {
                const option = document.createElement('option');
                option.value = dataset;
                option.textContent = dataset;
                dataSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading folders:', error);
        });
}

// Function to load models from the server
function listModel() {
    const modelSelect = document.getElementById('model_folder');
    modelSelect.innerHTML = '';
    const option = document.createElement('option');
    option.disabled = true;
    option.selected = true;
    option.textContent = 'Select Model';
    modelSelect.appendChild(option);
    fetch('http://power-puff.boys/inference/list_models')
        .then(response => response.json())
        .then(data => {
            data.models.forEach(model => {
                const option = document.createElement('option');
                option.value = model;
                option.textContent = model;
                modelSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error('Error loading folders:', error);
        });
}


// Checks for clicks on other services
document.querySelectorAll('.service').forEach(service => {
    service.addEventListener('click', function() {

        // Set clicked service to active
        document.querySelectorAll('.service').forEach(t => t.classList.remove('active'));
        service.classList.add('active');
        const serviceType = service.getAttribute('service-type');
        
        // Show content of active service
        document.querySelectorAll('.service-content').forEach(content => {
            content.style.display = 'none';
        });
        document.getElementById(serviceType).style.display = 'block';

        // Specific service logic
        if (serviceType === 'training') {
            listData();
        } else if (serviceType === 'inference') {
            listModel();
        }
    });
});

document.getElementById('uploadDataset').addEventListener('submit', function(event) {
    event.preventDefault();

    document.getElementById('processLoading').style.display = 'block';
    document.getElementById('processingOutput').style.display = 'none';

    const formData = new FormData(this);
    fetch(this.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('processLoading').style.display = 'none';
        document.getElementById('xtrainOutput').textContent = `x_train: (${data.x_train})`;
        document.getElementById('xtestOutput').textContent = `x_test: (${data.x_test})`;
        document.getElementById('ytrainOutput').textContent = `y_train: (${data.y_train})`;
        document.getElementById('ytestOutput').textContent = `y_test: (${data.y_test})`;
        document.getElementById('processingOutput').style.display = 'block';
    })
    .catch(error => {
        document.getElementById('processLoading').style.display = 'none';
        alert('Error uploading dataset');
        console.error('Error:', error);
    });
});

// Handle form submission for the training section
document.getElementById('trainModel').addEventListener('submit', function(event) {
    event.preventDefault();

    document.getElementById('trainLoading').style.display = 'block';
    document.getElementById('trainingOutput').style.display = 'none';


    const dataset = document.getElementById('data_folder').value;
    const modelName = document.getElementById('model_name').value;

    const data = {
        'data_folder': dataset,
        'model_name': modelName
    };

    fetch(this.action, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        // Process the response and display the results
        document.getElementById('trainLoading').style.display = 'none';
        document.getElementById('accuracyOutput').textContent = `Accuracy: ${data.accuracy}%`;
        document.getElementById('lossOutput').src = `data:image/png;base64,${data.loss}`;
        document.getElementById('trainingOutput').style.display = 'block';
    })
    .catch(error => {
        // Handle any errors that occur during the request
        document.getElementById('trainLoading').style.display = 'none';
        alert('Error during training');
        console.error('Error:', error);
    });
});


document.getElementById('makeInference').addEventListener('submit', function(event) {
    event.preventDefault();

    document.getElementById('inferLoading').style.display = 'block';
    document.getElementById('inferenceOutput').style.display = 'none';

    const formData = new FormData(this);
    fetch(this.action, {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('inferLoading').style.display = 'none';
        document.getElementById('predictOutput').textContent = `Predicted Digit: ${data.prediction}`
        document.getElementById('inferenceOutput').style.display = 'block';
    })
    .catch(error => {
        document.getElementById('inferLoading').style.display = 'none';
        alert('Error uploading dataset');
        console.error('Error:', error);
    });
});