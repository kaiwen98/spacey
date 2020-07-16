#include "TouchSensor.h"

void _BLE_get_from_server(void* parameter) {
  while (true) {
    for ( int i = 0; ; i++ ) {
      if (!(i % 5)) {
        Serial.println(i);
        xQueueSend(task_queue, &i, (TickType_t )10000);
        
        vTaskDelay(5000);
      }
    }
    vTaskDelete( NULL );
  }
}

void _Touch_get_from_server(void* parameter) {
  TouchSensor myTouch(4, 40, 5);
  int i;
  while (true) {
      i = myTouch.getReading();
      Serial.print("Touch: ");
      Serial.println(i);
      xQueueSend(task_queue, &i, (TickType_t )10000);
      vTaskDelay(5000); 
  }
}


void _Touch_get_from_serve(void* parameter) {
  TouchSensor myTouch(4, 69, 1);
  int i = 1;
  
  xQueueSend(task_queue, &i, (TickType_t )10000);
  while (true) {
      switch(myTouch.getTouchState()){
        case SEAT_OCCUPIED:
          i = myTouch.getReading() + 1000;
          xQueueSend(task_queue, &i, (TickType_t )10000);
          break;
        case SEAT_FREE:
          i = myTouch.getReading() + 2000;
          xQueueSend(task_queue, &i, (TickType_t )10000);
          break;
         default:
          break;
      }
      Serial.print("Touch: ");
      Serial.println(i);
     //
     //xQueueSend(task_queue, &i, (TickType_t )10000);
      vTaskDelay(500); 
  }
}

void _task_update_BLE(void* parameter) {
  int element;
  while (true) {
    for ( ;; ) {
 
      vTaskDelay(1000);
      xQueueReceive(task_queue, &element, portMAX_DELAY);
      // Serial.print(element);
      //Serial.print("|");
    }
  }
  vTaskDelete( NULL );
}


void _task_update_test(void* parameter)
{
  int element;
  WDT watch(80);
  watch.init_wdt(20000);
  while (1) {
    char buf[4];
    xQueueReceive(task_queue, &element, portMAX_DELAY);

    RedisUpdater myUpdater("NUS", "Macdonalds", network_setup());
    watch.reset();
    const char* state = itoa(element, buf, 10);
    Serial.println((myUpdater.redis) -> set("test", state));
    myUpdater.close_conn();
    WiFi.disconnect();
  }
}
