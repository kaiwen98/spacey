
#include "Spacey_NimBLE_Client.h"
#include "Spacey_NimBLE_Server.h"

#include "SPIFFS.h"
#include "BLE_listen.h"
#include <NimBLEDevice.h>
#include "esp_bt.h"

#include "global.h"
#include "fileIO.h"

void setup () {
      Serial.begin(115200);
      disableCore0WDT();
      disableCore1WDT();
  
      
      pinMode (2, OUTPUT);
      
      if (!SPIFFS.begin(FORMAT_SPIFFS_IF_FAILED)) {
            Serial.println("SPIFFS Mount Failed");
            return;
      }
      glb_cluster_num= std::string(readFromDrive().c_str());


      pinMode(0, INPUT_PULLUP);
      attachInterrupt(digitalPinToInterrupt(0), release, CHANGE);
     esp_bt_sleep_enable();
      
      NimBLEDevice::init(glb_cluster_num);
      NimBLEDevice::setSecurityAuth(BLE_SM_PAIR_AUTHREQ_SC);

      

     
      NimBLEDevice::setPower(ESP_PWR_LVL_P9); 
      
      glbscan = setup_client();
      glbadv = setup_server();

      xMutex = xSemaphoreCreateMutex();
      xBinSemaphore = xSemaphoreCreateBinary();
      
      message_queue = xQueueCreate(queue_size, sizeof(message_buffer));
       xTaskCreatePinnedToCore(execute_client, "client", 4096, (void*) glbscan, 4, &task_Client, 0);
      delay(500);
      xTaskCreatePinnedToCore(execute_server, "server", 4096, (void*) glbadv, 1, &task_Server, 0);
      xTaskCreatePinnedToCore(execute_reset, "Get Reset", 4096, NULL, 0, &task_Reset, 0);

      //vTaskStartScheduler(); 
      
}


void loop () {
      vTaskSuspend(NULL);
}

