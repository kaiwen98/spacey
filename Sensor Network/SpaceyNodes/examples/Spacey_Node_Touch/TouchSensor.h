#ifndef __TOUCH__
#define __TOUCH__
#include "constants.h"
#include "SpaceyAPI.h"
#include "global.h"

int configure_threshold(int num = 10){
      int max = 0;
      int read = 0;
      for (int i = 0; i < num; i++){
            Blink();
            read = touchRead(4);
            if (read > max){
                  max = read;
            }
      }
      return max*0.95;
}


class TouchSensor {
            int waitTime;
            int threshold;
            TSeated currState = NOT_SEATED;
            TSeated prevState = NOT_SEATED;
            int count = 0;
            int pin;
            int initflag = false;
      public:
            TouchSensor(int _pin, int _threshold, int _waitTime) {
                  pin = _pin;
                  threshold = _threshold;
                  waitTime = _waitTime;
                  initflag = true;
                  Serial.println("Set threshold to: ");
                  Serial.println(threshold);

                 //threshold = int(touchRead(pin) * 0.96);
            }

            int getReading() {
                  return touchRead(pin);
            }

            int reset(){
                  threshold = configure_threshold(3);
            }
            

            TState getTouchState() {
                  int countA = 0;
                  int countB = 0;
                  int countC = 0;
                  TSeated tempState;
                  //if (!occupied) return SEAT_FREE;

                  while (countA < waitTime && countB < waitTime && countC < waitTime) {

                        tempState = touchRead(pin) <= threshold ? IS_SEATED : NOT_SEATED;
                        Serial.println("Touchread: ");
                        Serial.print(touchRead(pin));
                        if (tempState != currState) {
                              prevState = currState;
                              currState = tempState;
                        }

                        
                        if (currState == NOT_SEATED && prevState == NOT_SEATED) {
                              Serial.println("C");
                              countA = 0;
                              countB = 0;
                              countC++;
                        }
                        

                        else if (currState == IS_SEATED && prevState == NOT_SEATED) {
                              Serial.println("A");
                              countB = 0;
                              countC = 0;
                              countA++;
                        }
                        else if (currState == NOT_SEATED && prevState == IS_SEATED) {
                              Serial.println("B");
                              countA = 0;
                              countC = 0;
                              countB++;
                        }

                        else {
                              Serial.println("D");
                        }
                        delay(50);
                  }
                  
                  if(countC >  5){
                        return NO_CHANGE;
                  }
                  if (countA > countB) {
                        prevState = IS_SEATED;
                        return SEAT_OCCUPIED;
                  }
                  else if (countA < countB) {
                        prevState = NOT_SEATED;
                        return SEAT_FREE;
                  }
            }
};

TouchSensor* myTouch = nullptr;


void task_get_touch(void* parameters) {

      uint8_t occupancy;
      while (true) {
            //Stare();
            TState state = myTouch->getTouchState();
            if (state == SEAT_FREE || state == NO_CHANGE) {
                  Serial.println("Seat is free");
                  Chirp();
                  occupancy = 0;
                  fill_message(message_buffer, glb_cluster_num, occupancy);
                  xQueueSend(message_queue, message_buffer, portMAX_DELAY);
            }
            else if (state == SEAT_OCCUPIED) {
                  Serial.println("Seat is occupied");
                  Chirp();
                  occupancy = 1;

                  fill_message(message_buffer, glb_cluster_num, occupancy);
                  xQueueSend(message_queue, message_buffer, portMAX_DELAY);
            }
            /*

            else if(state == NO_CHANGE){
                  Serial.println("Sleep");
                  esp_deep_sleep_start();
            }*/
      }
}



#endif
