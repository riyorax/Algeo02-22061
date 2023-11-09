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
    h, s, v = hsv_matrix[:,:,0], hsv_matrix[:,:,1], hsv_matrix[:,:,2]
    height, width = hsv_matrix.shape[:2]

    num_blocks_height = height // 3
    num_blocks_width = width // 3

    histogram_h = np.zeros(8)
    histogram_s = np.zeros(3)
    histogram_v = np.zeros(3)

    reshaped_matrix = hsv_matrix.reshape(hsv_matrix.shape[0] // 3, 3, hsv_matrix.shape[1] // 3, 3, 3)
    downsampled_matrix = np.mean(reshaped_matrix, axis=(1, 3))
    h_channel = downsampled_matrix[:, :, 0]
    s_channel = downsampled_matrix[:, :, 1]
    v_channel = downsampled_matrix[:, :, 2]
    
    h_bins = [1, 25, 40, 120, 190, 270, 295, 315, 360]
    s_bins = [0, 0.2, 0.7, 1]
    v_bins = [0, 0.2, 0.7, 1]

    # Compute histograms for each channel using the predetermined bins
    hist_h, bin_edges_h = np.histogram(h_channel, bins=h_bins)
    hist_s, bin_edges_s = np.histogram(s_channel, bins=s_bins)
    hist_v, bin_edges_v = np.histogram(v_channel, bins=v_bins)

    # for i in range(num_blocks_height):
    #     for j in range(num_blocks_width):
    #         block_h = h[i * 3:(i + 1) * 3, j * 3:(j + 1) * 3]
    #         block_s = s[i * 3:(i + 1) * 3, j * 3:(j + 1) * 3]
    #         block_v = v[i * 3:(i + 1) * 3, j * 3:(j + 1) * 3]

    #         avg_h = np.mean(block_h)
    #         avg_s = np.mean(block_s)
    #         avg_v = np.mean(block_v)

    #         histogram_h[h_bin(avg_h)] +=1
    #         histogram_s[SorB_bin(avg_s)] +=1
    #         histogram_v[SorB_bin(avg_v)] +=1
        
    # concat = np.concatenate((histogram_h, histogram_s, histogram_v))
    concat = np.concatenate((hist_h, hist_s, hist_v))

    return concat
    # return [hist_h, hist_s, hist_v]

def h_bin(h):
    if 316 <= h <= 360:
        return 0
    elif 1 <= h <= 25:
        return 1
    elif 26 <= h <= 40:
        return 2
    elif 41 <= h <= 120:
        return 3
    elif 121 <= h <= 190:
        return 4
    elif 191 <= h <= 270:
        return 5
    elif 271 <= h <= 295:
        return 6
    elif 295 <= h <= 315:
        return 7

def SorB_bin(val):
    if 0 <= val <= 0.2:
        return 0
    elif 0.2 <= val <= 0.7:
        return 1
    elif 26 <= val <= 0.7:
        return 2

hsv_matrix = RGBtoHSV(ImageToMatrix('src/4keh.jpg'))
histogram = create_histogram(hsv_matrix)

print(histogram)