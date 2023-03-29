import base64
import cv2

with open("Test.png", "rb") as img_file:
    image = img_file.read()
    b64_string = base64.b64encode(image)

imagecv2 = cv2.imread('Test.png')
print(type(imagecv2))
imagecv2_bytes = imagecv2.tobytes()
print(type(imagecv2_bytes))

b64_string2 = base64.b64encode(imagecv2_bytes)
print(b64_string2)
print(type(b64_string2))

