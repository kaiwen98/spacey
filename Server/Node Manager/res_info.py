import imagegen as img

class restaurant_info(object):
    def __init__(self,name, occupancy, coord, img_path, box_len):
        self.name = name
        self.image = img_path
        self.occupancy = occupancy
        self.coord = coord
        self.box_len = box_len
        self.temp = None
        self.node_on = None
        self.node_off = None
        img.imagegen(self)
