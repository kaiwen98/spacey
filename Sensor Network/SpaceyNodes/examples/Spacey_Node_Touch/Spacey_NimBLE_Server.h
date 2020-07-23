#ifndef __SERVER__
#define __SERVER__
#include <NimBLEDevice.h>
#include "warning_led.h"
#include "global.h"
#include "TouchSensor.h"

static NimBLEServer* pServer;
NimBLECharacteristic* _pChr  = nullptr;
bool disconnected = false;

class ServerCallbacks: public NimBLEServerCallbacks {
            void onConnect(NimBLEServer* pServer) {
                  Serial.println("Client connected");
                  Serial.println("Multi-connect support: start advertising");
                  //NimBLEDevice::startAdvertising();
            };

            void onConnect(NimBLEServer* pServer, ble_gap_conn_desc* desc) {
                  Serial.print("Client address: ");
                  Serial.println(NimBLEAddress(desc->peer_ota_addr).toString().c_str());
                  /**   We can use the connection handle here to ask for different connection parameters.
                        Args: connection handle, min connection interval, max connection interval
                        latency, supervision timeout.
                        Units; Min/Max Intervals: 1.25 millisecond increments.
                        Latency: number of intervals allowed to skip.
                        Timeout: 10 millisecond increments, try for 5x interval time for best results.
                  */
                  //pServer->updateConnParams(desc->conn_handle, 24, 48, 0, 60);
            };
            void onDisconnect(NimBLEServer* pServer) {
                  Serial.println("Client disconnected - start advertising");
                  //NimBLEDevice::startAdvertising();
                  disconnected = true;
            };
};

/** Handler class for characteristic actions */
class CharacteristicCallbacks: public NimBLECharacteristicCallbacks {

            /**   Called before notification or indication is sent,
                  the value can be changed here before sending if desired.
            */
            void onNotify(NimBLECharacteristic* pCharacteristic) {
                  Serial.println("Sending notification to clients");
            };

            /**   The status returned in status is defined in NimBLECharacteristic.h.
                  The value returned in code is the NimBLE host return code.
            */
            void onStatus(NimBLECharacteristic* pCharacteristic, Status status, int code) {
                  String str = ("Notification/Indication status code: ");
                  str += status;
                  str += ", return code: ";
                  str += code;
                  str += ", ";
                  str += NimBLEUtils::returnCodeToString(code);
                  Serial.println(str);

                  if ((int)status == 1) {
                        Chirp();
                        indicate_success = true;
                  }
            };
};

/** Handler class for descriptor actions */
class DescriptorCallbacks : public NimBLEDescriptorCallbacks {
            void onWrite(NimBLEDescriptor* pDescriptor) {
                  if (pDescriptor->getUUID().equals(NimBLEUUID("2902"))) {
                        /** Cast to NimBLE2902 to use the class specific functions. **/
                        NimBLE2902* p2902 = (NimBLE2902*)pDescriptor;
                        if (p2902->getNotifications()) {
                              Serial.println("Client Subscribed to notfications");
                        } else if (p2902->getIndications()) {
                              Serial.println("Client Subscribed to indications");
                        } else {
                              Serial.println("Client Unubscribed");
                        }
                  } else {
                        std::string dscVal((char*)pDescriptor->getValue(), pDescriptor->getLength());
                        Serial.print("Descriptor witten value:");
                        Serial.println(dscVal.c_str());
                  }
            };

            void onRead(NimBLEDescriptor* pDescriptor) {
                  Serial.print(pDescriptor->getUUID().toString().c_str());
                  Serial.println(" Descriptor read");
            };
};


/** Define callback instances globally to use for multiple Charateristics \ Descriptors */
static DescriptorCallbacks dscCallbacks;
static CharacteristicCallbacks chrCallbacks;


NimBLEAdvertising* setup_server() {
   
      Serial.println("Starting NimBLE Server");
      


      pServer = NimBLEDevice::createServer();
      pServer->setCallbacks(new ServerCallbacks());

      NimBLEService* pService = pServer->createService(SERVID);
      NimBLECharacteristic* pCharacteristic = pService->createCharacteristic(
                  CHARID,
                  NIMBLE_PROPERTY::WRITE |
                  NIMBLE_PROPERTY::INDICATE
                                              );
      Serial.println("Starting NimBLE Server");
      NimBLE2902* p2902 = (NimBLE2902*)pCharacteristic->createDescriptor("2902");
      p2902->setCallbacks(&dscCallbacks);
      pCharacteristic->setCallbacks(&chrCallbacks);
      /** Start the services when finished creating all Characteristics and Descriptors */
      pService->start();

      NimBLEAdvertising* pAdvertising = NimBLEDevice::getAdvertising();
      /** Add the services to the advertisment data **/
      pAdvertising->addServiceUUID(pService->getUUID());
      /**   If your device is battery powered you may consider setting scan response
            to false as it will extend battery life at the expense of less data sent.
      */

      pAdvertising->setScanResponse(false);

      return pAdvertising;

}

void execute_server(void* parameter) {

      while (true) {

            xQueueReceive(message_queue, message_buffer, portMAX_DELAY);
            NimBLEAdvertising* pAdvertising = glbadv;
            vTaskDelay(100);
           
            vTaskSuspend(task_Touch);
            
            disconnected = true;
            vTaskDelay(200);
            Serial.println("Queue Content");
            Serial.println(uxQueueSpacesAvailable(message_queue));
            Serial.println("Starting NimBLE Serverds");
            
            int count = 0;

            pAdvertising->start();
            uint8_t val = 0;
            Serial.println("Advertising Started");
            Serial.println(uxQueueSpacesAvailable(message_queue));
            int timeout = 0;
            indicate_success = false;
            while ( timeout < 30 && !indicate_success) {
                
                  if (pServer->getConnectedCount()) {
                        timeout = 0;
                        NimBLEService* pSvc = pServer->getServiceByUUID(SERVID);
                        if (pSvc) {
                              _pChr = pSvc->getCharacteristic(CHARID);
                              if (_pChr) {
                                    for (int i = 0; i < 4; i++) {
                                          Serial.print(message_buffer[i]);
                                          Serial.print(" | ");
                                    }

                                    Serial.println("");
                                    _pChr->setValue(message_buffer, 4);

                                    while (true) {
                                          /*
                                          vTaskDelay(500);
                                          _pChr->setValue(_threshold);
                                          _pChr->indicate();
                                          */
                                          vTaskDelay(50);
                                          
                                          
                                          _pChr->indicate();
                                          touchRead(4);
                                      if (indicate_success) break;
                                    }
                                    
                                    vTaskDelay(50);
                              }
                        }
                  }
                  else {
                        Serial.println("timeout: ");
                        Serial.print(timeout);
                        timeout++;
                        delay(500);
                  }
            }
           // indicate_success = false;
            // Send stop message to client to notify sequence is complete
            if (timeout < 30 ) {
                  _pChr->setValue(message_null, 4);
                  touchRead(4);
                  _pChr->indicate();

            }
            while (true) {
                  if (disconnected == true) break;
                  vTaskDelay(100);
            }
            disconnected = false;
            pAdvertising->stop();
            pServer->resetGATT();
            Serial.println(">>>>>> End Server");
            xQueueReset(message_queue);
            Serial.println("Sleep");
            if (message_buffer[3] == 0 && indicate_success) {
                 //_threshold = configure_threshold(3);
                 esp_deep_sleep_start();
                  vTaskResume(task_Touch);
            }
            else {
                  vTaskResume(task_Touch);
            }
           
           // vTaskDelete(NULL);

      }
}



#endif
