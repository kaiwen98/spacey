#include <SpaceyAPI_ESP32.h>

#include "Spacey_BLE_Client.h"
#include "Spacey_watchdog_timer.h"
#include "Spacey_Redis.h"
#include "Spacey_watchdog_timer.h"
#include "FreeRTOS.h"
#include "Spacey_BLE_Server.h"
#include "tasks.h"

#if CONFIG_FREERTOS_UNICORE
#define ARDUINO_RUNNING_CORE 0
#else
#define ARDUINO_RUNNING_CORE 1
#endif

String ID = "1,2,";


WDT watchdog(80);

void setup() {
  Serial.begin(115200);
  Serial.println("Starting Arduino BLE Client application...");
  //watchdog.init_wdt(1000);
  
  task_queue = xQueueCreate(queue_size, sizeof(int) );
          
               xTaskCreatePinnedToCore(
                                       task_BLE_Server,
                                       "Get from Server",
                                       4096,
                                       (void*)&ID,
                                       1,
                                       NULL,
                                       1
                                    );
                                    
                                    /*

                                     xTaskCreatePinnedToCore(
                                       _Touch_get_from_serve,
                                       "Get from Server",
                                       4096,
                                       (void*)&ID,
                                       1,
                                       NULL,
                                       1
                                    );              
                
               xTaskCreatePinnedToCore(_task_update_test,
                                       "Redis",
                                       4096,
                                       NULL,
                                       2,
                                       NULL,
                                       0);
                 
*/

} // End of setup.

void loop() {
  //BLE_get_from_server();
  //watchdog.reset();
}





