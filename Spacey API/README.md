

## Node Manager
<img src = https://github.com/kaiwen98/spacey/blob/master/images/gui%20scrnshot.png>

### Introduction
   A Node manager is set up to allow network administrators to synchronise the geographical location of the sensors in the restaurant spaces with database, which can allow the image procesor code to generate the image to reflect the istribution of occupied seats which will be relayed to the client.
  <br> You can run Spacey Admin/admin_map_creator.py to perform left click to move the cursor throughout the map, and then right click to deposit a sensor node where the cursor is. Then, you can revisit the node information by placing the cursor over a placed node. </br>
  <br> The Node manager has a save/load feature, whereby you can save your work in a json file which can be loaded in another time to continue. The json file of the completed project is then used to generate an image template using the Image Processor. </br>
  
## Image Processor
<img src = https://github.com/kaiwen98/spacey/blob/master/Spacey%20API/Image%20Processor/images/output%20graphic/output_lol.png>

### Introduction
   The image processor imports the relevant JSON file from the node manager to initialize the map in the respectory file directory into a PNG file. Thereafter, any updates in status of the seats will result in changes in the color of the respective seat and a corresponding update in the map.
