import ImageToMatrix as imt
import numpy as np
import os
import json
import warnings
import time
import cosine_similiarity as cs
import cv2
from multiprocessing import Pool

warnings.filterwarnings('ignore')

# def create_histogram(img_path):
#     hsv_matrix = imt.RGBtoHSV(imt.ImageToMatrix(img_path))
#     mod3_width = (hsv_matrix.shape[1] // 3) * 3
#     mod3_length = (hsv_matrix.shape[0] // 3) * 3

#     mod3_hsv_matrix = hsv_matrix[:mod3_length,:mod3_width]

#     reshaped_matrix = mod3_hsv_matrix.reshape(hsv_matrix.shape[0] // 3, 3, hsv_matrix.shape[1] // 3, 3, 3)
#     downsampled_matrix = np.mean(reshaped_matrix, axis=(1, 3))
#     h_channel = downsampled_matrix[:, :, 0]
#     s_channel = downsampled_matrix[:, :, 1]
#     v_channel = downsampled_matrix[:, :, 2]
    
#     h_bins = [0, 25, 40, 120, 190, 270, 295, 315, 361]
#     s_bins = [0, 0.2, 0.7, 1]
#     v_bins = [0, 0.2, 0.7, 1]

#     hist_h, bin_edges_h = np.histogram(h_channel, bins=h_bins)
#     hist_s, bin_edges_s = np.histogram(s_channel, bins=s_bins)
#     hist_v, bin_edges_v = np.histogram(v_channel, bins=v_bins)

#     concat = np.concatenate((hist_h, hist_s, hist_v))

#     return concat

# def create_histogram(img_path):
#     hsv_image = imt.RGBtoHSV(imt.ImageToMatrix(img_path))
#     hist_hue = cv2.calcHist([hsv_image], [0], None, [8], [0, 360]).flatten()
#     hist_saturation = cv2.calcHist([hsv_image], [1], None, [3], [0, 256]).flatten()
#     hist_value = cv2.calcHist([hsv_image], [2], None, [3], [0, 256]).flatten()
    
#     hist_combined = np.concatenate((hist_hue, hist_saturation, hist_value))
    
#     return hist_combined

def create_histogram(img_path):
    hsv_image = imt.RGBtoHSV(imt.ImageToMatrix(img_path))
    
    height, width = hsv_image.shape[:2]
    segment_height = height // 4
    segment_width = width // 4
    
    hist_per_segments = []
    for i in range(4):
        for j in range(4):
            segment = hsv_image[i*segment_height:(i+1)*segment_height,
                                j*segment_width:(j+1)*segment_width]
            hist_hue = cv2.calcHist([segment], [0], None, [8], [0, 360]).flatten()
            hist_saturation = cv2.calcHist([segment], [1], None, [3], [0, 1]).flatten()
            hist_value = cv2.calcHist([segment], [2], None, [3], [0, 1]).flatten()
            hist_combined = np.concatenate((hist_hue, hist_saturation, hist_value))
            hist_per_segments.append(hist_combined.tolist())
    
    return hist_per_segments

def process_colour_image(filename, folder_path):
    img_path = os.path.join(folder_path, filename)
    hist_vector = create_histogram(img_path)
    return {'path': filename, 'histograms': hist_vector}

def DatasetToColourJSON(folder_path, json_path):
    filenames = os.listdir(folder_path)
    data_list = []

    with Pool(processes=os.cpu_count()) as pool:
        results = pool.starmap(process_colour_image, [(filename, folder_path) for filename in filenames])
    
    data_list.extend(results)

    with open(json_path, 'w') as json_file:
        json.dump(data_list, json_file, indent=4)

# def DatasetToColourJSON(folder_path,json_path):
#     data_list = []
#     for filename in os.listdir(folder_path):
#         img_path = os.path.join(folder_path,filename)
#         hist_vector = create_histogram(img_path)
#         img_data = {'path': filename, 'histograms': hist_vector}
#         data_list.append(img_data)
#     with open(json_path, 'w') as json_file:
#         json.dump(data_list, json_file, indent=4)
    
# def SimilarityColour(img_path,colour_json_path,colour_similiar_json_path):
#     data = []
#     with open(colour_json_path) as file:
#         data = json.load(file)
#     image_hist = create_histogram(img_path)
#     similarities = []
#     for img_dataset in data:
#         vector_dataset = np.array(img_dataset['histogram'])
#         similarity = cs.cosine_similiarity(image_hist,vector_dataset)
#         if similarity >= 0.6:
#             similarities.append({'path': img_dataset['path'], 'similarity': similarity})
#     similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)
#     with open(colour_similiar_json_path, 'w') as file:
#         json.dump(similarities, file, indent=4)

def SimilarityColour(img_path, colour_json_path, colour_similar_json_path):
    data = []
    with open(colour_json_path) as file:
        data = json.load(file)
    
    image_hists = create_histogram(img_path)
    
    similarities = []
    for img_dataset in data:
        segment_similarities = []
        for segment_hist_uploaded, segment_hist_dataset in zip(image_hists, img_dataset['histograms']):
            similarity = cs.cosine_similiarity(segment_hist_uploaded, segment_hist_dataset)
            segment_similarities.append(similarity)
        
        avg = np.mean(segment_similarities)
        similarities.append({'path': img_dataset['path'], 'similarity': avg})

    similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)
    
    with open(colour_similar_json_path, 'w') as file:
        json.dump(similarities, file, indent=4)
if __name__ == '__main__':
    stime = time.time()
    DatasetToColourJSON('src/uploads/multiple_uploads','src/data/colour.json')
    # DatasetToColourJSON('src/function/img','src/data/colour.json')
    SimilarityColour('src/317.jpg','src/data/colour.json', 'src/data/colourSimilarity.json')
    ftime = time.time()
    print("Runtime: ", ftime-stime)
