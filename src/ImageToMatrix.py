import numpy
import cv2

def ImageToMatrix(path):
    img_bgr = cv2.imread(path)
    img_bgr = numpy.array(img_bgr)
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    img_rgb = img_rgb.astype('float64')
    return img_rgb

def RGBtoHSV(r,g,b):
    r = r/255
    g = g/255
    b = b/255
    Cmax = max(r,g,b)
    Cmin = min(r,g,b)
    Delta = Cmax - Cmin
    if Delta == 0:
        h = 0
    elif Delta == r:
        h = 60*(((g-b)/Delta)%6)
    elif Delta == g:
        h = 60*(((b-r)/Delta)+2)
    else:
        h = 60*(((r-g)/Delta)+4)
    
    if Cmax == 0:
        s = 0
    else:
        s = Delta/Cmax
    
    v = Cmax

    return numpy.array([h,s,v])

def RGBtoGrayScale(r,g,b):
    return 0.29*r + 0.587*g + 0.114*b

def matrixRGBTomatrixHSV(matrix_rgb):
    for i in range(matrix_rgb.shape[0]):
        for j in range(matrix_rgb.shape[1]):
            r = matrix_rgb[i][j][0]
            g = matrix_rgb[i][j][1]
            b = matrix_rgb[i][j][2]
            matrix_rgb[i][j] = RGBtoHSV(r,g,b)
    return matrix_rgb