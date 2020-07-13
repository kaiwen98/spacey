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



void setup()
{
  long a;
  char number[1];
  Serial.begin(115200);
  RedisUpdater myUpdater("NUS", "Macdonalds", network_setup());
  a = random(2);
  myUpdater.store_value("20,2,2", a);
  myUpdater.close_conn();
}

void loop()
{
}
