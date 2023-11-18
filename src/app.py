from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import os
from werkzeug.utils import secure_filename
import shutil
import json
from function import CBIR_Colour as CC
from function import CBIR_Texture as CT
import time
from flask import Response
from fpdf import FPDF
from PIL import Image

app = Flask(__name__)

global runtimer

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

    toggle_state = 'on' if 'toggleSwitch' in request.form else 'off'

    os.makedirs(app.config['SINGLE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['MULTIPLE_UPLOAD_FOLDER'], exist_ok=True)

    single_file = request.files.get('single_file')
    new_image = single_file and single_file.filename != ''

    if new_image:
        empty_folder(app.config['SINGLE_UPLOAD_FOLDER'])
    if new_image:
        empty_folder(app.config['SINGLE_UPLOAD_FOLDER'])
        single_filename = os.path.join(app.config['SINGLE_UPLOAD_FOLDER'], secure_filename(single_file.filename))
        single_file.save(single_filename)
    else:
        single_file_name = get_single_file_name('src/static/single_uploads')

    multiple_files = request.files.getlist('multiple_files')
    new_dataset = multiple_files and multiple_files[0].filename != ''
    if new_dataset:
        empty_folder(app.config['MULTIPLE_UPLOAD_FOLDER'])
        for file in multiple_files:
            if file and allowed_file(file.filename):
                multiple_filename = os.path.join(app.config['MULTIPLE_UPLOAD_FOLDER'], secure_filename(file.filename))
                file.save(multiple_filename)

    stime = time.time()
    if 'single_file' in request.files:
        single_file_name = get_single_file_name('src/static/single_uploads')
        single_file_name = 'src/static/single_uploads/' + single_file_name 
        if toggle_state == 'off':
            if new_dataset:
                CC.DatasetToColourJSON('src/static/multiple_uploads', 'src/data/colour.json')
            CC.SimilarityColour(single_file_name, 'src/data/colour.json', 'src/data/similarity.json')
        else:
            if new_dataset:
                CT.DatasetToTextureJSON('src/static/multiple_uploads', 'src/data/texture.json')
            CT.SimilarityTexture(single_file_name, 'src/data/texture.json', 'src/data/similarity.json')
    ftime = time.time()
    runtime = round(ftime - stime, 2)
    global runtimer
    runtimer = runtime

    return redirect(url_for('result',page =1, runtime = runtime))

# PAGINATION 

@app.route('/result/<int:page>', methods=['GET'])
def result(page=1):
    runtime = request.args.get('runtime', default=runtimer, type=float)
    with open('src/data/similarity.json', 'r') as file:
        dummy_data = json.load(file)

    items_per_page = 6

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    current_page_data = dummy_data[start_idx:end_idx]

    total_pages = (len(dummy_data) + items_per_page - 1) // items_per_page

    total_images = len(dummy_data)

    single_file_name = get_single_file_name('src/static/single_uploads')
    return render_template('result.html', data=current_page_data, current_page=page, total_pages=total_pages, single_file_name=single_file_name, runtime = runtime, total_images=total_images)

# Download PDF

def get_image_dimensions(image_path):
    with Image.open(image_path) as img:
        width, height = img.size
    return width, height

@app.route('/download_pdf', methods=['POST'])

def download_pdf():
    with open('src/data/similarity.json', 'r') as file:
        similarity_data = json.load(file)

    sorted_data = sorted(similarity_data, key=lambda x: x['similarity'], reverse=True)
    top_3_data = sorted_data[:3]

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    single_file_name = get_single_file_name('src/static/single_uploads')
    single_image_path = f'src/static/single_uploads/{single_file_name}'
    
    img_width, img_height = get_image_dimensions(single_image_path)

    pdf.ln(5)
    if img_width > img_height:  
        pdf.image(f'src/static/single_uploads/{single_file_name}', x=pdf.w / 2 - 25 , y=None, w=50)
    else:  
        pdf.image(f'src/static/single_uploads/{single_file_name}', x=pdf.w / 2 - 15 , y=None, h=50) 
    pdf.cell(0, 10, "Compared Image", ln=True, align='C')
    pdf.ln(5)

    pdf.set_font("Arial", size=12)

    for i, data in enumerate(top_3_data): 

        if img_width > img_height:  
            pdf.image(f'src/static/multiple_uploads/{data["path"]}' , x=pdf.w / 2 - 25 , y=None, w=50)
        else:  
            pdf.image(f'src/static/multiple_uploads/{data["path"]}' , x=pdf.w / 2 - 15 , y=None, h=50) 

        similarity_text = f"Similarity: {data['similarity']}"
        pdf.cell(0, 10, similarity_text, ln=True, align='C') 
        pdf.ln(5) 

    response = Response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; algeolens.pdf'

    return response








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
