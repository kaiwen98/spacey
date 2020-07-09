# 5c98e2

from PIL import Image, ImageDraw, ImageFilter
import os
import config as cfg


def imagegen():
    #cfg.decompile(cfg.json_path)

    floorplan_path = cfg.postimgpath

    node_off = Image.open(cfg.nodeOff_path)
    node_off = node_off.resize((int(cfg.box_len*2.5), cfg.box_len*2))
    node_on = Image.open(cfg.nodeOn_path)
    node_on = node_on.resize((int(cfg.box_len*2.5), cfg.box_len*2))

    cfg.canvas_xlen = cfg.x_bb2 - cfg.x_bb1
    cfg.canvas_ylen = cfg.y_bb2 - cfg.y_bb1
    cfg.img_x_bb1 -= cfg.x_bb1
    cfg.img_y_bb1 -= cfg.y_bb1

    bg = Image.new('RGBA', (cfg.canvas_xlen, cfg.canvas_ylen), (92, 152, 226, 255))
    floorplan = Image.open(floorplan_path)

    datas = floorplan.getdata()
    newData = []
    for item in datas:
        if item[3] > 100:
            #newData.append((51,82,133,255))
            newData.append((50,50,50,255))
        else:
            newData.append((0, 0, 0, 0))
    floorplan.putdata(newData)

    bg.paste(floorplan, (cfg.img_x_bb1, cfg.img_y_bb1), mask = floorplan)
    #bg.paste(floorplan, (0,0), mask = floorplan)



    for i in cfg.res.idxList:
        x = cfg.res.x_coord[i]- (cfg.x_bb1 + cfg.box_len)
        y = cfg.res.y_coord[i] - (cfg.y_bb1 + cfg.box_len)

        if cfg.res.occupancy[i]: node = node_on
        else: node = node_off
        bg.paste(node, (int(x),int(y)))

    #bg.paste(node_off,(0, 0))
    #bg.paste(node_off,(100, 500))
    bg.show()
    bg.save(cfg.save_path(), quality=95, format = "PNG")

