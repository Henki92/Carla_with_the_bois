import numpy as np


class DetectedObject:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.x = []
        self.y = []


def find_bounding_boxes(input_image):

    print("Input image shape", input_image.shape)
    image_height, image_width, image_channels = input_image.shape

    OD_object_list = [DetectedObject()]

    for row in range(0, image_height):
        for col in range(0, image_width):
            if input_image[row, col, 2] == 10:
                found_flag = False
                for i, OD_object in enumerate(OD_object_list):
                    if not OD_object.x:
                        print("Found first object at pixel col: ", col, "and row: ", row)
                        OD_object.x.append(col)
                        OD_object.y.append(row)
                        break
                    for num_pixels in range(len(OD_object.x)):
                        dist = np.sqrt(np.square(col - OD_object.x[num_pixels]) + np.square(row - OD_object.y[num_pixels])) # Euclidean distance
                        if dist < 25:# If the discovered point is within threshold amound of pixels assume it belong to same car
                            OD_object.x.append(col)
                            OD_object.y.append(row)
                            found_flag = True
                            break
                    if found_flag:
                        break
                if not found_flag:
                    if i == len(OD_object_list) - 1:
                        print("Found another object at pixel col: ", col, "and row: ", row)
                        OD_object_list.append(DetectedObject())
                        OD_object_list[-1].x.append(col)
                        OD_object_list[-1].y.append(row)
                        print("Number of objects:", len(OD_object_list))
                    break

    # Remove boxes that have odd ratio and are too small to be worth it
    for OD_object in OD_object_list:
        if max(OD_object.x) - min(OD_object.x) < 50:
            OD_object_list.remove(OD_object)
            break
        if max(OD_object.y) - min(OD_object.y) < 50:
            OD_object_list.remove(OD_object)
            break
        if (max(OD_object.x) - min(OD_object.x)) / (max(OD_object.y) - min(OD_object.y)) > 1.5:
            OD_object_list.remove(OD_object)

    return OD_object_list





