# 5c98e2

from PIL import Image, ImageDraw, ImageFilter
import os
import config as cfg
import res_info as res


def imagegen(res_info):

    node_off = Image.open(cfg.nodeOff_path)
    node_off = node_off.resize((int(res_info.box_len*2.5), res_info.box_len*2))
    node_on = Image.open(cfg.nodeOn_path)
    node_on = node_on.resize((int(res_info.box_len*2.5), res_info.box_len*2))

    res_info.node_on = node_on
    res_info.node_off = node_off

    print("cfg.box_len: ", res_info.box_len)
    bg = Image.open(res_info.image)
    print(res_info.name)
    print(res_info.coord)
    print(res_info.occupancy)
    for i in res_info.coord.keys():
        x = res_info.coord[str(i)].rsplit(',')[0]
        y = res_info.coord[str(i)].rsplit(',')[1]
        #print(x, type(x))
        #print("key: ", str(i))

        if int(res_info.occupancy[str(i)]) == 0: node = node_on
        else: node = node_off
        bg.paste(node, (int(x),int(y)))
    print(bg.size)
    bg.show()
    bg.save(res_info.image, quality=95, format = "PNG")

def imageupdate(res_info, occupancy_new):
    node_on = res_info.node_on 
    node_off = res_info.node_off 

    res_info.temp = Image.open(res_info.image)
    for i in res_info.occupancy.keys():
        if res_info.occupancy[i] != occupancy_new[i]:
            if int(occupancy_new[i]): node = node_on
            else                         : node = node_off
            x = res_info.coord[i].rsplit(',')[0]
            y = res_info.coord[i].rsplit(',')[1]
            res_info.temp.paste(node, (int(x), int(y)))
            res_info.occupancy[i] = occupancy_new[i]
    res_info.temp.show()
    #save_graphic(res_info)
    

# commit changes in occupancy to image to present.
def save_graphic(res_info):
    res_info.temp.save(res_info.image, quality=95, format = "PNG")