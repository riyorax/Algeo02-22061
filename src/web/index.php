<?php 
    $gambar = upload();
    if (!$gambar) {
        echo "Upload failed";
    } else {
        echo "Upload success";
    }

    function upload() {
        $namaFile = $_FILES['up_image']['name'];
        $error = $_FILES['up_image']['error'];
        $tmpName = $_FILES['up_image']['tmp_name'];

        if ($error !== UPLOAD_ERR_OK) {
            echo "Error uploading file.";
            return false;
        }

        $targetDirectory = 'img/';
        if (!file_exists($targetDirectory)) {
            mkdir($targetDirectory, 0755, true);
        }

        $destinationPath = $targetDirectory . $namaFile;
        if (move_uploaded_file($tmpName, $destinationPath)) {
            return true;
        } else {
            echo "Error moving file to destination.";
            return false;
        }
    }
?>
