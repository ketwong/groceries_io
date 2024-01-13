from flask import Flask, request, render_template, jsonify, abort
import os
import base64
import requests
import logging
import socket
from PIL import Image, ImageOps
import io
import time
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/results.db')
db = SQLAlchemy(app)
swagger = Swagger(app)

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

class ImageResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    count = db.Column(db.Integer, nullable=False)
    object_name = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<ImageResult {self.count}, {self.object_name}>'

with app.app_context():
    db.create_all()

def get_size_in_mb(file_storage):
    """
    Calculate the size of an uploaded file in megabytes.
    """
    file_storage.seek(0, os.SEEK_END)  # Go to the end of the file
    size = file_storage.tell() / (1024 * 1024)  # Get the size in MB
    file_storage.seek(0)  # Seek back to the start of the file
    return size

from PIL import Image, ImageOps

def resize_image(image, max_size=(400, 300), quality=70):
    """
    Resize and compress the image more aggressively.
    :param image: Image file.
    :param max_size: Maximum width and height.
    :param quality: Quality of the resized image, lower means more compression.
    :return: Resized and compressed image.
    """
    im = Image.open(image)
    im = ImageOps.exif_transpose(im)  # Correct the orientation if needed
    im.thumbnail(max_size, Image.Resampling.LANCZOS)  # Resize the image
    buffer = io.BytesIO()
    im.save(buffer, format='JPEG', quality=quality)  # Compress the image
    buffer.seek(0)
    return buffer

@app.route('/')
def index():
    app.logger.info('Rendering index page')
    return render_template('index.html')

@app.route('/dev')
def test():
    return render_template('dev.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    file upload
    ---
    tags:
        - image processing
    consumes:
        - multipart/form-data
    parameters:
        - in: formData
          name: image
          type: file
          required: true
          description: The image to upload.
    responses:
        200:
            description: Successful response
    """
    start_time = time.time()  # Start time measurement

    app.logger.info('START - Received upload request')

    if 'image' not in request.files:
        app.logger.error('No image part in the request')
        elapsed_time = time.time() - start_time
        app.logger.info(f'Job ended with errors in {elapsed_time:.2f} seconds')
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        app.logger.error('No selected file')
        elapsed_time = time.time() - start_time
        app.logger.info(f'Job ended with errors in {elapsed_time:.2f} seconds')
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        app.logger.info('Valid image received for processing')

        # Calculate the original image size in MB
        file.seek(0, os.SEEK_END)
        original_size = file.tell() / (1024 * 1024)
        file.seek(0)
        app.logger.info(f'Original image size: {original_size:.2f} MB')

        # Resize and compress image
        resized_image = resize_image(file, max_size=(800, 600), quality=85)

        # Calculate the resized image size in MB
        resized_image.seek(0, os.SEEK_END)
        resized_size = resized_image.tell() / (1024 * 1024)
        resized_image.seek(0)
        app.logger.info(f'Resized image size: {resized_size:.2f} MB')

        base64_image = base64.b64encode(resized_image.read()).decode('utf-8')
        app.logger.info('Image resized, compressed, and encoded to base64')

        api_response = call_vision_api(base64_image)
        app.logger.info('Received response from vision API')
        app.logger.info('The result: ' + api_response)

        # Parse the API response
        try:
            amount, grocery_item = api_response.split(', ')
            amount = int(amount)  # Convert amount to an integer
        except ValueError:
            app.logger.error('Error parsing the API response')
            return jsonify({'error': 'Error parsing the API response'}), 500
        
        # Add result to the database
        new_result = ImageResult(count=amount, object_name=grocery_item)
        db.session.add(new_result)
        db.session.commit()
        app.logger.info(f'Added new entry for {grocery_item} with count: {amount}')

        # Structured output
        structured_output = {
            "amount": amount,
            "groceryItem": grocery_item
        }

        app.logger.info(f'Processed Output: {structured_output}')

        elapsed_time = time.time() - start_time
        app.logger.info(f'END - Job completed in {elapsed_time:.2f} seconds')

        return jsonify(structured_output)
    else:
        app.logger.error('Invalid file type')
        elapsed_time = time.time() - start_time
        app.logger.info(f'Job ended with errors in {elapsed_time:.2f} seconds')
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
              "text": "Determine what is in the image, how many objects in the image in numbers? name of the object i.e. 'Banana', 'Orange', 'Bread' etc... focus the object located at the center at all times. The result should output as <number>, <objectName> or example like 1, Car"
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

@app.route('/get-result', methods=['GET'])
def get_result():
    """
    Retrieve a result or all results from the database
    ---
    tags:
      - results
    parameters:
      - in: query
        name: id
        type: integer
        required: false
        description: The ID of the specific result to retrieve
    responses:
      200:
        description: A list of results or a single result
      404:
        description: Not found (if no result is found with the given ID)
    """
    result_id = request.args.get('id')

    if result_id:
        # Retrieve a specific result by ID
        result = ImageResult.query.get(result_id)
        if result:
            return jsonify({'id': result.id, 'count': result.count, 'object_name': result.object_name})
        else:
            return jsonify({'error': 'Result not found'}), 404
    else:
        # Retrieve all results
        results = ImageResult.query.all()
        results_data = [{'id': result.id, 'count': result.count, 'object_name': result.object_name} for result in results]
        return jsonify(results_data)

@app.route('/update-result/<int:result_id>', methods=['PUT'])
def update_result(result_id):
    """
    Update a result in the database
    ---
    tags:
      - results
    parameters:
      - in: path
        name: result_id
        type: integer
        required: true
        description: The ID of the result to update
      - in: body
        name: body
        required: true
        schema:
          id: Result
          required:
            - count
            - object_name
          properties:
            count:
              type: integer
              description: The updated count
            object_name:
              type: string
              description: The updated object name
    responses:
      200:
        description: Result updated successfully
      404:
        description: Not found (if no result is found with the given ID)
    """
    result = ImageResult.query.get(result_id)
    if not result:
        return jsonify({'error': 'Result not found'}), 404

    data = request.get_json()  # Fetch the JSON data from the request

    if 'count' in data:
        result.count = data['count']
    if 'object_name' in data:
        result.object_name = data['object_name']

    db.session.commit()
    return jsonify({'message': 'Updated successfully'})

@app.route('/delete-result/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    """
    Delete a result from the database
    ---
    tags:
      - results
    parameters:
      - in: path
        name: result_id
        type: integer
        required: true
        description: The ID of the result to delete
    responses:
      200:
        description: Result deleted successfully
      404:
        description: Not found (if no result is found with the given ID)
    """
    result = ImageResult.query.get(result_id)
    if not result:
        return jsonify({'error': 'Result not found'}), 404

    db.session.delete(result)
    db.session.commit()
    return jsonify({'message': f'Record with id {result_id} deleted successfully'})

if __name__ == '__main__':
    app.run(debug=True)
