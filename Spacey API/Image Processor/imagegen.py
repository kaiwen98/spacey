# 5c98e2

from PIL import Image, ImageDraw, ImageFilter
import os
import p_config as cfg


def imagegen():
    

    node_off = Image.open(cfg.nodeOff_path)
    node_off = node_off.resize((int(cfg.box_len*2.5), cfg.box_len*2))
    node_on = Image.open(cfg.nodeOn_path)
    node_on = node_on.resize((int(cfg.box_len*2.5), cfg.box_len*2))

    bg = Image.open(cfg.save_path())

    for i in cfg.occupancy.keys():
        if cfg.occupancy[i]: node = node_on
        else               : node = node_off
        coord = cfg.json_coord[i].rsplit(',')
        x = coord[0]
        y = coord[1]
        bg.paste(node, (int(x),int(y)))

    #bg.paste(node_off,(0, 0))
    #bg.paste(node_off,(100, 500))
    bg.show()

    bg.save(cfg.get_output_graphic_path(), quality=95, format = "PNG")


