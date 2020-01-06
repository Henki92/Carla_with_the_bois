import cv2
import numpy as np
import progressbar


input_image = cv2.imread('Object_detection.png')
print('Image Dimensions :', input_image.shape)
image_height, image_width, image_channels = input_image.shape
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


class DetectedObject:
    def __init__(self):
        self.width = 0
        self.height = 0
        self.x = []
        self.y = []


OD_object_list = [DetectedObject()]


for row in range(0, image_height):
    for col in range(0, image_width):
        if image[row, col, 2] == 10:
            b = 1
            for i, OD_object in enumerate(OD_object_list):
                if len(OD_object_list) == 2 and i == 1:
                    b = 1
                if not OD_object.x:
                    OD_object.x.append(col)
                    OD_object.y.append(row)
                    break
                if OD_object.x[0] - 15 <= col <= OD_object.x[-1] + 15:
                    if OD_object.y[0] - 15 <= row <= OD_object.y[-1] + 15:
                        OD_object.x.append(col)
                        §.y.append(row)
                        break
                    else:
                        if i == len(OD_object_list) - 1:
                            print("obj- 1 = ", OD_object.y[-1] - 1, "row: ", row, "OBJ + 1:",  OD_object.y[-1] + 1)
                            OD_object_list.append(DetectedObject())
                            OD_object_list[-1].x.append(col)
                            OD_object_list[-1].y.append(row)
                        break
                else:
                    if i == len(OD_object_list) - 1:
                        print("obj - 1 = ", OD_object.x[-1] - 1, "col: ", col, "OBJ + 1:", OD_object.x[-1] + 1)
                        OD_object_list.append(DetectedObject())
                        OD_object_list[-1].x.append(col)
                        OD_object_list[-1].y.append(row)
                        print(len(OD_object_list))
                    break

print("Finished analysis")
print("Result is:")
print("Number of objects:", len(OD_object_list))
for obj in OD_object_list:
    print("x min: ", min(obj.x), "x max:", max(obj.x))
    print("y min: ", min(obj.y), "y max:", max(obj.y))

# Draw bounding boxes
for obj in OD_object_list:
    result = cv2.rectangle(disp_image, (min(obj.x), min(obj.y)), (max(obj.x), max(obj.y)), (0, 0, 255), 3, cv2.LINE_AA)

cv2.imshow("Result image", disp_image)
cv2.waitKey(0)




