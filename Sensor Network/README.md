

## Sensor Network
![](https://cdn-reichelt.de/bilder/web/xxl_ws/A300/SBC-NODEMCU-ESP32-01.png)
![](https://github.com/kaiwen98/spacey/blob/master/images/sensormote.png)


### Introduction
   A “Wireless Sensor Network” will be set up such that the network of sensors will span over the seats in a restaurant establishment. The area will be divided into individual clusters whereby the cluster head sensor node will consolidate the data from the cluster nodes in regular time intervals and relay the information to a server connected to the same wireless network.
  <br> The occupancy status of a table is signalled by contact sensors attached to each seat around the table, whereby a customer sitting on it will trigger a change in signal sent from the cluster sensor node to the cluster head node. </br>
  
### Implementation
  The implementation will be realized with **ESP32 microcontrollers** with **WIFI** and **Bluetooth capabilities**. We plan to implement communication within cluster with BLE star topology network cluster, while cluster head to PAN coordinator communication will be executed via a WIFI network. 
  <br>The occupance of the seat will be detected via a simple switch with two seperated copper contacts, whereby upon being sat upon will cause them to come into contact and close the circuit, thereby relaying an electrical signal to one of the digital input pins on the ESP32. </br>

### Milestone 1 Update
  We have ordered the parts from our suppliers but it has not arrived in Singapore yet. As such, we are unable to produce any code without having understood in detail the implementation of the code libraries in the folder. However, we will put forth our basic description of the workflow of the software: 
 * The cluster nodes will be put to sleep mode unless someone sits on the switch, hence triggering it to be awaken from sleep mode and relays the respective seat ID to the cluster head sensor. 
 * The cluster heads will consolidate the data within its cluster in 5 minute intervals and relay information to the PAN coordinator (Laptop)

 * The PAN coordinate will consolidate the data from the cluster heads and convert the data into a CSV file to be stored in the database to be retrieved by the Telegram Bot.
