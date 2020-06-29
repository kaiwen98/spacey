

## Sensor Network
<img src = https://cdn-reichelt.de/bilder/web/xxl_ws/A300/SBC-NODEMCU-ESP32-01.png>

<img src = https://github.com/kaiwen98/spacey/blob/master/images/sensormote.png width = "100%" height = "100%">



### Introduction
   A “Wireless Sensor Network” will be set up such that the network of sensors will span over the seats in a restaurant establishment. The area will be divided into individual clusters whereby the cluster head sensor node will consolidate the data from the cluster nodes in regular time intervals and relay the information to a server connected to the same wireless network.
  <br> The occupancy status of a table is signalled by contact sensors attached to each seat around the table, whereby a customer sitting on it will trigger a change in signal sent from the cluster sensor node to the cluster head node. </br>
  
### Implementation
  The implementation will be realized with **ESP32 microcontrollers** with **WIFI** and **Bluetooth capabilities**. We plan to implement communication within cluster with BLE star topology network cluster, while cluster head to PAN coordinator communication will be executed via a WIFI network. 
  <br>The occupance of the seat will be detected via a contact with a small loop of wire embedded on the seat, which triggers a register by one of the GPIO capacitive touch register pins on the ESP32, hence breaking it out of rest state and start its communication routine with its immediate cluster head node. </br>

### Milestone 2 Update
  We have successfully implemented the hardware element of the cluster node. Using the ESP-BLE API for C++ framework, the basic server-client GAP communication is implemented in the above code. 
  If you own an ESP32 and wishes to try the program out, you will need to follow the link to install the ESP32-Arduino Library, as well as replacing the installed libraries with our own (We made tweaks to the existing library for our use).
 
