# groceries_io - Image Recognition Web Application

## Overview
This project is a web-based application that allows users to upload an image and receive information about its contents using an AI-powered image recognition service. It's designed for users on the same local network to access the application via a web browser.

## Features
- Image Upload: Users can upload images using a simple interface.
- Image Recognition: The application uses OpenAI's image recognition API to analyze the uploaded images.
- Result Display: After processing, the application displays the recognition results on the web page.

## Technology Stack
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Flask (Python)
- **AI Service**: OpenAI API

## Setup and Installation

### Prerequisites
- Python 3.x
- Flask
- Requests library

### Installing Dependencies
Install the required Python packages using pip:
```bash
pip install flask requests openai 
```

### Environment Variables
Set the OpenAI API key as an environment variable:
```bash
# For Windows
set OPENAI_API_KEY=your_api_key_here

# For Unix/Linux
export OPENAI_API_KEY=your_api_key_here
```

### Running the Application
Navigate to the project directory and run the Flask application:
```bash
python app.py
```

## Usage
1. Open a web browser and navigate to `http://localhost:5000`.
2. Upload an image using the provided interface.
3. View the AI's analysis of the image displayed on the page.

## Accessing the App on a Local Network
To access the application from other devices on the same network:
1. Run the Flask app with the host set to `0.0.0.0`:
   ```bash
   flask run --host=0.0.0.0
   ```
2. On other devices, enter the IP address of the host machine followed by `:5000` in a web browser.

## Security Note
Running the application on `0.0.0.0` makes it accessible on all network interfaces. Ensure your network is secure and avoid exposing sensitive information.

## Future Enhancements
- Improve UI/UX design.
- Implement additional error handling and input validation.
- Explore deployment options for broader access.

## License
[MIT License](LICENSE)

## Author
Ket Wong

