from function import ImageToMatrix as imt
from function import cosine_similiarity as cs
import cv2
import numpy as np
import os
import json
from multiprocessing import Pool

def img2GRY(path):
    img_rgb = imt.ImageToMatrix(path)
    gray = img_rgb[:, :, 0] * 0.299 + img_rgb[:, :, 1] * 0.587 + img_rgb[:, :, 2] * 0.114 # Y = 0.299 * R + 0.587 * G + 0.114 * B
    resize = cv2.resize(gray, None, fx = 0.4, fy = 0.4) # Resize gambar agar mudah diproses
    return resize

def glcm(path):
    img = img2GRY(path)
    quantized = np.round(img).astype(np.int32)
    max_val = quantized.max() + 1
    glcm_matrix = np.zeros((max_val, max_val), dtype=np.int32)
    for i in range(quantized.shape[0] - 1):  
        for j in range(quantized.shape[1] - 1):  
            glcm_matrix[quantized[i, j], quantized[i, j + 1]] += 1
            glcm_matrix[quantized[i, j + 1], quantized[i, j]] += 1
    return glcm_matrix

def glcmNorm(glcm_matrix):
    return glcm_matrix / glcm_matrix.sum()

def contrast(glcm_norm):
    i, j = np.indices(glcm_norm.shape)
    return np.sum(glcm_norm * (i - j) ** 2)

def energy(glcm_norm):
    # https://iopscience.iop.org/article/10.1088/1742-6596/1591/1/012028/pdf
    return np.sum(glcm_norm ** 2)

def homogeneity(glcm_norm):
    i, j = np.indices(glcm_norm.shape)
    return np.sum(glcm_norm / (1 + (i - j) ** 2))

def entropy(glcm_norm):
    mask = glcm_norm > 0
    return -np.sum(glcm_norm[mask] * np.log10(glcm_norm[mask]))

def glcm_features(glcm_norm):
    return np.array([contrast(glcm_norm), energy(glcm_norm), homogeneity(glcm_norm), entropy(glcm_norm)])


def process_texture_image(filename, folder_path):
    img_path = os.path.join(folder_path, filename)
    glcmNorm_mat = glcmNorm(glcm(img_path))
    feat_vector = glcm_features(glcmNorm_mat)
    return {'path': filename, 'features': feat_vector.tolist()}

def DatasetToTextureJSON(folder_path, json_path):
    filenames = os.listdir(folder_path)
    data_list = []

    with Pool() as pool:
        results = pool.starmap(process_texture_image, [(filename, folder_path) for filename in filenames])
    
    data_list.extend(results)

    with open(json_path, 'w') as json_file:
        json.dump(data_list, json_file, indent=4)
    
def SimilarityTexture(img_path,colour_json_path,colour_similiar_json_path):
    data = []
    with open(colour_json_path) as file:
        data = json.load(file)
    glcmNorm_mat_img = glcmNorm(glcm(img_path))
    feat_vector_img = glcm_features(glcmNorm_mat_img)
    similarities = []
    for img_dataset in data:
        vector_dataset = np.array(img_dataset['features'])
        similarity = cs.cosine_similiarity(feat_vector_img,vector_dataset)
        if similarity >= 0.6:
            similarities.append({'path': img_dataset['path'], 'similarity': similarity})
    similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)
    with open(colour_similiar_json_path, 'w') as file:
        json.dump(similarities, file, indent=4)

# if __name__ == '__main__':
#     stime = time.time()
#     DatasetToTextureJSON('src/uploads/multiple_uploads','src/data/texture.json')
#     SimilarityTexture('src/317.jpg','src/data/texture.json', 'src/data/textureSimilarity.json')
#     ftime = time.time()
#     print("Runtime: ", ftime-stime)