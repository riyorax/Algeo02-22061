import ImageToMatrix
import numpy as np

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


hsv_matrix = ImageToMatrix.RGBtoHSV(ImageToMatrix.ImageToMatrix('src/waifu2.jpeg'))

h, s, v = hsv_matrix[:,:,0], hsv_matrix[:,:,1], hsv_matrix[:,:,2]
height, width = hsv_matrix.shape[:2]

num_blocks_height = height // 3
num_blocks_width = width // 3

histogram_h = np.zeros(8)
histogram_s = np.zeros(3)
histogram_v = np.zeros(3)
mod3_width = (hsv_matrix.shape[1] // 3) * 3
mod3_length = (hsv_matrix.shape[0] // 3) * 3

mod3_hsv_matrix = hsv_matrix[:mod3_length,:mod3_width]

reshaped_matrix = mod3_hsv_matrix.reshape(hsv_matrix.shape[0] // 3, 3, hsv_matrix.shape[1] // 3, 3, 3)
downsampled_matrix = np.mean(reshaped_matrix, axis=(1, 3))
h_channel = downsampled_matrix[:, :, 0]
s_channel = downsampled_matrix[:, :, 1]
v_channel = downsampled_matrix[:, :, 2]

print("row : ", downsampled_matrix.shape[0])
print("col : ", downsampled_matrix.shape[1])

h_bins = [0, 25, 40, 120, 190, 270, 295, 315, 361]
s_bins = [0, 0.2, 0.7, 1]
v_bins = [0, 0.2, 0.7, 1]

hist_h, bin_edges_h = np.histogram(h_channel, bins=h_bins)
hist_s, bin_edges_s = np.histogram(s_channel, bins=s_bins)
hist_v, bin_edges_v = np.histogram(v_channel, bins=v_bins)

# hist_h, bin_edges_h = np.histogram(h, bins=h_bins)
# hist_s, bin_edges_s = np.histogram(s, bins=s_bins)
# hist_v, bin_edges_v = np.histogram(v, bins=v_bins)
print(len(h_channel))
print(np.sum(hist_h))

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
histogram = np.concatenate((hist_h, hist_s, hist_v))

    # return [hist_h, hist_s, hist_v]


hsv_matrix_waifu = RGBtoHSV(ImageToMatrix('src/waifu2.jpeg'))
histogram_waifu = create_histogram(hsv_matrix_waifu)


hsv_matrix_948 = RGBtoHSV(ImageToMatrix('src/948.jpg'))
histogram_948 = create_histogram(hsv_matrix_948)

print("waifu h \n", histogram_waifu[0])
print("948 h \n", histogram_948[0])

print("waifu s \n", histogram_waifu[1])
print("948 s \n", histogram_948[1])

print("waifu h \n", histogram_waifu[2])
print("948 s \n", histogram_948[2])

similarity_h = cosine_similiarity.cosine_similiarity(histogram_948[0],histogram_waifu[0])
similarity_s = cosine_similiarity.cosine_similiarity(histogram_948[1],histogram_waifu[1])
similarity_v = cosine_similiarity.cosine_similiarity(histogram_948[2],histogram_waifu[2])
print("h :", similarity_h)
print("s :", similarity_s)
print("v :", similarity_v)
avg = (similarity_h+similarity_s+similarity_v)/3
print("avg :",avg)


