import ImageToMatrix as imt

def create_histogram(img_path):
    hsv_matrix = RGBtoHSV(ImageToMatrix(img_path))
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

    return concat

def DatasetToColourJSON(folder_path,json_path):
    data_list = []
    for filename in os.listdir(folder_path):
        img_path = os.path.join(folder_path,filename)
        hist_vector = create_histogram(img_path)
        img_data = {'path': filename, 'histogram': hist_vector}
        data_list.append(img_data)
    json_string = json.dumps(data_list)
    with open(json_path, 'w') as json_file:
        json_file.write(json_string)
