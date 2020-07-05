# 5c98e2

from PIL import Image, ImageDraw, ImageFilter
import os
import p_config as cfg

cfg.decompile("lol1.json")
path = os.getcwd()
path = os.path.join(path, "images")
nodeOff_path = os.path.join(path, "unoccupied_nodes.png")
nodeOn_path = os.path.join(path, "occupied_nodes.png")
floorplan_path = cfg.postimgpath

node_off = Image.open(nodeOff_path)
node_off = node_off.resize((int(cfg.box_len*2.5), cfg.box_len*2))
node_on = Image.open(nodeOn_path)
node_on = node_on.resize((int(cfg.box_len*2.5), cfg.box_len*2))

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

    x = cfg.res.x_coord[i]
    y = cfg.res.y_coord[i]

    if cfg.res.occupied[i]: node = node_on
    else: node = node_off
    bg.paste(node, (int(x),int(y)))

#bg.paste(node_off,(0, 0))
#bg.paste(node_off,(100, 500))
bg.show()
bg.save('test.png', quality=95, format = "PNG")

