#include <SpaceyAPI_ESP32.h>

#include "Spacey_BLE_Client.h"
#include "Spacey_watchdog_timer.h"
#include "Spacey_watchdog_timer.h"
#include "FreeRTOS.h"
#include "tasks.h"
#include "queue.h"

#if CONFIG_FREERTOS_UNICORE
#define ARDUINO_RUNNING_CORE 0
#else
#define ARDUINO_RUNNING_CORE 1
#endif


WDT watchdog(80);

void setup() {
  Serial.begin(115200);
  Serial.println("Starting Arduino BLE Client application...");
  //watchdog.init_wdt(1000);
  task_queue = xQueueCreate(queue_size, sizeof(int) );

               xTaskCreatePinnedToCore(task_BLE_Client,
                                       "Get from Server",
                                       4096,
                                       NULL,
                                       1,
                                       NULL,
                                       1);
                                       


} // End of setup.

void loop() {
  //BLE_get_from_server();
  //watchdog.reset();
}





