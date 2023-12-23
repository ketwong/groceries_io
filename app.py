from flask import Flask, request, render_template, jsonify
import os
import base64
import requests
import logging
import socket
from PIL import Image
import io

app = Flask(__name__)

# Setup logging with time and date format
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Check API Key
api_key = os.environ.get("OPENAI_API_KEY")
if not api_key:
    logging.error("OpenAI API key is missing or not set in the environment.")
    exit(1)  # Exit if the API key is not set

# Test OpenAI API Reachability
def test_openai_api_reachability():
    hostname = "api.openai.com"
    try:
        host = socket.gethostbyname(hostname)
        s = socket.create_connection((host, 80), 2)
        logging.info(f"Successfully reached {hostname}")
        return True
    except:
        logging.error(f"Failed to reach {hostname}")
        return False

test_openai_api_reachability()

def get_size_in_mb(file_storage):
    """
    Calculate the size of an uploaded file in megabytes.
    """
    file_storage.seek(0, os.SEEK_END)  # Go to the end of the file
    size = file_storage.tell() / (1024 * 1024)  # Get the size in MB
    file_storage.seek(0)  # Seek back to the start of the file
    return size

def resize_image(image, max_size=(800, 600), quality=85):
    """
    Resize and compress the image.
    :param image: Image file.
    :param max_size: Maximum width and height.
    :param quality: Quality of the resized image.
    :return: Resized and compressed image.
    """
    im = Image.open(image)
    im.thumbnail(max_size)
    buffer = io.BytesIO()
    im.save(buffer, format='JPEG', quality=quality)
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    app.logger.info('Rendering index page')
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    app.logger.info('START - Received upload request')

    if 'image' not in request.files:
        app.logger.error('No image part in the request')
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        app.logger.error('No selected file')
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        app.logger.info('Valid image received for processing')

        # Calculate the original image size in MB
        file.seek(0, os.SEEK_END)  # Go to the end of the file
        original_size = file.tell() / (1024 * 1024)  # Get the size in MB
        file.seek(0)  # Seek back to the start of the file
        app.logger.info(f'Original image size: {original_size:.2f} MB')

        # Resize and compress image
        resized_image = resize_image(file, max_size=(800, 600), quality=85)

        # Calculate the resized image size in MB
        resized_image.seek(0, os.SEEK_END)  # Go to the end of the file
        resized_size = resized_image.tell() / (1024 * 1024)  # Get the size in MB
        resized_image.seek(0)  # Seek back to the start of the file
        app.logger.info(f'Resized image size: {resized_size:.2f} MB')

        base64_image = base64.b64encode(resized_image.read()).decode('utf-8')
        app.logger.info('Image resized, compressed, and encoded to base64')

        content = call_vision_api(base64_image)
        app.logger.info('Received response from vision API')
        app.logger.info('The result: ' + content)
        app.logger.info('END - Job completed')
        return jsonify({'content': content})
    else:
        app.logger.error('Invalid file type')
        return jsonify({'error': 'Invalid file type'}), 400

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def call_vision_api(base64_image):
    headers = {
      "Content-Type": "application/json",
      "Authorization": f"Bearer {api_key}"
    }
    payload = {
      "model": "gpt-4-vision-preview",
      "messages": [
        {
          "role": "user",
          "content": [
            {
              "type": "text",
              "text": "Determine what is in the image with the object name only, i.e. 'Banana', 'Orange', 'Bread' etc... focus the object located at the center at all times."
            },
            {
              "type": "image_url",
              "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low"
              }
            }
          ]
        }
      ],
      "max_tokens": 300
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
    return response.json()['choices'][0]['message']['content']

if __name__ == '__main__':
    app.run(debug=True)
