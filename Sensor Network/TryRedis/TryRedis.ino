#include <Redis.h>
#include <string.h>

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

char input[] = "";
String temp = "";
void setup() 
{
    Serial.begin(115200);
    Serial.println();

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
    if (!redisConn.connect(REDIS_ADDR, REDIS_PORT))
    {
        Serial.println("Failed to connect to the Redis server!");
        return;
    }

    Redis redis(redisConn);
    auto connRet = redis.authenticate(REDIS_PASSWORD);
    if (connRet == RedisSuccess)
    {
        Serial.println("Connected to the Redis server!");
    } 
    else 
    {
        Serial.printf("Failed to authenticate to the Redis server! Errno: %d\n", (int)connRet);
        return;
    }

    Serial.print("SET foo bar: ");
    if (redis.hget("NUS_Macdonalds_hash", "7,2,2")){
        Serial.println("ok!");
 
        temp = redis.hget("NUS_Macdonalds_hash", "7,2,2");
    }
    else{
        Serial.println("err!");
    }

    strcpy(input,temp.c_str());
    if (redis.hset("NUS_Macdonalds_occupancy", input, "1")){
        Serial.println("ok!");
    }

    

    Serial.print("GET foo: ");
    Serial.println(redis.get("foo"));

    redisConn.stop();
    Serial.print("Connection closed!");
}

void loop() 
{
}
