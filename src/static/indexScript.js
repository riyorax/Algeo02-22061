function previewImage(input) {
    var preview = document.getElementById('uploadPreview');
    
    if (input.files && input.files[0]) {
        var reader = new FileReader();
        
        reader.onload = function(e) {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(input.files[0]);
    } else {
        preview.src = 'src/static/placeholder.png';
    }
}

function zipAndUploadDataset() {
    var datasetFiles = document.getElementById('dataset_files').files;
    if (datasetFiles.length === 0) {
        alert('Please select a dataset to upload.');
        return;
    }
    document.getElementById('loading').style.display = 'flex';
    var zip = new JSZip();
    for (var i = 0; i < datasetFiles.length; i++) {
        var file = datasetFiles[i];
        zip.file(file.webkitRelativePath || file.name, file);
    }
    zip.generateAsync({type: "blob"})
        .then(function(content) {
            var formData = new FormData();
            formData.append('zip_file', content, 'dataset.zip');

            return fetch('/upload_dataset', {
                method: 'POST',
                body: formData
            });
        })
        .then(response => {
            document.getElementById('loading').style.display = 'none';

            if (response.ok) {
                alert('Dataset has been successfully uploaded.');
            } else {
                console.error('Upload failed:', response.statusText);
                alert('Failed to upload dataset.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            document.getElementById('loading').style.display = 'none';
            alert('An error occurred during upload.');
        });
}

function checkUploadAndRedirect() {
    var uploadImageInput = document.getElementById('upload_image');
    if (!uploadImageInput.files.length) {
        alert("Please select an image to upload!");
        return false;
    }
    document.getElementById('loading').style.display = 'flex';
    redirectToResult()
}

function redirectToResult() {
    window.location.href = "result.html";
}