from flask import Flask, render_template, request, Response
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Serve the HTML file
@app.route("/")
def index():
    return render_template('index.html')


# Define the base URLs for the three Flask services
SERVICE_1_BASE_URL = "http://localhost:5001"
SERVICE_2_BASE_URL = "http://localhost:5002"
SERVICE_3_BASE_URL = "http://localhost:5003"

@app.route('/process/<path:url>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_service1(url):
    return proxy_request(SERVICE_1_BASE_URL, url)

@app.route('/train/<path:url>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_service2(url):
    return proxy_request(SERVICE_2_BASE_URL, url)

@app.route('/inference/<path:url>', methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy_service3(url):
    return proxy_request(SERVICE_3_BASE_URL, url)

def proxy_request(base_url, url):
    downstream_url = f"{base_url}/{url}"
    
    # Prepare files as a dictionary
    files = {key: (f.filename, f.stream, f.content_type) for key, f in request.files.items()}
    
    response = requests.request(
        method=request.method,
        url=downstream_url,
        headers={key: value for key, value in request.headers if key.lower() != 'host'},
        params=request.args,
        data=request.form,
        cookies=request.cookies,
        files=files,  # Correctly formatted files
        allow_redirects=False
    )
    
    excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
    headers = [(name, value) for (name, value) in response.raw.headers.items()
               if name.lower() not in excluded_headers]

    return Response(response.content, response.status_code, headers)



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
