import cv2
import numpy as np
from scipy.ndimage import convolve
import sys

def binary_threshold(img):

    assert len(img.shape)==2
    (thresh, img_bin) = cv2.threshold(img, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    return img_bin

def canny_edge(img):
    assert len(img.shape) == 2

    edge_img = cv2.Canny(img,100,200)

    return edge_img

def crop_image_to_quarter(img,quarter):

    set_of_permissible_quarters = {'NW','NE','SW','SE'}
    assert quarter in set_of_permissible_quarters

    y_len = img.shape[0]
    mid_y_len = int(0.5*y_len)

    x_len = img.shape[1]
    mid_x_len = int(0.5*x_len)

    if(quarter=='NW'):
        cropped_img = img[0:mid_y_len,0:mid_x_len]
    elif(quarter=='NE'):
        cropped_img = img[0:mid_y_len,mid_x_len:]
    elif(quarter=='SW'):
        cropped_img = img[mid_y_len:,0:mid_x_len]
    else:
        cropped_img = img[mid_y_len:,mid_x_len:]

    return cropped_img

def crop_image_to_half(img,axis,half):

    set_of_axes = {'x','y'}
    set_of_y_halves = {'top','bottom'}
    set_of_x_halves = {'left','right'}

    y_len = img.shape[0]
    mid_y_len = int(0.5 * y_len)

    x_len = img.shape[1]
    mid_x_len = int(0.5 * x_len)


    assert axis in set_of_axes

    if(axis == 'y'):
        assert half in set_of_y_halves
        if(half=='top'):
            return img[0:mid_y_len]
        else:
            return img[mid_y_len:]


    else:
        assert half in set_of_x_halves
        if(half=='left'):
            return img[:,0:mid_x_len]
        else:
            return img[:,mid_x_len:]

def crop_image_to_percent(img,axis,part_image,percentage):

    set_of_axes = {'x','y'}
    set_of_y_parts = {'top','bottom'}
    set_of_x_parts = {'left','right'}

    if(percentage>1):
        percentage = percentage/100.0

    y_len = img.shape[0]
    x_len = img.shape[1]

    assert axis in set_of_axes

    if(axis == 'y'):
        assert part_image in set_of_y_parts
        if (part_image == 'top'):
            return img[0:int(percentage*y_len)]
        else:
            return img[int((1-percentage)*y_len):]


    else:
        assert part_image in set_of_x_parts
        if(part_image=='left'):
            return img[:,0:int(percentage*x_len)]
        else:
            return img[:,int((1-percentage)*x_len):]

def crop_window_from_image(image,x_limits,y_limits):

    assert y_limits[0]<y_limits[1]
    assert x_limits[0]<x_limits[1]

    return image[y_limits[0]:y_limits[1],x_limits[0]:x_limits[1]]

def draw_rectangle_on_image(image,x_limits,y_limits):
    assert y_limits[0]<y_limits[1]
    assert x_limits[0]<x_limits[1]

    pt1 = (x_limits[0],y_limits[0])
    pt2 = (x_limits[1],y_limits[1])
    return cv2.rectangle(image, pt1,pt2,(0, 255, 0), 3)

def trim_edges_of_image(image,pixels=10):

    return image[pixels:-pixels, pixels:-pixels]


def get_boxes_in_image(bin_img):


    vertical_kernel_length_erode = int(bin_img.shape[1]/50)
    vertical_kernel_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (1, vertical_kernel_length_erode))
    vertical_kernel_length_dilate = 10
    vertical_kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT,(1,vertical_kernel_length_dilate))

    horizontal_kernel_length_erode = int(bin_img.shape[0]/5)
    horizontal_kernel_erode = cv2.getStructuringElement(cv2.MORPH_RECT, (horizontal_kernel_length_erode, 1))
    horizontal_kernel_length_dilate = 100
    horizontal_kernel_dilate = cv2.getStructuringElement(cv2.MORPH_RECT,(horizontal_kernel_length_dilate,1))


    iterations = 1
    # Morphological operation to detect vertical lines from an image
    img_temp_vertical = cv2.erode(bin_img, vertical_kernel_erode, iterations=iterations)
    vertical_lines_img = cv2.dilate(img_temp_vertical, vertical_kernel_dilate, iterations=iterations)

    # Morphological operation to detect horizontal lines from an image
    img_temp_horizontal = cv2.erode(bin_img, horizontal_kernel_erode, iterations=iterations)
    horizontal_lines_img = cv2.dilate(img_temp_horizontal, horizontal_kernel_dilate, iterations=iterations)

    # kernel = cv2.getStructuringElement(cv2.MORPH_RECT,(2,2))

    alpha = 0.5
    beta = 1.0 - alpha

    # This function helps to add two image with specific weight parameter to get a third image as summation of two image.
    img_final_bin = cv2.addWeighted(vertical_lines_img, alpha, horizontal_lines_img, beta, 0.0)

    # img_final_bin = cv2.dilate(img_final_bin, kernel, iterations=iterations)

    (thresh, img_final_bin) = cv2.threshold(img_final_bin, 128, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    return img_final_bin

def get_vertical_line_stats_in_x_axis(bin_img):

    assert (len(np.unique(bin_img)) <= 2)

    vertical_kernel_length = int(bin_img.shape[0])
    vertical_kernel = np.ones((vertical_kernel_length,1))

    list_stats = []

    for i in range(0,bin_img.shape[1]):
        column = bin_img[:,i]
        column_convolve = (vertical_kernel*column)/(vertical_kernel_length*255)
        sum = np.sum(column_convolve)
        list_stats.append(sum)

    array_stats = np.array(list_stats).reshape(1,bin_img.shape[1])

    return array_stats

def get_horizontal_line_stats_in_y_axis(bin_img):

    assert (len(np.unique(bin_img)) <= 2)

    horizontal_kernel_length = int(bin_img.shape[1])
    horizontal_kernel = np.ones((1,horizontal_kernel_length))

    list_stats = []

    for i in range(0, bin_img.shape[0]):
        row = bin_img[i,:]
        column_convolve = (horizontal_kernel * row) / (horizontal_kernel_length * 255)
        sum = np.sum(column_convolve)
        list_stats.append(sum)

    array_stats = np.array(list_stats).reshape(bin_img.shape[0],1)

    return array_stats



