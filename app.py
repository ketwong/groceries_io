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

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/results.db')
db = SQLAlchemy(app)

# Logging configuration function
def configure_logging():
    # Configure the basic parameters for logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            logging.StreamHandler()  # Log to stderr (default)
        ]
    )

    # You can also add additional handlers if needed, e.g., for logging to a file:
    # file_handler = logging.FileHandler('app.log')
    # file_handler.setFormatter(logging.Formatter(
    #     '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    # ))
    # logging.getLogger().addHandler(file_handler)

# Call the function to configure logging
configure_logging()

logger = logging.getLogger()

# API key verification
def verify_api_key():
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logging.error("OpenAI API key is missing or not set in the environment.")
        exit(1)

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
        return f'<ImageResult {self.id} {self.count} {self.object_name}>'

# Initialize the app and create tables
def initialize_app():
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

# Route handlers
@app.route('/')
def index():
    logger.info('Rendering index page')
    return render_template('index.html')

@app.route('/dev')
def dev():
    return render_template('dev.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    start_time = time.time()  # Start time measurement

    logger.info('START - Received upload request')

    if 'image' not in request.files:
        app.logger.error('No image part in the request')
        elapsed_time = time.time() - start_time
        logger.info(f'Job ended with errors in {elapsed_time:.2f} seconds')
        return jsonify({'error': 'No file part'}), 400

    file = request.files['image']
    if file.filename == '':
        app.logger.error('No selected file')
        elapsed_time = time.time() - start_time
        logger.info(f'Job ended with errors in {elapsed_time:.2f} seconds')
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        logger.info('Valid image received for processing')

        # Calculate the original image size in MB
        file.seek(0, os.SEEK_END)
        original_size = file.tell() / (1024 * 1024)
        file.seek(0)
        logger.info(f'Original image size: {original_size:.2f} MB')

        # Resize and compress image
        resized_image = resize_image(file, max_size=(800, 600), quality=85)

        # Calculate the resized image size in MB
        resized_image.seek(0, os.SEEK_END)
        resized_size = resized_image.tell() / (1024 * 1024)
        resized_image.seek(0)
        logger.info(f'Resized image size: {resized_size:.2f} MB')

        base64_image = base64.b64encode(resized_image.read()).decode('utf-8')
        logger.info('Image resized, compressed, and encoded to base64')

        content = call_vision_api(base64_image)
        logger.info('Received response from vision API')
        logger.info('The result: ' + content)

        elapsed_time = time.time() - start_time
        logger.info(f'END - Job completed in {elapsed_time:.2f} seconds')
        return jsonify({'content': content})
    else:
        app.logger.error('Invalid file type')
        elapsed_time = time.time() - start_time
        logger.info(f'Job ended with errors in {elapsed_time:.2f} seconds')
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

@app.route('/submit-result', methods=['POST'])
def submit_result():
    logger.info(f'Received data for submit-result: {request.json}')
    if not request.json or 'count' not in request.json or 'object_name' not in request.json:
        abort(400)

    object_name = request.json['object_name']
    new_count = request.json['count']

    # Check if an entry with the same object name already exists
    existing_result = ImageResult.query.filter_by(object_name=object_name).first()
    
    if existing_result:
        # Increment the count of the existing entry
        existing_result.count += new_count
        message = f'Updated count for {object_name}. New count: {existing_result.count}'
    else:
        # Create a new entry
        new_result = ImageResult(count=new_count, object_name=object_name)
        db.session.add(new_result)
        message = f'Added new entry for {object_name} with count: {new_count}'

    db.session.commit()
    return jsonify({'message': message}), 200

@app.route('/results')
def get_results():
    results = ImageResult.query.all()
    return render_template('results.html', results=results)

@app.route('/results/<int:result_id>', methods=['PUT'])
def update_result(result_id):
    result = ImageResult.query.get_or_404(result_id)
    result.count = request.json.get('count', result.count)
    result.object_name = request.json.get('object_name', result.object_name)
    db.session.commit()
    return jsonify({'message': 'Updated successfully'})

@app.route('/delete-result/<int:result_id>', methods=['DELETE'])
def delete_result(result_id):
    result = ImageResult.query.get_or_404(result_id)
    db.session.delete(result)
    db.session.commit()
    return jsonify({'message': f'Record with id {result_id} deleted successfully'})

@app.route('/decrease-result', methods=['PATCH'])
def decrease_result():
    data = request.get_json()
    if not data or 'count' not in data or 'object_name' not in data:
        abort(400)

    item = ImageResult.query.filter_by(object_name=data['object_name']).first()
    if item:
        item.count -= data['count']
        if item.count <= 0:
            db.session.delete(item)
    db.session.commit()
    return jsonify({'message': 'Updated successfully'}), 200

@app.route('/update-inventory', methods=['POST'])
def update_inventory():
    data = request.get_json()
    print(f"Received action: {data.get('action')}, object_name: {data.get('object_name')}")
    
    if not data or 'object_name' not in data or 'action' not in data:
        abort(400, description="Missing 'object_name' or 'action' in the request")

    object_name = data['object_name']
    action = data['action']

    # Corrected logging format
    logger.info(f'Inventory update request: Action - {action.upper()}, Object Name - {object_name}')

    # Query the database for the existing inventory item
    inventory_item = ImageResult.query.filter_by(object_name=object_name).first()

    if inventory_item:
        if action == 'in':
            inventory_item.count += 1
            message = f'Increased count for {object_name}. New count: {inventory_item.count}'
        elif action == 'out':
            decrease_amount = 2  # Set the decrease amount to 2
            if inventory_item.count >= decrease_amount:
                inventory_item.count -= decrease_amount
                message = f'Decreased count for {object_name}. New count: {inventory_item.count}'
            else:
                message = f'Cannot decrease count for {object_name}. Insufficient items in inventory.'
    else:
        if action == 'in':
            inventory_item = ImageResult(count=1, object_name=object_name)
            db.session.add(inventory_item)
            message = f'Added to inventory: {object_name} with count: 1'
        elif action == 'out':
            message = f'Cannot remove from inventory: {object_name} does not exist.'

    db.session.commit()
    return jsonify({'message': message}), 200

@app.errorhandler(400)
def handle_bad_request(error):
    return jsonify({'error': 'Bad request'}), 400

if __name__ == '__main__':
    configure_logging()
    verify_api_key()
    test_openai_api_reachability()
    initialize_app()
    app.run(debug=True)
