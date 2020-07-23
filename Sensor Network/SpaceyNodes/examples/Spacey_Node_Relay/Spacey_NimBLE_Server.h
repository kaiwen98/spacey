#ifndef __SERVER__
#define __SERVER__
#include <NimBLEDevice.h>

static NimBLEServer* pServer;
NimBLECharacteristic* _pChr  = nullptr;
bool disconnected = false;
static bool s_indicate_success = false;
static bool hand_over_to_client = false;

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
                        s_indicate_success = true;
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
      Serial.begin(115200);
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
            disconnected = true;
            xSemaphoreTake(xMutex, portMAX_DELAY);
            vTaskDelay(20);
            Serial.println("Queue Content");
            Serial.println(uxQueueSpacesAvailable(message_queue));
            Serial.println("Starting NimBLE Serverds");
            NimBLEAdvertising* pAdvertising = (NimBLEAdvertising*) parameter;
            int count = 0;

            pAdvertising->start();
            uint8_t val = 0;
            Serial.println("Advertising Started");
            Serial.println(uxQueueSpacesAvailable(message_queue));
            int timeout = 0;

            hand_over_to_client = false;
            while ( !hand_over_to_client && timeout < 30) {
                  /*
                        xQueueReceive(message_queue, message_buffer, portMAX_DELAY);
                        for (int i = 0; i < 4; i++) {
                        Serial.print(message_buffer[i]);
                        Serial.print(" | ");
                        }
                        vTaskDelay(1000);
                  */

                  if (pServer->getConnectedCount()) {

                        disconnected = false;
                        NimBLEService* pSvc = pServer->getServiceByUUID(SERVID);
                        if (pSvc) {
                              _pChr = pSvc->getCharacteristic(CHARID);
                              if (_pChr) {
                                    if (uxQueueSpacesAvailable(message_queue) == queue_size) {
                                          xQueueSendToBack(message_queue, message_null, portMAX_DELAY);
                                          hand_over_to_client = true;
                                          _pChr->setValue(message_null, 4);
                                    }
                                    else {
                                          xQueueReceive(message_queue, message_buffer, portMAX_DELAY);
                                          for (int i = 0; i < 4; i++) {
                                                Serial.print(message_buffer[i]);
                                                Serial.print(" | ");
                                                Serial.println("");
                                                _pChr->setValue(message_buffer, 4);
                                          }
                                    }

                              

                                    while (true) {
                                          vTaskDelay(50);
                                          _pChr->indicate();
                                          if (s_indicate_success) break;
                                          Serial.println("out");
                                    }

                                    s_indicate_success = false;
                                    vTaskDelay(50);

                              }
                        }
                        timeout = 0;
                  }
                  else {
                        Serial.println("timeout: ");
                        Serial.print(timeout);
                        timeout++;
                        vTaskDelay(500);
                  }
            }

       

            // Send stop message to client to notify sequence is complete
            if (timeout < 30 ) {
                  _pChr->setValue(message_null, 4);
                  _pChr->indicate();

            }
            while (true) {
                  Serial.println("pyo");
                  if (disconnected == true) break;
                  vTaskDelay(10);;
            }
            disconnected = false;
            pAdvertising->stop();
            pServer->resetGATT();
            Serial.println(">>>>>> End Server");
            xSemaphoreGive(xMutex);
            xQueueReset(message_queue);
            vTaskDelay(20);

      }
}



#endif
