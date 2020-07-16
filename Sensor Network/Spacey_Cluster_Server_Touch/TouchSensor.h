#ifndef __TOUCH__
#define __TOUCH__
#include <constants.h>
#include <packet.h>
#include "Arduino.h"

class TouchSensor{
  int waitTime;
  int threshold;
  TSeated currState = NOT_SEATED;
  TSeated prevState = NOT_SEATED;
  TState state = SEAT_FREE;
  int count = 0;
  int pin;
  public: 
    TouchSensor(int _pin, int _threshold, int _waitTime){
      pin = _pin;
      threshold = _threshold;
      waitTime = _waitTime;
     // threshold = int(touchRead(pin) * 0.95);
    }

    int getReading(){
      return touchRead(pin);
    }
    
    TState getTouchState(){
      currState = touchRead(pin) <= threshold? IS_SEATED:NOT_SEATED;
      if (prevState != currState) count++;
      
      if(prevState == NOT_SEATED && currState == IS_SEATED && count > waitTime) {
        prevState = currState;
        count = 0;
        currState = NOT_SEATED;    
        return SEAT_OCCUPIED;
      }
      else if(prevState == IS_SEATED && currState == NOT_SEATED && count > waitTime){
        prevState = currState;
        count = 0;
        return SEAT_FREE;
      }
      else {
        currState = NOT_SEATED;    
        return NO_CHANGE;
      }    
   } 
};
#endif
