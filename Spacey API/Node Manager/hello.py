import json
import base64
import os
from os.path import dirname as dir
from PIL import Image

_root = dir(os.getcwd())

image_path = os.path.join(_root, "floorplan_images", "output floorplan")
new_path = os.path.join(image_path, "processed_img_from_hell.png")
sample_path = os.path.join(image_path, "processed_img_.png")
json_path = os.path.join(_root, "test_img.json")
data = {}

def json_serialize_image(image_file, data):
    with open(image_file, mode='rb') as file:
        img = file.read()
    data['img'] = base64.b64encode(img).decode("utf-8") #picture to bytes, then to string 

def json_deserialize_image(image_file, data):
    result = data['img'].encode("utf-8")
    result = base64.b64decode(result)
    image_result = open(image_file, 'wb') # create a writable image and write the decoding result
    image_result.write(result)



if __name__ == "__main__":
    data = {}
    json_serialize_image(sample_path, data)
    with open(json_path, 'w') as outfile:
        json.dump(data, outfile)
    with open(json_path, 'r') as infile:
        data = json.load(infile)
    json_deserialize_image(new_path, data)
    node_off = Image.open(new_path)
    node_off.show()