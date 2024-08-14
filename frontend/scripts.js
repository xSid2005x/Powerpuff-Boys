// Function to load dataset names from the server
function listData() {
    const dataSelect = document.getElementById('data_folder');
    dataSelect.innerHTML = '';
    const option = document.createElement('option');
    option.disabled = true;
    option.selected = true;
    option.textContent = 'Select Dataset';
    dataSelect.appendChild(option);
    fetch('http://localhost:5002/list_data')
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

// Function to ensure the default section is shown
function showDefaultSection() {
    const defaultService = document.querySelector('.service[service-type="data-processing"]');
    const defaultContent = document.getElementById('data-processing');

    // Set the default service as active
    document.querySelectorAll('.service').forEach(t => t.classList.remove('active'));
    defaultService.classList.add('active');

    // Show the default content
    document.querySelectorAll('.service-content').forEach(content => {
        content.style.display = 'none';
        content.style.opacity = 0;
    });
    defaultContent.style.display = 'block';
    defaultContent.style.opacity = 1;
}

// Call showDefaultSection on window load
window.onload = showDefaultSection;

// Update file name display when a file is chosen
document.getElementById('dataset_file').addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : 'No file chosen';
    document.getElementById('fileName').textContent = fileName;
});

// Function to load models from the server
function listModel() {
    const modelSelect = document.getElementById('model_folder');
    modelSelect.innerHTML = '';
    const option = document.createElement('option');
    option.disabled = true;
    option.selected = true;
    option.textContent = 'Select Model';
    modelSelect.appendChild(option);
    fetch('http://localhost:5003/list_models')
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
        
        // Hide the currently visible content
        document.querySelectorAll('.service-content').forEach(content => {
            content.style.opacity = 0;
            setTimeout(() => {
                content.style.display = 'none';
            }, 500); // Delay to match the fade-out transition
        });

        // Show the newly selected content with a fade-in effect
        const newContent = document.getElementById(serviceType);
        setTimeout(() => {
            newContent.style.display = 'block';
            newContent.style.opacity = 1;
        }, 500); // Delay to match the fade-in transition

        // Specific service logic
        if (serviceType === 'training') {
            listData();
        } else if (serviceType === 'inference') {
            listModel();
        }
    });
});

// Handle form submission for the data processing section
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

// Handle form submission for the inference section
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
        document.getElementById('predictOutput').textContent = `classification: ${data.prediction}`;
        document.getElementById('confidenceOutput').textContent = `Confidence Level: ${(data.confidence * 100).toFixed(2)}%`; // Display confidence level
        document.getElementById('inferenceOutput').style.display = 'block';
    })
    .catch(error => {
        document.getElementById('inferLoading').style.display = 'none';
        alert('Error during inference');
        console.error('Error:', error);
    });
});

// Tab switching logic
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', function() {
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));

        // Hide all tab contents
        document.querySelectorAll('.tab-content').forEach(content => {
            content.style.display = 'none';
        });

        // Add active class to the clicked tab
        tab.classList.add('active');

        // Show the corresponding tab content
        const tabType = tab.getAttribute('tab-type');
        document.getElementById(tabType).style.display = 'block';

        // Clear the opposite tab's input and output
        if (tabType === 'upload-tab') {
            clearCanvas(); // Clear the drawing canvas
            document.getElementById('fileNameImage').textContent = 'No file chosen';
            document.getElementById('imagePreview').style.display = 'none';
            document.getElementById('test_image').value = ''; // Clear the file input
        } else if (tabType === 'draw-tab') {
            clearCanvas(); // Clear the drawing canvas
            document.getElementById('fileNameImage').textContent = 'No file chosen';
            document.getElementById('imagePreview').style.display = 'none';
            document.getElementById('test_image').value = ''; // Clear the file input
        }
    });
});

// Update file name display when a file is chosen in the Inference section
document.getElementById('test_image').addEventListener('change', function() {
    const fileName = this.files[0] ? this.files[0].name : 'No file chosen';
    document.getElementById('fileNameImage').textContent = fileName;

    // Display the image preview
    const file = this.files[0];
    const reader = new FileReader();
    reader.onload = function(e) {
        const imagePreview = document.getElementById('imagePreview');
        imagePreview.src = e.target.result;
        imagePreview.style.display = 'block';
    }
    reader.readAsDataURL(file);
});

// Function to update file name display when a file is chosen
function updateFileName(inputElement, fileNameElementId) {
    const fileName = inputElement.files[0] ? inputElement.files[0].name : 'No file chosen';
    document.getElementById(fileNameElementId).textContent = fileName;
}

// Attach event listeners to both file inputs
document.getElementById('dataset_file').addEventListener('change', function() {
    updateFileName(this, 'fileNameDataset');
});

document.getElementById('test_image').addEventListener('change', function() {
    updateFileName(this, 'fileNameImage');
});

// Drawing on the canvas
const canvas = document.getElementById('drawingCanvas');
const ctx = canvas.getContext('2d');
let drawing = false;

canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mousemove', draw);
document.getElementById('clearCanvas').addEventListener('click', clearCanvas);
document.getElementById('uploadDrawing').addEventListener('click', uploadDrawing);

function startDrawing(event) {
    drawing = true;
    ctx.beginPath(); // Start a new path
    draw(event); // Draw the initial point where the mouse is pressed down
}

function stopDrawing() {
    drawing = false;
    ctx.beginPath(); // Reset the path so it doesn't connect with the previous drawing
}

function draw(event) {
    if (!drawing) return;

    // Get the mouse position relative to the canvas
    const rect = canvas.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;

    ctx.lineWidth = 10;
    ctx.lineCap = 'round';
    ctx.strokeStyle = 'white';

    ctx.lineTo(x, y);
    ctx.stroke();
    ctx.beginPath();
    ctx.moveTo(x, y);
}

function clearCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
}

function uploadDrawing() {
    canvas.toBlob(function(blob) {
        const file = new File([blob], "drawing.png", { type: "image/png" });

        // Set the file input to the generated file from the canvas drawing
        const dataTransfer = new DataTransfer();
        dataTransfer.items.add(file);
        document.getElementById('test_image').files = dataTransfer.files;

        alert('Drawing uploaded as image!');
    });
}



