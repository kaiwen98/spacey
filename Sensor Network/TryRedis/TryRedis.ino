#include <Redis.h>
#include <string.h>
#include "RedisHead.h"
#include <stdlib.h>

// this sketch will build for the ESP8266 or ESP32 platform
#ifdef HAL_ESP32_HAL_H_ // ESP32
#include <WiFiClient.h>
#include <WiFi.h>
#else
#ifdef CORE_ESP8266_FEATURES_H // ESP8266
#include <ESP8266WiFi.h>
#endif
#endif

#define WIFI_SSID       "Linksys05333"
#define WIFI_PASSWORD   "gtdfrahkeg"

#define REDIS_ADDR      "redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com"
#define REDIS_PORT      13969
#define REDIS_PASSWORD  "PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL"



const int wdtTimeout = 10000;  //time in ms to trigger the watchdog
hw_timer_t *timer = NULL;



WiFiClient network_setup() {
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to the WiFi");
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(250);
    Serial.print(".");
  }
  Serial.println();
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  WiFiClient redisConn;
  if (!redisConn.connect(REDIS_ADDR, REDIS_PORT)) {
    Serial.println("Failed to connect to the Redis server!");
  }
  return redisConn;
}


void IRAM_ATTR resetModule() {
  Serial.println("reboot");
  ets_printf("reboot\n");
  esp_restart();
}


void task_update_BLE()
{
  long a;
  timer = timerBegin(0, 80, true);                  //timer 0, div 80
  timerAttachInterrupt(timer, &resetModule, true);  //attach callback
  timerAlarmWrite(timer, wdtTimeout * 1000, false); //set time in us
  timerAlarmEnable(timer);                          //enable interrupt
  
  RedisUpdater myUpdater("NUS", "Macdonalds", network_setup());
  timerWrite(timer, 0); //reset timer (feed watchdog)
  a = random(2);
  myUpdater.store_value("20,2,2", a); //Insert as a task
  myUpdater.close_conn();
  WiFi.disconnect();
}






void setup(){
  Serial.begin(115200);
}

void loop()
{
  task_update_BLE();
}
