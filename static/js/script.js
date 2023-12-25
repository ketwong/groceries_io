document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    document.getElementById('loading').style.display = 'block';
    var formData = new FormData(this);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        console.log('Data:', data); // For debugging
    
        // Check if data contains the expected structure
        if (typeof data.content === 'string') {
            const parts = data.content.split(', ');
            if (parts.length === 2) {
                const count = parseInt(parts[0], 10);
                const objectName = parts[1];
    
                if (!isNaN(count)) {
                    // Display the result before submitting to submit-result endpoint
                    document.getElementById('result').textContent = `${count}, ${objectName}`;
    
                    // Submit to submit-result endpoint
                    return fetch('/submit-result', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ count, object_name: objectName })
                    });
                }
            }
        }
        throw new Error('Invalid response format from /upload');
    })    
    .then(response => response.json())
    .then(json => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('processing').style.display = 'none';
        document.getElementById('result').textContent = 'Result: ' + json.message;
    })
    .catch(error => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('processing').style.display = 'none';
        console.error('Error:', error);
        document.getElementById('result').textContent = 'Error: ' + error.message;
    });
});

document.getElementById('image-input').addEventListener('change', function(e) {
    var file = e.target.files[0];
    var reader = new FileReader();
    reader.onload = function(e) {
        var img = document.getElementById('image-preview');
        img.src = e.target.result;
        img.style.display = 'block';
    };
    reader.readAsDataURL(file);
});
