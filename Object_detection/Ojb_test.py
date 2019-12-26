import cv2
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


input_image = cv2.imread('Object_detection.png')
print('Image Dimensions :', input_image.shape)
IM_HEIGHT, IM_WIDTH, IM_CHANNELS = input_image.shape
i = np.array(input_image)
i2 = i.reshape((IM_HEIGHT, IM_WIDTH, 3))
i3 = i2[:, :, :3]


OD_object_list = find_bounding_boxes(i3)
print("Objects found after clear: ", len(OD_object_list))
image = input_image[:, :, :]


list_of_pixel_coord_with_cars = np.where(image == 10)
coord = list(zip(list_of_pixel_coord_with_cars[0], list_of_pixel_coord_with_cars[1]))
print(coord)
disp_image = np.copy(image)
for row, col in coord:
    disp_image[row, col] = 100

cv2.imshow("Highlight", disp_image)
cv2.imwrite('Objet_detection_highlight.png', disp_image)
cv2.waitKey(1000)


print("Finished analysis")
print("Result is:")
print("Number of objects:", len(OD_object_list))
for i, obj in enumerate(OD_object_list):
    print("Object: ", i)
    print("x min: ", min(obj.x), "x max:", max(obj.x))
    print("y min: ", min(obj.y), "y max:", max(obj.y))

# Draw bounding boxes
for obj in OD_object_list:
    result = cv2.rectangle(disp_image, (min(obj.x), min(obj.y)), (max(obj.x), max(obj.y)), (0, 0, 255), 3, cv2.LINE_AA)

cv2.imshow("Result image", disp_image)
cv2.waitKey(0)




