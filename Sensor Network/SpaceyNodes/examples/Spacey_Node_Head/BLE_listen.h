#ifndef __RESET__
#define __RESET__

#include "global.h"

#include <NimBLEDevice.h>
#include "fileIO.h"
#include "global.h"
#include "SpaceyAPI.h"
#include "warning_led.h"
#include "fileIO.h"



BLECharacteristic * pCharacteristic;
bool deviceConnected = false;
bool oldDeviceConnected = false;
sensor_info* myDevice;
NimBLEServer* pServer = nullptr;
uint8_t txValue = 0;

// See the following for generating UUIDs:
// https://www.uuidgenerator.net/


void IRAM_ATTR release() {
      BaseType_t xHigherPriorityTaskWoken = pdFALSE;
      xSemaphoreGiveFromISR( xBinSemaphore, &xHigherPriorityTaskWoken );
      if ( xHigherPriorityTaskWoken == pdTRUE) {
            portYIELD_FROM_ISR(); // this wakes up imu_task immediately instead of on next FreeRTOS tick
      }
}


class MyServerCallbacks: public NimBLEServerCallbacks {
            void onConnect(BLEServer* pServer) {
                  deviceConnected = true;
                  BlinkWarning(200);
            };

            void onDisconnect(NimBLEServer* pServer) {
                  deviceConnected = false;
            }
};


class MyCallbacks: public NimBLECharacteristicCallbacks {
            void onWrite(NimBLECharacteristic *pCharacteristic) {

                  std::string rxValue = pCharacteristic->getValue();

                  if (!myDevice->verifypw(rxValue)) {
                        Serial.println("Unauthorised personnel...");
                        ESP.restart();
                        return;
                  }

                  std::string input = processInput(rxValue);

                  writeToDrive(std::string(input.c_str()));
                  if (rxValue.length() > 0) {
                        Serial.println("*********");
                        Serial.print("Received Value: ");
                        for (int i = 0; i < rxValue.length(); i++)
                              Serial.print(rxValue[i]);

                        Serial.println("*********");
                        glb_cluster_num = std::string(readFromDrive().c_str());
                        Serial.println(String(glb_cluster_num.c_str()));
                        Serial.println("done");
                        BlinkWarning(10);
                        vTaskDelay(10000);
                        ESP.restart();
                  }
            }
};



/** Define callback instances globally to use for multiple Charateristics \ Descriptors */
//static MyServerCallbacks Callbacks;
//static MyCallbacks chrCallbacks;


NimBLEAdvertising* setup_server() {
      Serial.begin(115200);
      Serial.println("Starting NimBLE Server");


      pServer = NimBLEDevice::createServer();
      pServer->setCallbacks(new MyServerCallbacks());

      NimBLEService* pService = pServer->createService(PSERVID);
      NimBLECharacteristic* pCharacteristic = pService->createCharacteristic(
                  PCHARID,
                  NIMBLE_PROPERTY::WRITE 
                                              );
      Serial.println("Starting NimBLE Server");
     
      pCharacteristic->setCallbacks(new MyCallbacks);
      pService->start();
      NimBLEAdvertising* pAdvertising = NimBLEDevice::getAdvertising();
      pAdvertising->addServiceUUID(pService->getUUID());
      pAdvertising->setScanResponse(false);

      return pAdvertising;

}


void execute_reset(void* parameter) {
      while (true) {
            if (xSemaphoreTake( xBinSemaphore, portMAX_DELAY ) == pdPASS) break;
      }
      wdt.stop();
      Serial.println("Reset imminent");
      vTaskSuspend(task_Client);
      vTaskSuspend(task_wifi);

      glbscan->stop();
      Serial.print("Removng");
   
      vTaskDelay(2000);
      Serial.println("Blink");
  
      BlinkWarning(1000);
      
      myDevice = new sensor_info(glb_cluster_num.c_str(), _PASSWORD_);
      std::string title("Reset_") ;
      title += myDevice->cluster_num_s;
      Serial.println(String(title.c_str()));

      NimBLEDevice::changeName(title);
      pServer = NimBLEDevice::getServer();
      pServer->getAdvertising()->start();
      Serial.println("Waiting a client connection to notify...");

      while (true) {
            
            for (int i = 0; i < 10; i++) {
                  vTaskDelay(1000);
                  Blink();
                  Serial.println("Dev connected?");
                  Serial.println(deviceConnected);
                  if (deviceConnected) {
                        while(true);
                  }
            }
            ESP.restart();
      }
}

#endif

