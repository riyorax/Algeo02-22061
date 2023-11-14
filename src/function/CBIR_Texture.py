import ImageToMatrix as imt
import cosine_similiarity as cs
import cv2
import numpy as np
import time
import os
import json
from multiprocessing import Pool

def img2GRY(path):
    img_rgb = imt.ImageToMatrix(path)
    gray = img_rgb[:, :, 0] * 0.299 + img_rgb[:, :, 1] * 0.587 + img_rgb[:, :, 2] * 0.114 # Y = 0.299 * R + 0.587 * G + 0.114 * B
    resize = cv2.resize(gray, None, fx = 0.4, fy = 0.4) # Resize gambar agar mudah diproses
    return resize

# def glcm(path):
#     img = img2GRY(path)
#     glcm = np.zeros([256, 256])                 # quantization level 256
#     for i in (range(img.shape[0])):    # img height, tqdm used to see the processing time
#         for j in range(img.shape[1]):           # img width
#             firstpx = round(img[i][j])          # first pixel
#             try:
#                 nextpx = round(img[i][j+1])     # next pixel
#             except IndexError:                  # catch out of pixel error
#                 continue                        # ignore it, insignificant edge pixel
#             glcm[firstpx][nextpx] += 1          # at co-occurrence matrix, add if the pixel pair is found
#     return glcm

# def glcmNorm(glcm):
#     symMat = np.add(glcm, transpose(glcm))      # symmetric matrix = matrix + matrix^T
#     glcmNorm = symMat/np.sum(symMat)
#     return glcmNorm

# def contrast(glcmNorm):
#     sum = 0
#     for i in range(glcmNorm.shape[0]):
#         for j in range(glcmNorm.shape[1]):
#             sum += glcmNorm[i][j]*(i-j)**2
#     return sum

# def homogeneity(glcmNorm):
#     sum_numerator = 0
#     sum_denominator = 0
#     for i in range(glcmNorm.shape[0]):
#         for j in range(glcmNorm.shape[1]):
#             sum_numerator += glcmNorm[i][j]*(i-j)
#             sum_denominator += 1 + ((i-j)**2)
#     return sum_numerator/sum_denominator

# def entropy(glcmNorm):
#     sum = 0
#     for i in range(glcmNorm.shape[0]):
#         for j in range(glcmNorm.shape[1]):
#             if glcmNorm[i][j] != 0:
#                 sum += glcmNorm[i][j] * np.log10(glcmNorm[i][j])
#     return -sum

# def transpose(matrix):
#     tmatrix = [[0 for j in range(256)] for i in range(256)];
#     for i in range(256):
#         for j in range(256):
#             tmatrix[i][j] = matrix[j][i]
#     return tmatrix

# def glcmVector(glcmNorm):
#     return [contrast(glcmNorm), homogeneity(glcmNorm), entropy(glcmNorm)]

# def similarity(path1, path2):
#     v1 = glcmVector(glcmNorm(glcm(path1)))
#     v2 = glcmVector(glcmNorm(glcm(path2)))
#     print(v1)
#     print(v2)
#     return cs.cosine_similiarity(v1, v2)

# import numpy as np
# import cv2

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

def homogeneity(glcm_norm):
    i, j = np.indices(glcm_norm.shape)
    return np.sum(glcm_norm / (1 + (i - j) ** 2))

def entropy(glcm_norm):
    mask = glcm_norm > 0
    return -np.sum(glcm_norm[mask] * np.log10(glcm_norm[mask]))

def glcm_features(glcm_norm):
    return np.array([contrast(glcm_norm), homogeneity(glcm_norm), entropy(glcm_norm)])

def similarity(path1, path2):
    # img1 = img2GRY(path1)
    # img2 = img2GRY(path2)
    glcm1 = glcm(path1)
    glcm2 = glcm(path2)
    glcm_norm1 = glcmNorm(glcm1)
    glcm_norm2 = glcmNorm(glcm2)
    v1 = glcm_features(glcm_norm1)
    v2 = glcm_features(glcm_norm2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

# Use the similarity function to compare two images
# similarity_score = similarity('path_to_image1.jpg', 'path_to_image2.jpg')

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

# def DatasetToTextureJSON(folder_path,json_path):
#     data_list = []
#     for filename in os.listdir(folder_path):
#         img_path = os.path.join(folder_path,filename)
#         glcmNorm_mat = glcmNorm(glcm(img_path))
#         feat_vector = glcm_features(glcmNorm_mat)
#         feat_vector = feat_vector.tolist()
#         img_data = {'path': filename, 'features': feat_vector}
#         data_list.append(img_data)
#     with open(json_path, 'w') as json_file:
#         json.dump(data_list, json_file, indent=4)
    
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

if __name__ == '__main__':
    stime = time.time()
    DatasetToTextureJSON('src/uploads/multiple_uploads','src/data/texture.json')
    SimilarityTexture('src/317.jpg','src/data/texture.json', 'src/data/textureSimilarity.json')
    ftime = time.time()
    print("Runtime: ", ftime-stime)