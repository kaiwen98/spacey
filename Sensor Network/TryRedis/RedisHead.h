#ifndef __REDIS__
#define __REDIS__
#include "Arduino.h"
#include <Redis.h>
#include <string.h>
#include <cstdlib>

#define REDIS_PASSWORD  "PbKFE8lJq8HFGve4ON5rRFXhlVrGYUHL"
// this sketch will build for the ESP8266 or ESP32 platform
#include <WiFiClient.h>
#include <WiFi.h>

class task {
    String dev_info = "";
    char* occupancy = "0";
  public:
    task(String x, char* y) {
      dev_info = x;
      occupancy = y;
    }
};

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

#endif
