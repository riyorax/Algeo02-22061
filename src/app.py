from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename
import shutil
from function import CBIR_Colour as CC
from function import CBIR_Texture as CT

app = Flask(__name__)

SINGLE_UPLOAD_FOLDER = 'src/uploads/single_uploads'
MULTIPLE_UPLOAD_FOLDER = 'src/uploads/multiple_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app.config['SINGLE_UPLOAD_FOLDER'] = SINGLE_UPLOAD_FOLDER
app.config['MULTIPLE_UPLOAD_FOLDER'] = MULTIPLE_UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

def empty_folder(folder_path):
    if os.path.exists(folder_path):
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print('Failed to delete %s. Reason: %s' % (file_path, e))

@app.route('/', methods=['POST'])
def upload_files():

    empty_folder(app.config['SINGLE_UPLOAD_FOLDER'])
    empty_folder(app.config['MULTIPLE_UPLOAD_FOLDER'])

    os.makedirs(app.config['SINGLE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MULTIPLE_UPLOAD_FOLDER'], exist_ok=True)

    single_file = request.files.get('single_file')
    if single_file and allowed_file(single_file.filename):
        single_filename = os.path.join(app.config['SINGLE_UPLOAD_FOLDER'], secure_filename(single_file.filename))
        single_file.save(single_filename)

    multiple_files = request.files.getlist('multiple_files')
    for file in multiple_files:
        if file and allowed_file(file.filename):
            multiple_filename = os.path.join(app.config['MULTIPLE_UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(multiple_filename)
    
    if 'multiple_files' in request.files:
        CC.DatasetToColourJSON('src/uploads/multiple_uploads', 'src/data/colour.json')

        CT.DatasetToTextureJSON('src/uploads/multiple_uploads', 'src/data/texture.json')

    return redirect(url_for('result'))

@app.route("/result.html")
def result():
    return render_template('result.html')

@app.route('/aboutus.html')
def about_us():
    return render_template("aboutus.html")

@app.route('/howtouse.html')
def howtouse():
    return render_template("howtouse.html")

@app.route('/searchengineconcept.html')
def searchengineconcept():
    return render_template("searchengineconcept.html")

if __name__ == '__main__':
    app.run(debug=True)
