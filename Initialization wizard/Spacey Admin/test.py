from PIL import Image, ImageEnhance, ImageOps
import os
path = os.getcwd()

image_path = os.path.join(path, "images")
print(image_path)

image_file = os.path.join(image_path, "floor_plan4.png")

img = Image.open(image_file)
img = img.convert("RGBA")
enhancer = ImageEnhance.Contrast(img)
img = enhancer.enhance(10)
enhancer = ImageEnhance.Sharpness(img)
img = enhancer.enhance(10)

img.show()

datas = img.getdata()

newData = []
for item in datas:
    if item[0] < 5 and item[1] < 5 and item[2] < 5 and item[3] != 0:
        newData.append((0,0,0,255))
    else:
        newData.append((255, 255, 255, 0))
        

img.putdata(newData)
new_image_file = os.path.join(image_path, "image_edited4.png")
print(new_image_file)
img.save(new_image_file,"PNG")