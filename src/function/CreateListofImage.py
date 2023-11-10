from PIL import Image
import os

def convert_images_with_descriptions_to_list(directory, description_file):
    image_list = []
    # Check if the description file exists
    if not os.path.exists(description_file):
        print(f"Description file '{description_file}' not found.")
        return image_list

    # Read descriptions from the file
    with open(description_file, 'r') as file:
        descriptions = file.readlines()

    # Get a list of all files in the directory
    files = os.listdir(directory)

    # Match images with their descriptions
    for file, description in zip(files, descriptions):
        # Check if the file is an image (you can add more image extensions if needed)
        if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            # Create a tuple with the image name, description, and the image object
            image_path = os.path.join(directory, file)
            image = Image.open(image_path)
            image_list.append((file, description.strip(), image))

    return image_list

