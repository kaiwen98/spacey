
#include "Spacey_NimBLE_Client.h"
#include "Spacey_Redis.h"

#include "SPIFFS.h"
#include "BLE_listen.h"
#include <NimBLEDevice.h>

#include "global.h"
#include "fileIO.h"
#include "esp_task_wdt.h"


void setup () {
      Serial.begin(115200);
      
      pinMode (2, OUTPUT);
      
      if (!SPIFFS.begin(FORMAT_SPIFFS_IF_FAILED)) {
            Serial.println("SPIFFS Mount Failed");
            return;
      }
      glb_cluster_num= std::string(readFromDrive().c_str());


      pinMode(0, INPUT_PULLUP);
      attachInterrupt(digitalPinToInterrupt(0), release, CHANGE);
     
      
      NimBLEDevice::init(glb_cluster_num);
      NimBLEDevice::setSecurityAuth(BLE_SM_PAIR_AUTHREQ_SC);
      NimBLEDevice::setPower(ESP_PWR_LVL_P9); 
      
      glbscan = setup_client();
      glbadv = setup_server();

      xMutex = xSemaphoreCreateMutex();
      xBinSemaphore = xSemaphoreCreateBinary();
      
      message_queue = xQueueCreate(queue_size, sizeof(message_buffer));
       xTaskCreatePinnedToCore(execute_client, "client", 4096, (void*) glbscan, 7, &task_Client, 0);
      delay(500);
      xTaskCreatePinnedToCore(execute_update_wifi, "wifi", 5000, NULL, 6, &task_wifi, 1);
      xTaskCreatePinnedToCore(execute_reset, "Get Reset", 4096, (void*) glbadv, 0, &task_Reset, 0);

      
}


void loop () {
      vTaskSuspend(NULL);
}

