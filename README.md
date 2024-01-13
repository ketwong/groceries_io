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
- Pillow library
- OpenAI library

### Installing Dependencies
Install the required Python packages using pip:
```bash
pip install flask requests openai Pillow Flask-SQLAlchemy
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

2. On other devices, enter the IP address of the host machine followed by :5000 in a web browser.
# Interacting with the Database
Reading from the Database
Use the read_db.py script to read data from the SQLite database:

**READ DB:** 
```
python scripts/read_db.py
```

Updating the Database
Use HTTP requests to update or delete data:

* To update a record, send a PUT request to /results/<result_id> with the new data.
* To delete a record, send a DELETE request to /delete-result/<result_id>.

**DELETE DB entry:**
```
PS C:\Users\dev> Invoke-WebRequest -Uri "http://localhost:5000/delete-result/2" -Method DELETE


StatusCode        : 200
StatusDescription : OK
Content           : {"message":"Record with id 2 deleted successfully"}

RawContent        : HTTP/1.1 200 OK
                    Connection: close
                    Content-Length: 52
                    Content-Type: application/json
                    Date: Mon, 25 Dec 2023 18:56:38 GMT
                    Server: Werkzeug/3.0.1 Python/3.12.1

                    {"message":"Record with id 2 delete...
Forms             : {}
Headers           : {[Connection, close], [Content-Length, 52], [Content-Type, application/json], [Date, Mon, 25 Dec
                    2023 18:56:38 GMT]...}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : System.__ComObject
RawContentLength  : 52
```

**UPDATE DB entry:**
```
$uri = 'http://localhost:5000/results/1' # Replace with the correct URI and ID
$body = @{
    count = 3
    object_name = 'Car'
} | ConvertTo-Json

Invoke-WebRequest -Uri $uri -Method PUT -Body $body -ContentType "application/json"
PS C:\Users\dev\git\groceries_io> Invoke-WebRequest -Uri $uri -Method PUT -Body $body -ContentType "application/json"

StatusCode        : 200
StatusDescription : OK
Content           : {"message":"Updated successfully"}

RawContent        : HTTP/1.1 200 OK
                    Connection: close
                    Content-Length: 35
                    Content-Type: application/json
                    Date: Mon, 25 Dec 2023 19:15:58 GMT
                    Server: Werkzeug/3.0.1 Python/3.12.1

                    {"message":"Updated successfully"}
                    ...
Forms             : {}
Headers           : {[Connection, close], [Content-Length, 35], [Content-Type, application/json], [Date, Mon, 25 Dec
                    2023 19:15:58 GMT]...}
Images            : {}
InputFields       : {}
Links             : {}
ParsedHtml        : System.__ComObject
RawContentLength  : 35
```

## Security Note
Running the application on `0.0.0.0` makes it accessible on all network interfaces. Ensure your network is secure and avoid exposing sensitive information.

## Future Enhancements
- Improve UI/UX design.
- Implement additional error handling and input validation.
- Explore deployment options for broader access.
- Enhance the database functionality to track and manage image recognition results more efficiently.

## License
[MIT License](LICENSE)

## Author
Ket Wong

## History

v1 
![image](https://github.com/ketwong/groceries_io/assets/42503376/d1151277-9707-4142-979a-7d791c25667c)

