
#include "Spacey_NimBLE_Server.h"
#include "BLE_listen.h"
#include "TouchSensor.h"
#include <NimBLEDevice.h>

#include "warning_led.h"
#include "global.h"
#include "fileIO.h"
#include "esp_bt.h"



void IRAM_ATTR callback() {
   
}

void setup () {
      Serial.begin(115200);
      //disableCore0WDT();
      //disableCore1WDT();


      pinMode (2, OUTPUT);

      if (!SPIFFS.begin(FORMAT_SPIFFS_IF_FAILED)) {
            Serial.println("SPIFFS Mount Failed");
            return;
      }
      glb_cluster_num = std::string(readFromDrive().c_str());
      esp_bt_sleep_enable();

      NimBLEDevice::init(glb_cluster_num);
      NimBLEDevice::setSecurityAuth(BLE_SM_PAIR_AUTHREQ_SC);


      NimBLEDevice::setPower(ESP_PWR_LVL_P9);
      glbadv = setup_server();

      if (_threshold == 0) {
            Serial.println("resetting");
            
            _threshold = configure_threshold();
      }

      else{
            for (int i = 0; i < 10; i ++) Blink();
      }
      
      touchAttachInterrupt(4, callback, _threshold*1.05);
      myTouch = new TouchSensor(4, _threshold, 8);
      esp_sleep_enable_touchpad_wakeup();

      pinMode(0, INPUT_PULLUP);
      attachInterrupt(digitalPinToInterrupt(0), release, CHANGE);



      xBinSemaphore = xSemaphoreCreateBinary();

      message_queue = xQueueCreate(queue_size, sizeof(message_buffer));
      xTaskCreatePinnedToCore(task_get_touch, "client", 4096, NULL, 4, &task_Touch, 0);
      delay(50);
      xTaskCreatePinnedToCore(execute_server, "server", 4096, (void*) glbadv, 1, &task_Server, 0);
      xTaskCreatePinnedToCore(execute_reset, "Get Reset", 4096, NULL, 0, &task_Reset, 0);

      //vTaskStartScheduler();


}


void loop () {
      vTaskSuspend(NULL);
}

