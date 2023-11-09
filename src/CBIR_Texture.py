import ImageToMatrix as imt
import cosine_similiarity as cs
import cv2
import numpy as np
import tqdm
import time

def img2GRY(path):
    img_rgb = imt.ImageToMatrix(path)
    gray = img_rgb[:, :, 0] * 0.299 + img_rgb[:, :, 1] * 0.587 + img_rgb[:, :, 2] * 0.114 # Y = 0.299 * R + 0.587 * G + 0.114 * B
    resize = cv2.resize(gray, None, fx = 0.4, fy = 0.4) # Resize gambar agar mudah diproses
    return resize

def glcm(path):
    img = img2GRY(path)
    glcm = np.zeros([256, 256])                 # quantization level 256
    for i in tqdm.tqdm(range(img.shape[0])):    # img height, tqdm used to see the processing time
        for j in range(img.shape[1]):           # img width
            firstpx = round(img[i][j])          # first pixel
            try:
                nextpx = round(img[i][j+1])     # next pixel
            except IndexError:                  # catch out of pixel error
                continue                        # ignore it, insignificant edge pixel
            glcm[firstpx][nextpx] += 1          # at co-occurrence matrix, add if the pixel pair is found
    return glcm

def glcmNorm(glcm):
    symMat = np.add(glcm, transpose(glcm))      # symmetric matrix = matrix + matrix^T
    glcmNorm = symMat/np.sum(symMat)
    return glcmNorm

def contrast(glcmNorm):
    sum = 0
    for i in range(glcmNorm.shape[0]):
        for j in range(glcmNorm.shape[1]):
            sum += glcmNorm[i][j]*(i-j)**2
    return sum

def homogeneity(glcmNorm):
    sum_numerator = 0
    sum_denominator = 0
    for i in range(glcmNorm.shape[0]):
        for j in range(glcmNorm.shape[1]):
            sum_numerator += glcmNorm[i][j]*(i-j)
            sum_denominator += 1 + ((i-j)**2)
    return sum_numerator/sum_denominator

def entropy(glcmNorm):
    sum = 0
    for i in range(glcmNorm.shape[0]):
        for j in range(glcmNorm.shape[1]):
            if glcmNorm[i][j] != 0:
                sum += glcmNorm[i][j] * np.log10(glcmNorm[i][j])
    return -sum

def transpose(matrix):
    tmatrix = [[0 for j in range(256)] for i in range(256)];
    for i in range(256):
        for j in range(256):
            tmatrix[i][j] = matrix[j][i]
    return tmatrix

def glcmVector(glcmNorm):
    return [contrast(glcmNorm), homogeneity(glcmNorm), entropy(glcmNorm)]

def similarity(path1, path2):
    v1 = glcmVector(glcmNorm(glcm(path1)))
    v2 = glcmVector(glcmNorm(glcm(path2)))
    print(v1)
    print(v2)
    return cs.cosine_similiarity(v1, v2)

Cpath = ".\\waifu2.jpeg"
Dpath = ".\\waifu.jpg"
stime = time.time()
print(similarity(Cpath, Dpath))
ftime = time.time()
print(ftime-stime)