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

    toggle_state = 'on' if 'toggleSwitch' in request.form else 'off'

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
    stime = time.time()
    if toggle_state == 'off':
        if 'single_file' in request.files:
            CC.DatasetToColourJSON('src/static/multiple_uploads', 'src/data/colour.json')
            single_file_name = get_single_file_name('src/static/single_uploads')
            single_file_name = 'src/static/single_uploads/' + single_file_name 
            CC.SimilarityColour(single_file_name, 'src/data/colour.json','src/data/similarity.json')
    else:
        if 'single_file' in request.files:
            CT.DatasetToTextureJSON('src/static/multiple_uploads', 'src/data/texture.json')
            single_file_name = get_single_file_name('src/static/single_uploads')
            single_file_name = 'src/static/single_uploads/' + single_file_name 
            CT.SimilarityTexture(single_file_name, 'src/data/texture.json','src/data/similarity.json')
    ftime = time.time()
    runtime = round(ftime - stime, 2)

    return redirect(url_for('result',page =1, runtime = runtime))



# PAGINATION 



@app.route('/result/<int:page>', methods=['GET'])
def result(page=1):
    runtime = request.args.get('runtime', default=0, type=float)
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


@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    with open('src/data/similarity.json', 'r') as file:
        similarity_data = json.load(file)

    # Sort the data based on similarity (you may need to adjust this depending on your data structure)
    sorted_data = sorted(similarity_data, key=lambda x: x['similarity'], reverse=True)

    # Take the top 6 images
    top_6_data = sorted_data[:6]

    # Create a PDF document
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Set font for the PDF
    pdf.set_font("Arial", size=12)

    # Add the single file image to the PDF
    single_file_name = get_single_file_name('src/static/single_uploads')
    single_image_path = f'src/static/single_uploads/{single_file_name}'

    # Center the single file image
    pdf.image(single_image_path, x=pdf.w / 2 - 40, y=pdf.get_y(), w=80)  # Adjust 'w' parameter if needed

    # Move to the next line after the single file image
    pdf.ln(65)

    # Set image size and margin for the top 6 images
    image_size = 40  # Adjust the image size as needed
    margin = 5  # Adjust the margin as needed

    # Add the top 6 images and similarity information
    for i in range(0, len(top_6_data), 2):
        for j in range(2):
            if i + j < len(top_6_data):
                image_path = f'src/static/multiple_uploads/{top_6_data[i + j]["path"]}'
                
                # Center the image with additional margin between columns
                x_position = pdf.w / 4 - image_size / 2 + j * (pdf.w / 2) + j * (margin)
                
                pdf.image(image_path, x=x_position, y=pdf.get_y(), w=image_size)

                # Add similarity information below the image
                similarity_text = f"Similarity: {top_6_data[i + j]['similarity']}"
                pdf.ln(5)  # Move down a bit
                pdf.cell(0, 10, similarity_text, ln=True, align='C')  # Center the text

        # Move to the next line after each pair of images
        pdf.ln(image_size + margin + 15)  # Add extra spacing between pairs

    # Output the PDF content
    response = Response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=top_6_images.pdf'

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
