#ifndef __SGLBL__
#define __SGLBL__
#define _PASSWORD_ "123456"
#define SERVID "AAAA"
#define CHARID "BBBB"
# define TIMEOUT 15
#define PSERVID "CCCC"
#define PCHARID "DDDD"
#include "Spacey_watchdog_timer.h"

std::string glb_cluster_num;

SemaphoreHandle_t xMutex;
SemaphoreHandle_t xBinSemaphore;
NimBLEAdvertising *glbadv = nullptr;
NimBLEScan* glbscan = nullptr;

QueueHandle_t message_queue;
uint8_t message_buffer[4];
const uint8_t message_null[4] = {0,0,0,3};
int queue_size = 20;
TaskHandle_t task_Server, task_Client, task_Reset, task_wifi;
static bool indicate_success = false;
WDT wdt(80);

#endif
