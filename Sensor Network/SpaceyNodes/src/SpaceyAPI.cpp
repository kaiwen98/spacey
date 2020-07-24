#include <map>
#include <bits/stdc++.h>
#include <vector>
#include <string>
#include <string.h>
#include "SpaceyAPI.h"
#include <stdio.h>
#include <cstring>
#include <stdlib.h>
#include <math.h>
#include <cctype>

/*
sensor_info::sensor_info(std::string cluster, std::string level, std::string id){
      sensor_info::cluster_num[0] = charToInt(cluster);
      sensor_info::cluster_num[1] = charToInt(level);
      sensor_info::cluster_num[2] = charToInt(id);
      sensor_info::cluster_num_s = cluster+","+level+","+id;
}*/

sensor_info::sensor_info(const char* cluster_full, const char* _password){
      char *buffer[3];
      tokenize(buffer, cluster_full, ",");
      sensor_info::cluster_num[0] = charToInt(std::string(buffer[0]));
      sensor_info::cluster_num[1] = charToInt(std::string(buffer[1]));
      sensor_info::cluster_num[2] = charToInt(std::string(buffer[2]));
      sensor_info::cluster_num_s = cluster_full;
      sensor_info::password = _password;
}

bool sensor_info::verifypw(std::string input){
  if (input.length() < 6) return false;
  char buf[7] = "";
  const char *inp = input.c_str();
  const char* pw = sensor_info::password;
  int comma_c = 0;
  for(int i = 0; i < 6; i ++)
    buf[i] = inp[i];
  buf[6] = '\0';

  if(strcmp(buf, pw)) return false;

  std::string substr = processInput(input);
  const char* sub = substr.c_str();
  
  if(strlen(sub) > 9) return false;
  for (int i = 0; i < strlen(sub); i++){
    if (i == strlen(sub)-1  && !std::isdigit(sub[i])) return false;
    if(sub[i] == ',') comma_c++;
    if(sub[i] == ',' && !std::isdigit(sub[i+1]) ) return false;
  }
  return true;
}

// Populate a uint8_t buffer, the cluster number in the string input
void fill_message(uint8_t* message_buffer, std::string cluster_num, uint8_t occupancy){
  char *buffer[3];
  const char* delim = ",";
  tokenize(buffer, cluster_num.c_str(), delim);
  
    for(int i = 0; i <3; i++){
        message_buffer[i] = *(uint8_t*)(buffer[i]) - 48;
    }
    std::cout<<std::endl;

  message_buffer[3] = occupancy;
}


//Used to convert data to bytes to facilitate indications
uint8_t charToInt(std::string num){
  uint8_t result = 0;
  uint8_t add = 0;
  char *buffer = new char[num.length() + 1];
  std::strcpy(buffer, num.c_str());
  for(int i = 0; i < strlen(buffer); i++){
    add = pow(10,(strlen(buffer) - i-1))*(buffer[i]-48);
    result += add;
  }
  return result;
}

std::string intToChar(uint8_t* msg, int _len)
{
    char msgc[10];
    int len = _len*2+1;
    char *buf = new char(10);
    int j = 0;
   
    for (int i = 0; i < len; i++){
        if(!(i%2)){
            
            msgc[i] = (char)msg[j] + 48; 
        
            j++;
        }
        else msgc[i] = ',';
    }
    msgc[len] = 0;

    return std::string(msgc);
}


void tokenize(char *buffer[3], const char* input, const char* tok)
{   
   char *token;
   char *str = new char[strlen(input) + 1];
   int i = 0;

   std::strcpy(str, input);
   token = strtok(str, tok);
   
   while( token != NULL ) {
      buffer[i] = token;
      token = strtok(NULL, tok);
      i++;
   }
}

std::string processInput(std::string input){
  int len = input.length() - 7;
  return input.substr(7, len);
}


bool verifySpaceyID(std::string advname, char* clusterNum_buffer[]){
	char* buffer[3];
	char delim[2] = ",";
	tokenize(buffer, advname.c_str(), delim);
	//Only connect to children nodes in the same cluster, they should have higher cluster level (Greater distance from cluster head nodes)
	return !strcmp(buffer[0], clusterNum_buffer[0]) && charToInt(buffer[1]) == (charToInt(clusterNum_buffer[1])+1);
}