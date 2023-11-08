import ImageToMatrix as imt
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
                continue
            glcm[firstpx][nextpx] += 1          # at co-occurrence matrix, add if the pixel pair is found
    return glcm

def glcmNorm(glcm):
    symMat = np.add(glcm, transpose(glcm))      # symmetric matrix = matrix + matrix^T
    glcmNorm = symMat/np.sum(symMat)
    return glcmNorm

def contrast():
    pass

def homogeneity():
    pass

def entropy():
    pass

def transpose(matrix):
    tmatrix = [[0 for j in range(256)] for i in range(256)];
    for i in range(256):
        for j in range(256):
            tmatrix[i][j] = matrix[j][i]
    return tmatrix
            
Cpath = ".\\waifu.jpg"
stime = time.time()
print(glcmNorm(glcm(Cpath)))
ftime = time.time()
print(ftime-stime)