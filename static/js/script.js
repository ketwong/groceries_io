document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    document.getElementById('loading').style.display = 'block';
    var formData = new FormData(this);

    fetch('/upload', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          document.getElementById('loading').style.display = 'none';
          document.getElementById('processing').style.display = 'block';

          setTimeout(() => {
              document.getElementById('processing').style.display = 'none';
              // Update this line to display amount and groceryItem
              document.getElementById('result').textContent = 'Result: ' + data.amount + ', ' + data.groceryItem;
          }, 1000);
      }).catch(error => {
          document.getElementById('loading').style.display = 'none';
          document.getElementById('processing').style.display = 'none';
          console.error('Error:', error);
          document.getElementById('result').textContent = 'Error: ' + error;
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