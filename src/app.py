from flask import Flask, render_template, request, redirect, url_for, send_from_directory, jsonify
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
import zipfile
import tempfile
from multiprocessing import Pool
from decimal import Decimal, ROUND_DOWN

app = Flask(__name__)

global runtimer
global processedTexture
global processedColour
global functionUsed

processedTexture = False
processedColour = False

def get_single_file_name(folder_path):
    files = os.listdir(folder_path)
    if files:
        return files[0]
    else:
        return None
    
def is_dataset_empty(dataset_path):
    for _, _, files in os.walk(dataset_path):
        if files:
            return False
    return True

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

IMAGE_UPLOAD_FOLDER = 'src/static/image_upload'
DATASET_FOLDER = 'src/static/dataset'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp'}

app.config['IMAGE_UPLOAD_FOLDER'] = IMAGE_UPLOAD_FOLDER
app.config['DATASET_FOLDER'] = DATASET_FOLDER

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

def extract_file(args):
    zip_path, member, extract_path = args
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        source = zip_ref.open(member)
        target_file_path = os.path.join(extract_path, os.path.basename(member.filename))
        with open(target_file_path, "wb") as target:
            shutil.copyfileobj(source, target)
        source.close()

@app.route('/upload_dataset', methods=['POST'])
def upload_dataset():
    global processedColour
    global processedTexture

    zip_file = request.files.get('zip_file')
    if zip_file:
        temp_file = tempfile.NamedTemporaryFile(delete=False)
        zip_filename = secure_filename(zip_file.filename)
        temp_file_path = temp_file.name
        zip_file.save(temp_file_path)
        temp_file.close()

        extract_path = 'src/static/dataset'

        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path, exist_ok=True)

        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            members = [m for m in zip_ref.infolist() if not m.is_dir()]
            args = [(temp_file_path, member, extract_path) for member in members]

        with Pool() as pool:
            pool.map(extract_file, args)

        os.remove(temp_file_path)

        

        processedTexture = False
        processedColour = False

        return 'Dataset uploaded and extracted successfully'

    return 'No file uploaded'

@app.route('/', methods=['POST'])
def search():
    global processedTexture
    global processedColour
    global runtimer
    global functionUsed

    os.makedirs(app.config['IMAGE_UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['DATASET_FOLDER'], exist_ok=True)

    uploaded_image = request.files.get('upload_image')
    new_image = uploaded_image and uploaded_image.filename != ''

    if new_image:
        empty_folder(app.config['IMAGE_UPLOAD_FOLDER'])
        image_filename = os.path.join(app.config['IMAGE_UPLOAD_FOLDER'], secure_filename(uploaded_image.filename))
        uploaded_image.save(image_filename)
    else:
        image_filename = get_single_file_name('src/static/image_upload')

    stime = time.time()
    dataset_path = 'src/static/dataset'
    if is_dataset_empty(dataset_path):
        return jsonify({'error': 'Please upload a dataset before searching.'}), 400
    
    toggle_state = 'on' if 'toggleSwitch' in request.form else 'off'

    img_path = get_single_file_name('src/static/image_upload')
    print(img_path)
    img_path = 'src/static/image_upload/' + img_path

    if toggle_state == 'off':
        functionUsed = "CBIR Colour"
        if not processedColour:
            CC.DatasetToColourJSON('src/static/dataset', 'src/data/colour.json')
            processedColour = True
        CC.SimilarityColour(img_path, 'src/data/colour.json', 'src/data/similarity.json')
    else:
        functionUsed = "CBIR Texture"
        if not processedTexture:
            CT.DatasetToTextureJSON('src/static/dataset', 'src/data/texture.json')
            processedTexture = True
        CT.SimilarityTexture(img_path, 'src/data/texture.json', 'src/data/similarity.json')
    ftime = time.time()
    runtime = round(ftime - stime, 2)
    runtimer = runtime
    return redirect(url_for('result',page =1, runtime = runtime))

# PAGINATION 

@app.route('/result/<int:page>', methods=['GET'])
def result(page=1):
    global runtimer
    runtime = request.args.get('runtime', default=runtimer, type=float)
    with open('src/data/similarity.json', 'r') as file:
        image_data = json.load(file)
    
    for item in image_data:
        similarity = Decimal(str(item['similarity'])) * 100
        format_percentage = similarity.quantize(Decimal('.01'), rounding=ROUND_DOWN)
        item['similarity'] = f"{format_percentage}%"
        
    items_per_page = 6

    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    current_page_data = image_data[start_idx:end_idx]

    total_pages = (len(image_data) + items_per_page - 1) // items_per_page

    total_images = len(image_data)

    image_upload = get_single_file_name('src/static/image_upload')
    global functionUsed
    return render_template('result.html', data=current_page_data, current_page=page, total_pages=total_pages, single_file_name=image_upload, runtime = runtime, total_images=total_images, functionUsed = functionUsed)

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

    single_file_name = get_single_file_name('src/static/image_upload')
    single_image_path = f'src/static/image_upload/{single_file_name}'
    img_width, img_height = get_image_dimensions(single_image_path)

    pdf.ln(5)
    pdf.set_font("Arial", 'B', size=16)
    pdf.cell(0, 14, "ALGEO LENS", ln=True, align='C')
    pdf.ln(5)

    if img_width > img_height:  
        pdf.image(f'src/static/image_upload/{single_file_name}', x=10 , y=None, w=50)
    else:  
        pdf.image(f'src/static/image_upload/{single_file_name}', x=10 , y=None, h=50)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Compared Image", ln=True, align='L')
    pdf.ln(5)


    for i, data in enumerate(top_3_data): 

        if img_width > img_height:  
            pdf.image(f'src/static/dataset/{data["path"]}' , x=10 , y=None, w=50)
        else:  
            pdf.image(f'src/static/dataset/{data["path"]}' , x=10 , y=None, h=40) 

        similarity_text = f"Similarity: {data['similarity']}"
        pdf.cell(0, 10, similarity_text, ln=True, align='L') 
        pdf.ln(5) 

    response = Response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename="algeolens.pdf"'

    return response

# Routing

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
