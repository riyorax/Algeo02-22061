import cv2
import numpy as np

def ImageToMatrix(path):
    img_bgr = cv2.imread(path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype('float32')
    return img_rgb

def RGBtoHSV(rgb_matrix):
    rgb_normalized = rgb_matrix / 255.0
    r, g, b = rgb_normalized[:, :, 0], rgb_normalized[:, :, 1], rgb_normalized[:, :, 2]

    Cmax = np.max(rgb_normalized, axis=-1)
    Cmin = np.min(rgb_normalized, axis=-1)
    Delta = Cmax - Cmin

    h = np.where(Delta == 0, 0,
                np.where(Cmax == r, 60 * ((g - b) / Delta % 6), #Kasus Cmax = r
                np.where(Cmax == g, 60 * ((b - r) / Delta + 2), #Kasus Cmax = g
                60 * ((r - g) / Delta + 4))))                   #Kasus Cmax = b

    s = np.where(Cmax == 0, 0, Delta / Cmax)
    v = Cmax

    hsv_matrix = np.dstack((h, s, v))
    
    return hsv_matrix