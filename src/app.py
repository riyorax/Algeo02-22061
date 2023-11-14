from flask import Flask, render_template, request, redirect, url_for
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)

SINGLE_UPLOAD_FOLDER = 'single_uploads'
MULTIPLE_UPLOAD_FOLDER = 'multiple_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['SINGLE_UPLOAD_FOLDER'] = SINGLE_UPLOAD_FOLDER
app.config['MULTIPLE_UPLOAD_FOLDER'] = MULTIPLE_UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def upload_files():

    single_file = request.files.get('single_file')
    if single_file and allowed_file(single_file.filename):
        single_filename = os.path.join(app.config['SINGLE_UPLOAD_FOLDER'], secure_filename(single_file.filename))
        single_file.save(single_filename)

    multiple_files = request.files.getlist('multiple_files')
    for file in multiple_files:
        if file and allowed_file(file.filename):
            multiple_filename = os.path.join(app.config['MULTIPLE_UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(multiple_filename)

    return redirect(url_for('index'))

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
