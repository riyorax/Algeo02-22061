from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
import shutil
import json
from function import CBIR_Colour as CC
from function import CBIR_Texture as CT

app = Flask(__name__)

def get_single_file_name(folder_path):
    files = os.listdir(folder_path)
    if files:
        return files[0]
    else:
        return None

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

SINGLE_UPLOAD_FOLDER = 'src/static/single_uploads'
MULTIPLE_UPLOAD_FOLDER = 'src/static/multiple_uploads'
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

    os.makedirs(app.config['SINGLE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MULTIPLE_UPLOAD_FOLDER'], exist_ok=True)

    empty_folder(app.config['SINGLE_UPLOAD_FOLDER'])
    empty_folder(app.config['MULTIPLE_UPLOAD_FOLDER'])

    single_file = request.files.get('single_file')
    if single_file and allowed_file(single_file.filename):
        single_filename = os.path.join(app.config['SINGLE_UPLOAD_FOLDER'], secure_filename(single_file.filename))
        single_file.save(single_filename)

    multiple_files = request.files.getlist('multiple_files')
    for file in multiple_files:
        if file and allowed_file(file.filename):
            multiple_filename = os.path.join(app.config['MULTIPLE_UPLOAD_FOLDER'], secure_filename(file.filename))
            file.save(multiple_filename)

    if 'single_file' in request.files:
        CC.DatasetToColourJSON('src/static/multiple_uploads', 'src/data/colour.json')
        single_file_name = get_single_file_name('src/static/single_uploads')
        single_file_name = 'src/static/single_uploads/' + single_file_name 
        CC.SimilarityColour(single_file_name, 'src/data/colour.json','src/data/colourSimilarity.json')

    return redirect(url_for('result',page =1))



# PAGINATION 



@app.route('/result/<int:page>')
def result(page=1):
    with open('src/data/colourSimilarity.json', 'r') as file:
        dummy_data = json.load(file)

    items_per_page = 10
    page = int(request.args.get('page', 1))

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    current_page_data = dummy_data[start_idx:end_idx]

    total_pages = (len(dummy_data) + items_per_page - 1) // items_per_page

    single_file_name = get_single_file_name('src/static/single_uploads')
    return render_template('result.html', data=current_page_data, current_page=page, total_pages=total_pages, single_file_name=single_file_name)

@app.route('/src/uploads/multiple_uploads/<path:filename>')
def serve_image(filename):
    return send_from_directory('src/uploads/multiple_uploads', filename)

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

# from function import CBIR_Colour as CC

# if __name__ == '__main__':
#     CC.DatasetToColourJSON('src/static/multiple_uploads', 'src/data/colourSimilarity.json')

# print(get_single_file_name('src/static/single_uploads'))