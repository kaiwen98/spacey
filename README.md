# SPACEY: IoT Solution for occupancy management in restaurant chains
![](https://img.theculturetrip.com/wp-content/uploads/2018/05/de4wxm.jpg)


## How to use:
* [**Telegram Bot**](https://github.com/kaiwen98/spacey/tree/master/Server)
  <br>You can try our bot right now! Our bot name is @spaceynusbot. Do let us know what you think! </br><br/>
* [**Node Manager GUI**](https://github.com/kaiwen98/spacey/tree/master/Spacey%20API)
<br>Our latest release is [v1.2.0](https://github.com/kaiwen98/spacey/releases/tag/1.2.0). 
  * Windows Users are to download **Spacey.API.Windows.1.2.0.exe** and run the installation wizard.
  * Linux Users are to download **Spacey.API.Linux.1.2.0.zip** and extract it in their working directory, then run **./run.sh** in the **~/Spacey API/** folder.
* [**BLE Sensor Network**](https://github.com/kaiwen98/spacey/tree/master/Sensor%20Network/SpaceyNodes)
<br>You will need to have the following setup:</br>
  * Install [Arduino IDE](https://www.arduino.cc/en/main/software)
  * Install [Arduino-ESP32 Libraries](https://github.com/espressif/arduino-esp32)
  * Own at least 2 ESP32 SoC microcontrollers

## Problem Scope and Motivation:
  <p><br> Our target problem is commonplace throughout Singapore - During mealtimes, customers often arrive at their favourite eateries only to discover that there are no more seats available for them. They either have to waste time looking for another eatery, or stand around to wait until the other customers are done with their meal. </br>
  <br> This is a very common problem in large-scale and popular hawker centres such as Chomp Chomp and Bukit Merah Hawker centre, whereby a seat reservation and tracking systems are not implemented unlike restaurants such as Saboten and Andes. </br>
 	<br> The scope of the problem in which we wish to target  are hawker centres, fast food chains and coffee houses in NUS, whereby there is frequent occurrences of overcrowding due to high influx of customers. That being said, our implementation can easily be expanded out to higher level purposes such as business analytics, traffic monitoring and crowd control. </br> 
  

## Sensor Network
![](https://cdn-reichelt.de/bilder/web/xxl_ws/A300/SBC-NODEMCU-ESP32-01.png)
### Introduction
   A “Wireless Sensor Network” will be set up such that the network of sensors will span over the seats in a restaurant establishment. The area will be divided into individual clusters whereby the cluster head sensor node will consolidate the data from the cluster nodes in regular time intervals and relay the information to a server connected to the same wireless network.
  <br> The occupancy status of a table is monitored by contact sensors attached to each seat around the table, whereby a customer sitting on it will trigger a change in signal sent from the cluster sensor node to the cluster head node. </br>
  
### Implementation
  The implementation will be realized with **ESP32 microcontrollers** with **WIFI** and **Bluetooth capabilities**. We plan to implement communication within cluster with BLE star topology network cluster, while the updating of the remote database will be done over WiFi by the cluster head node. 
  <br>The occupancy of the seat is detected by a simple capacitive touch sensor, which is cheap to make and does not cause discomfort to the customers.  </br>

## Telegram Bot
![](https://lh3.googleusercontent.com/ZU9cSsyIJZo6Oy7HTHiEPwZg0m2Crep-d5ZrfajqtsH-qgUXSqKpNA2FpPDTn-7qA5Q)
### Introduction
Provides a convenient and user-friendly interface for students to check for updates regarding available seats, on one of the most popular messaging platform in the university. 
<br>The telegram bot offers not only restaurant occupancy updates, but also provides notification services and data analytics features for business owners and casual users alike.</br>
  
### Implementation
  The bot is written in Python with the use of a plethora of libraries, from python-telegram-bot to matplotlib. As of now, it is hosted on Heroku and is currently accessible at @spaceynusbot. You can also use the software from our latest release to generate your own floor plan!
  
## Node Manager
<img src = https://github.com/kaiwen98/spacey/blob/master/images/gui%20scrnshot.png>

### Introduction
   A Node manager is set up to allow network administrators to synchronise the geographical location of the sensors in the restaurant spaces with database, which can allow the image procesor code to generate the image to reflect the istribution of occupied seats which will be relayed to the client.
  <br> You can download the software from our latest release to create your own output graphic from floor plan files! </br>


  
  
