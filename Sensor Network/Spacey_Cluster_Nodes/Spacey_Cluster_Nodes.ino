
/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleServer.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updates by chegewara
*/
/*
#include <constants.h>
#include <packet.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <stdint.h>
#include "TouchSensor.h"
#include "esp_system.h"
#include "esp_bt.h"

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
static bool constant = true;
TouchSensor myTouch(4, 40, 5);
const int wdtTimeout = 15000;  //time in ms to trigger the watchdog
hw_timer_t *timer = NULL;
static int sleepMode = 1;


BLECharacteristic *pCharacteristic;
BLEService *pService;


class myServerCallbacks: public BLEServerCallbacks{
  void onDisconnect(BLEServer* pserver){
    Serial.println("Disconnected");
    sleepMode++;
  }
};

void wakeUp(){
  Serial.println("Wake Up");
  sleepMode = 0;
  Serial.println("Done");
}





void BLEServerInit(){
  BLEDevice::init("");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new myServerCallbacks());
  pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                                         CHARACTERISTIC_UUID,
                                         BLECharacteristic::PROPERTY_READ |
                                         BLECharacteristic::PROPERTY_WRITE
                                       );

  //pCharacteristic->setValue("0");
  //pService->start();
  // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  // spacey
  BLEAdvertisementData pAdvertisingData;
  pAdvertisingData.setName("Macdonalds2 - NUS");
  pAdvertisingData.setClusterNum("7");
  pAdvertising->setScanResponseData(pAdvertisingData);
  
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMinPreferred(0x12);
  

  Serial.println("Characteristic defined! Now you can read it in your phone!");
}

void IRAM_ATTR resetModule() {
  Serial.println("reboot");
  //ets_printf("reboot\n");
  if(!sleepMode) esp_restart();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting BLE work!");
  Serial.println(sleepMode);
  esp_sleep_enable_touchpad_wakeup();
  if(touchRead(T0) < 40 ) sleepMode = 0;

}

void loop() {
  if(sleepMode) {
    esp_bt_controller_disable();
    touchAttachInterrupt(T0, wakeUp, 40);
    
  }
  
  else {
    timer = timerBegin(0, 80, true);                  //timer 0, div 80
    timerAttachInterrupt(timer, &resetModule, true);  //attach callback
    timerAlarmWrite(timer, wdtTimeout * 1000, false); //set time in us
    timerAlarmEnable(timer);                          //enable interrupt
    BLEServerInit();
  
    pService->start();
    pCharacteristic->setValue("0");
    BLEDevice::startAdvertising();
  }
  
  if(sleepMode) {
     Serial.println("Entering deep sleep");
     esp_deep_sleep_start();
  }
  
  else {
    timerWrite(timer, 0); //reset timer (feed watchdog)
    constant = true;
      while(constant){
        timerWrite(timer, 0); //reset timer (feed watchdog)
        constant = false;
        switch(myTouch.getTouchState()){
          case SEAT_OCCUPIED:
            Serial.println("Seat occupied");
            BLEDevice::deinit();
            BLEServerInit();
            
            pCharacteristic->setValue("1");
            BLEDevice::startAdvertising();
            pService->start();
          break;
          
          case SEAT_FREE:
            Serial.println("Seat freed");
            BLEDevice::deinit();
            BLEServerInit();
            
            pCharacteristic->setValue("0");
            BLEDevice::startAdvertising();
            pService->start();
          break;
          
          default: 
            constant = true;
          break;
        }
        delay(500);
      }
  }
  
  // put your main code here, to run repeatedly:
  
}
*/









/*
    Based on Neil Kolban example for IDF: https://github.com/nkolban/esp32-snippets/blob/master/cpp_utils/tests/BLE%20Tests/SampleServer.cpp
    Ported to Arduino ESP32 by Evandro Copercini
    updates by chegewara
*/
#include <constants.h>
#include <packet.h>
#include <BLEDevice.h>
#include <BLEUtils.h>
#include <BLEServer.h>
#include <stdint.h>
#include "TouchSensor.h"
#include "esp_system.h"
#include "esp_bt.h"

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/

#define SERVICE_UUID        "4fafc201-1fb5-459e-8fcc-c5c9c331914b"
#define CHARACTERISTIC_UUID "beb5483e-36e1-4688-b7f5-ea07361b26a8"
static bool constant = true;
TouchSensor myTouch(4, 40, 5);
const int wdtTimeout = 15000;  //time in ms to trigger the watchdog
hw_timer_t *timer = NULL;
static int sleepMode = 1;


BLECharacteristic *pCharacteristic;
BLEService *pService;


class myServerCallbacks: public BLEServerCallbacks{
  void onDisconnect(BLEServer* pserver){
    Serial.println("Disconnected");
    sleepMode++;
  }
};



void BLEServerInit(){
  BLEDevice::init("");
  BLEServer *pServer = BLEDevice::createServer();
  pServer->setCallbacks(new myServerCallbacks());
  pService = pServer->createService(SERVICE_UUID);
  pCharacteristic = pService->createCharacteristic(
                                         CHARACTERISTIC_UUID,
                                         BLECharacteristic::PROPERTY_READ |
                                         BLECharacteristic::PROPERTY_WRITE
                                       );

  //pCharacteristic->setValue("0");
  //pService->start();
  // BLEAdvertising *pAdvertising = pServer->getAdvertising();  // this still is working for backward compatibility
  BLEAdvertising *pAdvertising = BLEDevice::getAdvertising();
  // spacey
  BLEAdvertisementData pAdvertisingData;
  pAdvertisingData.setName("Macdonalds2 - NUS");
  pAdvertisingData.setClusterNum("7");
  pAdvertising->setScanResponseData(pAdvertisingData);
  
  pAdvertising->addServiceUUID(SERVICE_UUID);
  pAdvertising->setScanResponse(true);
  pAdvertising->setMinPreferred(0x06);  // functions that help with iPhone connections issue
  pAdvertising->setMinPreferred(0x12);
  

  Serial.println("Characteristic defined! Now you can read it in your phone!");
}

void IRAM_ATTR resetModule() {
  Serial.println("reboot");
  //ets_printf("reboot\n");
  if(!sleepMode) esp_restart();
}

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Starting BLE work!");
  timer = timerBegin(0, 80, true);                  //timer 0, div 80
  timerAttachInterrupt(timer, &resetModule, true);  //attach callback
  timerAlarmWrite(timer, wdtTimeout * 1000, false); //set time in us
  timerAlarmEnable(timer);                          //enable interrupt
  BLEServerInit();
  
  pService->start();
  pCharacteristic->setValue("0");
  BLEDevice::startAdvertising();

}

void loop() {

    timerWrite(timer, 0); //reset timer (feed watchdog)
    constant = true;
      while(constant){
        timerWrite(timer, 0); //reset timer (feed watchdog)
        constant = false;
        switch(myTouch.getTouchState()){
          case SEAT_OCCUPIED:
            Serial.println("Seat occupied");
            BLEDevice::deinit();
            BLEServerInit();
            
            pCharacteristic->setValue("1");
            BLEDevice::startAdvertising();
            pService->start();
          break;
          
          case SEAT_FREE:
            Serial.println("Seat freed");
            BLEDevice::deinit();
            BLEServerInit();
            
            pCharacteristic->setValue("0");
            BLEDevice::startAdvertising();
            pService->start();
          break;
          
          default: 
            constant = true;
          break;
        }
        delay(500);
      }
 
  
  // put your main code here, to run repeatedly:
  
}
