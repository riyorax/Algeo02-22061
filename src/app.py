from flask import Flask, request, render_template
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploaded_images"
app.config['IMAGE_FOLDER'] = 'gallery'
app.config['ALLOWED_EXTENSIONS'] = {'png, jpg, jpeg'}

@app.route("/index")
def Index():
    return render_template("index.html")

# Set extension yang boleh diupload 
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Upload image buat diproses
@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return 'File uploaded successfully'
    else:
        return 'File format not allowed'

image_data = {
    'meme.jpeg': 'gambar 1',
    'megumikato.jpg': 'gambar 2'
}

def index():
    return render_template('gallery.html', image_data=image_data)

if __name__ == "__main__":
    app.run(debug=True)
