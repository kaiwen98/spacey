

#ifndef __CLIENT__
#define __CLIENT__
#include <NimBLEDevice.h>
#include "global.h"
#include <esp_nimble_hci.h>
#include "warning_led.h"

void scanEndedCB(NimBLEScanResults results);

static NimBLEAdvertisedDevice* advDevice;

static bool doConnect = false;
static bool c_disconnected = false;
static uint32_t scanTime = 1000; /** 0 = scan forever */
NimBLEScanResults *myResults = nullptr;
NimBLERemoteCharacteristic* pChr = nullptr;
NimBLERemoteDescriptor* pDsc = nullptr;
NimBLEClient* pClient = nullptr;


/**   None of these are required as they will be handled by the library with defaults. **
 **                       Remove as you see fit for your needs                        */
class ClientCallbacks : public NimBLEClientCallbacks {
            void onConnect(NimBLEClient* pClient) {
                  Serial.println("Connected");
                  c_disconnected = false;
            };

            void onDisconnect(NimBLEClient* pClient) {
                  Serial.print(pClient->getPeerAddress().toString().c_str());
                  Serial.println(" Disconnected - Starting scan");
                  c_disconnected = true;
                  //NimBLEDevice::getScan()->start(scanTime, scanEndedCB);
            };
};


/** Define a class to handle the callbacks when advertisments are received */
class AdvertisedDeviceCallbacks: public NimBLEAdvertisedDeviceCallbacks {

            void onResult(NimBLEAdvertisedDevice* advertisedDevice) {
                  Serial.print("Advertised Device found: ");
                  Serial.println(advertisedDevice->toString().c_str());
                  if (advertisedDevice->isAdvertisingService(NimBLEUUID(SERVID)))
                  {
                        Serial.println("Found Our Service");
                        /** stop scan before connecting */
                        //NimBLEDevice::getScan()->stop();
                        /** Save the device reference in a global for the client to use*/
                        //advDevice = advertisedDevice;
                        /** Ready to connect now */
                        doConnect = true;
                  }
            };
};


/** Notification / Indication receiving handler callback */
void notifyCB(NimBLERemoteCharacteristic* pRemoteCharacteristic, uint8_t* pData, size_t length, bool isNotify) {
      if (indicate_success) return;
      uint8_t *message;
      std::string str = (isNotify == true) ? "Notification" : "Indication";
      str += " from ";
      /** NimBLEAddress and NimBLEUUID have std::string operators */
      str += std::string(pRemoteCharacteristic->getRemoteService()->getClient()->getPeerAddress());
      str += ": Service = " + std::string(pRemoteCharacteristic->getRemoteService()->getUUID());
      str += ", Characteristic = " + std::string(pRemoteCharacteristic->getUUID());
      str += ", Value = " ;
      Chirp();
      memcpy(message_buffer, pData, 4);
      Serial.println(str.c_str());

      for (int i = 0; i < 4; i++) {
            Serial.print(message_buffer[i]);
            Serial.print(" ");
      }


      Serial.println(" ");

      if (!memcmp(message_buffer, message_null, 4)) {
            indicate_success = true;
            return;
      }
      xQueueSendToBack(message_queue, message_buffer, portMAX_DELAY);
      for (int i = 0; i < 4; i++) {
            message_buffer[i] = 0;
      }



}



/** Callback to process the results of the last scan or restart it */
void scanEndedCB(NimBLEScanResults results) {
      Serial.println("Scan Ended");
}


/** Create a single global instance of the callback class to be used by all clients */
static ClientCallbacks clientCB;


/** Handles the provisioning of clients and connects / interfaces with the server */



bool connectToServer() {
      pClient = nullptr;

      /** Check if we have a client we should reuse first **/
      if (NimBLEDevice::getClientListSize()) {
            /**   Special case when we already know this device, we send false as the
                  second argument in connect() to prevent refreshing the service database.
                  This saves considerable time and power.
            */
            pClient = NimBLEDevice::getClientByPeerAddress(advDevice->getAddress());
            if (pClient) {
                  if (!pClient->connect(advDevice, false)) {
                        Serial.println("Reconnect failed");
                        return false;
                  }
                  Serial.println("Reconnected client");
            }
            /**   We don't already have a client that knows this device,
                  we will check for a client that is disconnected that we can use.
            */
            else {
                  pClient = NimBLEDevice::getDisconnectedClient();
            }
      }

      /** No client to reuse? Create a new one. */
      if (!pClient) {
            if (NimBLEDevice::getClientListSize() >= NIMBLE_MAX_CONNECTIONS) {
                  Serial.println("Max clients reached - no more connections available");
                  return false;
            }

            pClient = NimBLEDevice::createClient();

            Serial.println("New client created");

            pClient->setClientCallbacks(&clientCB, false);
            /**   Set initial connection parameters: These settings are 15ms interval, 0 latency, 120ms timout.
                  These settings are safe for 3 clients to connect reliably, can go faster if you have less
                  connections. Timeout should be a multiple of the interval, minimum is 100ms.
                  Min interval: 12 * 1.25ms = 15, Max interval: 12 * 1.25ms = 15, 0 latency, 51 * 10ms = 510ms timeout
            */
            pClient->setConnectionParams(12, 12, 0, 51);

            /** Set how long we are willing to wait for the connection to complete (seconds), default is 30. */
            pClient->setConnectTimeout(5);


            if (!pClient->connect(advDevice)) {
                  /** Created a client but failed to connect, don't need to keep it as it has no data */
                  NimBLEDevice::deleteClient(pClient);
                  Serial.println("Failed to connect, deleted client");
                  return false;
            }
      }

      if (!pClient->isConnected()) {
            if (!pClient->connect(advDevice, true)) {
                  Serial.println("Failed to connect");
                  return false;
            }
      }

      Serial.print("Connected to: ");
      Serial.println(pClient->getPeerAddress().toString().c_str());
      Serial.print("RSSI: ");
      Serial.println(pClient->getRssi());

      /** Now we can read/write/subscribe the charateristics of the services we are interested in */
      NimBLERemoteService* pSvc = nullptr;


      pSvc = pClient->getService(SERVID);
      if (pSvc) {    /** make sure it's not null */
            pChr = pSvc->getCharacteristic(CHARID);
      }

      if (pChr) {    /** make sure it's not null */
            /**   registerForNotify() has been deprecated and replaced with subscribe() / unsubscribe().
                  Subscribe parameter defaults are: notifications=true, notifyCallback=nullptr, response=false.
                  Unsubscribe parameter defaults are: response=false.
            */
            if (pChr->canIndicate()) {
                  /** Send false as first argument to subscribe to indications instead of notifications */
                  //if(!pChr->registerForNotify(notifyCB, false)) {
                  if (!pChr->subscribe(false, notifyCB)) {
                        /** Disconnect if subscribe failed */
                        return false;
                  }
            }
      }

      else {
            Serial.println("DEAD service not found.");
      }

      Serial.println("Done with this device!");
      return true;
}

NimBLEScan* setup_client() {

      /** create new scan */
      NimBLEScan* pScan = NimBLEDevice::getScan();

      /** create a callback that gets called when advertisers are found */
      pScan->setAdvertisedDeviceCallbacks(new AdvertisedDeviceCallbacks());

      /** Set scan interval (how often) and window (how long) in milliseconds */
      pScan->setInterval(45);
      pScan->setWindow(15);
      pScan->setClusterNum(glb_cluster_num);

      /**   Active scan will gather scan response data from advertisers
            but will use more energy from both devices
      */
      pScan->setActiveScan(true);
      Serial.println("Done with server");
      return pScan;

}

void execute_client(void* parameter) {
      /**   Start scanning for advertisers for the scan time specified (in seconds) 0 = forever
            Optional callback for when scanning stops.
      */
      static bool hand_to_client = false;
      Serial.println("bruh");
      while (true) {
            xSemaphoreTake(xMutex, portMAX_DELAY);
            hand_to_client = false;
            
            while(!hand_to_client){
                  NimBLEScan* pScan;
                  pScan = (NimBLEScan*) parameter;
                  disableCore0WDT();
                  int count = 0;
                  while (count < 3) {
                        
                        pScan->start(scanTime, scanEndedCB);
                        /** Get All nearby devices that qualify for data relay.*/
                        if (pScan->getNumResults() > 0)  break;
                        Serial.println("scanning");
                        vTaskDelay(3000);
                  }
                  enableCore0WDT();
      
      
                  // pScan->stop();
                  myResults = new NimBLEScanResults(pScan->getResults());
                  Serial.println(myResults->getCount());
                  int size = myResults->getCount();
                  Serial.println("size: ");
                  Serial.print(size);
                  for (int i = 0; i < size; i++) {
                        advDevice = new NimBLEAdvertisedDevice(myResults->getDevice(i));
                        Serial.println("Device Name: ");
                        Serial.print(String(advDevice->getName().c_str()));
                        Serial.println("");
                        Serial.println("woops2");
                        if (connectToServer()) {
                              Serial.println("Success! we should now be getting notifications, scanning for more!");
                              c_disconnected = false;
                              while (true) {
                                    if (indicate_success || c_disconnected) break;
                                    Serial.println("in");
                                    vTaskDelay(50);
                              }
                              if (c_disconnected) c_disconnected = false;
                              indicate_success = false;
                              pChr->unsubscribe();
                              Serial.print("Yeet");
                              pClient->disconnect();
                              NimBLEDevice::deleteClient(pClient);
                              delete advDevice;
                        }
                        else {
                              Serial.println("Failed to connect, starting scan");
                        }
                        vTaskDelay(50);
                  }
                  Serial.println("lol");
                  delete myResults;
                  pScan->stop();
      
      
                  if (uxQueueSpacesAvailable(message_queue) < queue_size){
                        Serial.println(">>>>>> End Client");
                        hand_to_client = true;
                        xSemaphoreGive(xMutex);
                  }
                   vTaskDelay(50);
            }
      }
}


#endif

