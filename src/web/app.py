from flask import Flask, render_template
from PIL import Image
import os

app = Flask(__name__)

def get_image_list(directory):
    image_list = []
    files = os.listdir(directory)

    for file in files:
        if file.lower().endswith(('.png', '.jpg', '.jpeg')):
            image_path = os.path.join(directory, file)
            image = Image.open(image_path)
            image_list.append((file, image))

    return image_list

@app.route('/')
def index():
    # Use os.path.abspath to get the absolute path
    directory_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "static/images"))
    
    # Ensure that the 'static/images' folder structure exists
    if not os.path.exists(directory_path):
        print(f"Error: The directory '{directory_path}' does not exist.")
        return "Error: Image directory not found."

    images = get_image_list(directory_path)

    return render_template('index.html', images=images)

if __name__ == '__main__':
    app.run(debug=True)
