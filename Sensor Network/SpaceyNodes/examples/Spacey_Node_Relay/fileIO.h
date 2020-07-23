#ifndef __SPFILE__
#define __SPFILE__

#include "FS.h"
#include "SPIFFS.h"

/*    You only need to format SPIFFS the first time you run a
      test or else use the SPIFFS plugin to create a partition
      https://github.com/me-no-dev/arduino-esp32fs-plugin */
#define FORMAT_SPIFFS_IF_FAILED true

void writeFile(fs::FS &fs, const char * path, const char * message) {
      Serial.printf("Writing file: %s\r\n", path);

      File file = fs.open(path, FILE_WRITE);
      if (!file) {
            Serial.println("- failed to open file for writing");
            return;
      }
      if (file.print(message)) {
            Serial.println("- file written");
      } else {
            Serial.println("- frite failed");
      }
}

String readFileOut(fs::FS &fs, const char * path) {
      static uint8_t buf[512];
      int i = 0;
      int len = 0;
      File  file = fs.open(path);
      if (file && !file.isDirectory()) {
            len = file.size();
            size_t flen = len;
            while (len) {
                  size_t toRead = len;
                  if (toRead > 512) {
                        toRead = 512;
                  }
                  file.read(buf, toRead);
                  if ((i++ & 0x001F) == 0x001F) {
                  }
                  len -= toRead;
            }
            file.close();
            return String((char *)buf);
      } else {
            
            writeFile(SPIFFS, "/dev_info.txt", "0,0,0");
      }
}



void appendFile(fs::FS &fs, const char * path, const char * message) {
      Serial.printf("Appending to file: %s\r\n", path);

      File file = fs.open(path, FILE_APPEND);
      if (!file) {
            Serial.println("- failed to open file for appending");
            return;
      }
      if (file.print(message)) {
            Serial.println("- message appended");
      } else {
            Serial.println("- append failed");
      }
}

void writeToDrive(std::string val) {
      writeFile(SPIFFS, "/dev_info.txt", val.c_str());
}

void listDir(fs::FS &fs, const char * dirname, uint8_t levels){
    Serial.printf("Listing directory: %s\r\n", dirname);

    File root = fs.open(dirname);
    if(!root){
        Serial.println("- failed to open directory");
        return;
    }
    if(!root.isDirectory()){
        Serial.println(" - not a directory");
        return;
    }

    File file = root.openNextFile();
    while(file){
        if(file.isDirectory()){
            Serial.print("  DIR : ");
            Serial.println(file.name());
            if(levels){
                listDir(fs, file.name(), levels -1);
            }
        } else {
            Serial.print("  FILE: ");
            Serial.print(file.name());
            Serial.print("\tSIZE: ");
            Serial.println(file.size());
        }
        file = root.openNextFile();
    }
}

String readFromDrive() {
      
      Serial.println(readFileOut(SPIFFS, "/dev_info.txt"));
      return readFileOut(SPIFFS, "/dev_info.txt");
    
}

#endif
