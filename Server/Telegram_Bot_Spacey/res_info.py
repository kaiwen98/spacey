import imagegen as img
import config as cfg

class restaurant_info(object):
    def __init__(self, name, occupancy, coord, img_path, box_len, serialized_img):
        self.name = name
        self.image = img_path
        self.occupancy = occupancy
        self.coord = coord
        self.box_len = box_len
        self.temp = None
        self.node_on = None
        self.node_off = None
        self.serialized_img = serialized_img
        img.imagegen(self)

    def update_img(self):
        coord = {}
        full_name_coord = self.name + "_coord" 
        coord = cfg.database.client.hgetall(full_name_coord)

        if self.serialized_img != coord["processed_img"]:
            print("image changed!")
            cfg.json_deserialize_image(coord["processed_img"], cfg.get_output_graphic_path(self.name))
            self.occupancy = cfg.database.client.hgetall(self.name + "_occupancy")
            del coord["processed_img"]
            self.box_len = int(coord["box_len"])
            del coord["box_len"]
            self.coord.clear()
            self.coord = coord.copy()

        else: 
            print("no change!")