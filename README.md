# SPACEY: IoT Solution for occupancy management in restaurant chains
![](https://img.theculturetrip.com/wp-content/uploads/2018/05/de4wxm.jpg)

## Problem Scope and Motivation:
  ><br> Our target problem is commonplace throughout Singapore - During mealtimes, customers often arrive at their favourite eateries only to discover that there are no more seats available for them. They either have to waste time looking for another eatery, or stand around to wait until the other customers are done with their meal. </br>
  <br> This is a very common problem in large-scale and popular hawker centres such as Chomp Chomp and Bukit Merah Hawker centre, whereby a seat reservation and tracking systems are not implemented unlike restaurants such as Saboten and Andes. </br>
 	<br> The scope of the problem in which we wish to target  are hawker centres, fast food chains and coffee houses in NUS, whereby there is frequent occurrences of overcrowding due to high influx of customers. That being said, our implementation can easily be expanded out to higher level purposes such as business analytics, traffic monitoring and crowd control. </br> </p> 

## Sensor Network
![](https://cdn-reichelt.de/bilder/web/xxl_ws/A300/SBC-NODEMCU-ESP32-01.png)
### Introduction
   A “Wireless Sensor Network” will be set up such that the network of sensors will span over the seats in a restaurant establishment. The area will be divided into individual clusters whereby the cluster head sensor node will consolidate the data from the cluster nodes in regular time intervals and relay the information to a server connected to the same wireless network.
  <br> The occupancy status of a table is signalled by contact sensors attached to each seat around the table, whereby a customer sitting on it will trigger a change in signal sent from the cluster sensor node to the cluster head node. </br>
  
### Implementation
  The implementation will be realized with **ESP32 microcontrollers** with **WIFI** and **Bluetooth capabilities**. We plan to implement communication within cluster with BLE star topology network cluster, while cluster head to PAN coordinator communication will be executed via a WIFI network. 
  <br>The occupance of the seat will be detected via a simple switch with two seperated copper contacts, whereby upon being sat upon will cause them to come into contact and close the circuit, thereby relaying an electrical signal to one of the digital input pins on the ESP32. </br>


## Telegram Bot
![](https://lh3.googleusercontent.com/ZU9cSsyIJZo6Oy7HTHiEPwZg0m2Crep-d5ZrfajqtsH-qgUXSqKpNA2FpPDTn-7qA5Q)
### Introduction
Provides a convenient and user-friendly interface for students to check for updates regarding available seats, on one of the most popular messaging platform in the university.
  
### Implementation
  The bot is written in Python with the use of Telegram Bot API libraries and MatPlotlib. In its preliminary stage of implementation, it accepts queries from users on the occupany information of a given location, and returns a set of data including:
  * Numerical occupancy status of the restaurant
  * Graphical map of the seats in the resstaurant, with each seat colored according to occupancy
  The query will be identified via push buttons that will appear in the bot chat log for the user to interact with.
  
  
## Database
### Introduction
May be implemented to scale up the project. For now, the information will be stored and relayed in .csv format.
  
### Implementation
We are exploring our options, including Telegram native database, SQLite or MongoDB.

  
  
