

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



