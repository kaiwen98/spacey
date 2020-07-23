#ifndef __WDT__
#define __WDT__
#include "esp_system.h"
#include "global.h"

// Executed when the watchdog timer triggers a reboot
void IRAM_ATTR resetModule() {
  Serial.println("reboot");
  ets_printf("reboot\n");
  esp_restart();
}

class WDT{
  hw_timer_t* timer = NULL;
  public: 
    WDT(int div){
      timer = timerBegin(0, div, true);                  //timer 0, div 80
    }
    
    void init_wdt(const int  wdtTimeout) {
      timerAttachInterrupt(timer, &resetModule, true);  //attach callback
      timerAlarmWrite(timer, wdtTimeout * 1000, false); //set time in us
      timerAlarmEnable(timer);                          //enable interrupt
    }

    void stop(){
      timerAlarmDisable(timer);
    }

    void reset(){
      timerWrite(timer, 0); //reset timer (feed watchdog)
    }
};

#endif
