import cv2
import numpy as np

def ImageToMatrix(path):
    img_bgr = cv2.imread(path)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype('float64')
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
                60 * ((r - g) / Delta + 4)))) #Kasus Cmax = b

    s = np.where(Cmax == 0, 0, Delta / Cmax)
    v = Cmax

    hsv_matrix = np.dstack((h, s, v))
    
    return hsv_matrix


def create_histogram(hsv_matrix):
    mod3_width = (hsv_matrix.shape[1] // 3) * 3
    mod3_length = (hsv_matrix.shape[0] // 3) * 3

    mod3_hsv_matrix = hsv_matrix[:mod3_length,:mod3_width]

    reshaped_matrix = mod3_hsv_matrix.reshape(hsv_matrix.shape[0] // 3, 3, hsv_matrix.shape[1] // 3, 3, 3)
    downsampled_matrix = np.mean(reshaped_matrix, axis=(1, 3))
    h_channel = downsampled_matrix[:, :, 0]
    s_channel = downsampled_matrix[:, :, 1]
    v_channel = downsampled_matrix[:, :, 2]
    
    h_bins = [0, 25, 40, 120, 190, 270, 295, 315, 361]
    s_bins = [0, 0.2, 0.7, 1]
    v_bins = [0, 0.2, 0.7, 1]

    hist_h, bin_edges_h = np.histogram(h_channel, bins=h_bins)
    hist_s, bin_edges_s = np.histogram(s_channel, bins=s_bins)
    hist_v, bin_edges_v = np.histogram(v_channel, bins=v_bins)

    concat = np.concatenate((hist_h, hist_s, hist_v))
    # concat = [hist_h, hist_s, hist_v]

    return concat