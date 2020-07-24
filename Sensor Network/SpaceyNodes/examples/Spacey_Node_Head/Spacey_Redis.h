#ifndef __REDIS__
#define __REDIS__
#include "Arduino.h"
#include <Redis.h>
#include <cstring>
#include <cstdlib>
#include <string>
#include "SpaceyAPI.h"
#include "global.h"
#include <esp_task_wdt.h>
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

/*
#define WIFI_SSID             "kw"
#define WIFI_PASSWORD   "kaiwen1998"
*/


/*
#define WIFI_SSID             "hongan"
#define WIFI_PASSWORD   "9831561fff"
*/


      #define REDIS_ADDR      "redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com"
      #define REDIS_PORT      13969
      #define REDIS_PASSWORD  "PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL"


/*
#define REDIS_ADDR      "192.168.1.141"
#define REDIS_PORT      6379
#define REDIS_PASSWORD  "kaiwen"

*/
/*
#define REDIS_ADDR      "192.168.1.89"
#define REDIS_PORT      6379
#define REDIS_PASSWORD  "kaiwen"
*/
#include "Spacey_watchdog_timer.h"
static int timeout = 0;

WiFiClient network_setup() {
      WiFi.mode(WIFI_STA);
      WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
      Serial.print("Connecting to the WiFi");
      while (WiFi.status() != WL_CONNECTED)
      {
            timeout ++;
            if (timeout > TIMEOUT) ESP.restart();
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

class RedisUpdater {
      public:
            String user;
            String restaurant;
            WiFiClient conn;
            Redis* redis;
            RedisUpdater(String _user, String _restaurant, WiFiClient _conn) {
                  user = _user;
                  restaurant = _restaurant;
                  conn = _conn;
                  redis = new Redis(conn);
                  auto connRet = redis->authenticate(REDIS_PASSWORD);
                  if (connRet == RedisSuccess)
                  {
                        Serial.println("Connected to the Redis server!");
                  }
                  else
                  {
                        Serial.printf("Failed to authenticate to the Redis server! Errno: %d\n", (int)connRet);
                        return;
                  }
            }

            void store_value(uint8_t* msg) {
                  std::string temp = intToChar(msg, 3);
                  Serial.println("temp is: ");
                  Serial.println(String(temp.c_str()));
                  const char* occ = msg[3] == 1? "1":"0";
                  Serial.println(String(occ));
                  String idx = get_index_DB(msg);               
                  Serial.println("IDX is ");
                  Serial.print(idx);
                  set_occupance_DB(occ, idx.c_str());
                  
            }

            String get_index_DB(uint8_t* message) {
                  
                  String value;
                  String key = user + "_" + restaurant + "_" + "hash";
                  Serial.println(key);
                  const char* devinfo = intToChar(message_buffer, 2).c_str();
                  Serial.println(String(devinfo));
                  //String devinfo = String(intToChar(message, 2).c_str());
                  value = redis->hget(key.c_str(), devinfo);
                  Serial.println(value);
                  return value;
            }

            void set_occupance_DB(const char* occ, const char* index) {
                  char buf[2];
                  Serial.println(index);
                  Serial.println(occ);
                  bool err;
                  String key = user + "_" + restaurant + "_" + "occupancy";
                  Serial.print(2);
                  err = redis->hset(key.c_str(), index, occ);
                  if (!err) Serial.println("Error reading from DB");
                  return;
            }

            void close_conn() {
                  conn.stop();
                  Serial.println("Bye!");
            }

};



// Run this to liaise with database
void execute_update_wifi(void* paramters)
{
      while (true) {
            xSemaphoreTake(xMutex, portMAX_DELAY);
            
            timeout = 0;
            RedisUpdater myUpdater("NUS", "Deck", network_setup());
            Serial.println(uxQueueSpacesAvailable(message_queue));
            while (uxQueueSpacesAvailable(message_queue) != queue_size ) {

                  xQueueReceive(message_queue, message_buffer, portMAX_DELAY);

                  myUpdater.store_value(message_buffer); //Insert as a task
                  Blink();
            }
            myUpdater.close_conn();
            WiFi.disconnect();
            
            xSemaphoreGive(xMutex);
            vTaskDelay(100);
      }
}




#endif
