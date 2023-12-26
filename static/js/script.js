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

        if (typeof data.content === 'string') {
            const parts = data.content.split(', ');
            if (parts.length === 2) {
                const count = parseInt(parts[0], 10);
                const objectName = parts[1];

                if (!isNaN(count)) {
                    document.getElementById('result').textContent = `${count}, ${objectName}`;
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

document.getElementById('inventory-toggle').addEventListener('change', function() {
    const action = this.checked ? 'out' : 'in';

    // Log the action to the console
    console.info(`User selected: ${action.toUpperCase()}`);
    
    // Update the inventory status display based on the action
    document.getElementById('inventory-status').textContent = action.toUpperCase();
    
    // Call updateInventory with the appropriate action
    updateInventory(action);
});



// Make sure you have two buttons or controls with IDs 'add-inventory' and 'remove-inventory'
document.getElementById('add-inventory').addEventListener('click', function() {
    updateInventory('in');
});

document.getElementById('remove-inventory').addEventListener('click', function() {
    updateInventory('out');
});

function updateInventory(action) {
    const objectName = document.getElementById('recognized-object').textContent;
    if (!objectName) {
        console.error('No object recognized. Cannot update inventory.');
        // Optionally, display an error message to the user.
        document.getElementById('result').textContent = 'Error: No object recognized. Cannot update inventory.';
        return; // Exit the function if there's no object name.
    }
    console.log(`Sending action: ${action}, object: ${objectName}`); // Debugging

    fetch('/update-inventory', {
        method: 'POST', // Ensure this matches the backend method
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: action, object_name: objectName })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(json => {
        document.getElementById('result').textContent = json.message;
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('result').textContent = 'Error: ' + error.message;
    });
}

document.getElementById('image-input').addEventListener('change', function(e) {
    var file = e.target.files[0];
    if (file) {
        var reader = new FileReader();
        reader.onload = function(e) {
            console.log("FileReader loaded the file"); // For debugging
            var img = document.getElementById('image-preview');
            if (img) {
                img.src = e.target.result;
                img.style.display = 'block';
            } else {
                console.error("Couldn't find the image-preview element");
            }
        };
        reader.onerror = function(e) {
            console.error("FileReader encountered an error: ", e);
        };
        reader.readAsDataURL(file);
    } else {
        console.log("No file selected");
    }
});

