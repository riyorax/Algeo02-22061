from flask import Flask, request, render_template
import os

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = "uploaded_images"
app.config['IMAGE_FOLDER'] = 'gallery'
app.config['ALLOWED_EXTENSIONS'] = {'png, jpg, jpeg, csv'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/index")
def Index():
    return render_template("index.html")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'image' not in request.files:
            return render_template('index.html', message='No file part')
        file = request.files['image']
        if file.filename == '':
            return render_template('index.html', message='No selected file')
        file.save(app.config['UPLOAD_FOLDER'] + '/' + file.filename)
        return render_template('index.html', message='File uploaded successfully')
    return render_template('index.html', message=None)

@app.route('/upload', methods=['POST'])
def upload_dataset():
    if 'dataset' not in request.files:
        return 'No file part'
    file = request.files['dataset']
    if file.filename == '':
        return 'No selected file'
    if file and allowed_file(file.filename):
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
        return 'Dataset uploaded successfully!'
    else:
        return 'Invalid file format. Please upload a CSV file.'

if __name__ == "__main__":
    app.run(debug=True)
