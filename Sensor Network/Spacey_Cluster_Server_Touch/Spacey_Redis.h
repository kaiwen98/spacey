#ifndef __REDIS__
#define __REDIS__
#include "Arduino.h"
#include <Redis.h>
#include <string.h>
#include <cstdlib>

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
#define REDIS_ADDR      "redis-13969.c11.us-east-1-3.ec2.cloud.redislabs.com"
#define REDIS_PORT      13969
#define REDIS_PASSWORD  "PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL"
*/

#define REDIS_ADDR      "192.168.1.141"
#define REDIS_PORT      6379
#define REDIS_PASSWORD  "kaiwen"

#include "Spacey_watchdog_timer.h"

class update_task {
    String dev_info = "";
    char* occupancy = "0";
  public:
    update_task(String x, char* y) {
      dev_info = x;
      occupancy = y;
    }
};

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

    void store_value(String devinfo, int state){
      char idx[] = "";
      String temp = get_index_DB(devinfo);
      strcpy(idx, temp.c_str());
      set_occupance_DB(idx, state);
     
    }

    String get_index_DB(String devinfo) {
      String value;
      String key = user + "_" + restaurant + "_" + "hash";
      Serial.println(key);
      value = redis->hget(key.c_str(), devinfo.c_str());
      return value;
    }

    void set_occupance_DB(char* index, int occupancy) {
      char buf[2];
      Serial.println(index);
      Serial.println(occupancy);
      bool err;
      String key = user + "_" + restaurant + "_" + "occupancy";
      const char* state = itoa(occupancy, buf, 10);
      err = redis->hset(key.c_str(), index, state);
      if (!err) Serial.println("Error reading from DB");
      return;
    }

    void close_conn(){
      conn.stop();
      Serial.println("Bye!");
    }

};



// Run this to liaise with database
void task_update_BLE(long occupancy)
{
  WDT wdt(80);
  wdt.init_wdt(120);
  RedisUpdater myUpdater("NUS", "Macdonalds", network_setup());
  wdt.reset();
  occupancy = random(2);
  myUpdater.store_value("20,2,2", occupancy); //Insert as a task
  myUpdater.close_conn();
  WiFi.disconnect();
}




#endif
