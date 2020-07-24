#ifndef _SPACEYAPI_
#define _SPACEYAPI_

#include <vector>
#include <string>
#include <string.h>
#include "NimBLEScan.h"
#include "NimBLEDevice.h"


uint8_t charToInt(std::string);
// Full packet:
// 23,42,12,1/15

class sensor_info{
  public:
    uint8_t cluster_num[3];
    std::string cluster_num_s;
    uint8_t message_buffer[4];
    //sensor_info(std::string cluster, std::string level, std::string id);
    sensor_info(const char* cluster_full, const char* password);

    const char* password = "123456";
    bool verifypw(std::string input);
};

std::string intToChar(uint8_t* msg, int _len);
std::string processInput(std::string input);
void tokenize(char *buffer[3], const char* input, const char* tok);
bool verifySpaceyID(std::string advname, char* clusterNum_buffer[]);
void fill_message(uint8_t* message_buffer, std::string cluster_num, uint8_t occupancy);




#endif