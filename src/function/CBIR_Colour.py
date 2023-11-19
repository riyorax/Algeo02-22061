from function import ImageToMatrix as imt
import numpy as np
import os
import json
import warnings
from function import cosine_similiarity as cs
import cv2
from multiprocessing import Pool

warnings.filterwarnings('ignore')

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
        if avg >= 0.6:
            similarities.append({'path': img_dataset['path'], 'similarity': avg})

    similarities = sorted(similarities, key=lambda x: x['similarity'], reverse=True)
    
    with open(colour_similar_json_path, 'w') as file:
        json.dump(similarities, file, indent=4)


