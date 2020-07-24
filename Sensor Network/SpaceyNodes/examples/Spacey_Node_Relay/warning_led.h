#ifndef __LED__
#define __LED__
#include "global.h"

int LED_BUILTIN = 2;
void BlinkWarning(int  _delay) {
      for (int i = 0; i < 3; i ++) {
            if ( _delay == -1) break;
            digitalWrite(LED_BUILTIN, HIGH);
            delay(_delay);
            digitalWrite(LED_BUILTIN, LOW);
            delay(_delay);
      }
}

void BlinkFreeze(int  _delay) {
      for (int i = 0; i < 3; i ++) {
            if ( _delay == -1) break;
            digitalWrite(LED_BUILTIN, HIGH);
            delay(_delay);
            digitalWrite(LED_BUILTIN, LOW);
            delay(_delay);
      }
}

void Stare() {
      digitalWrite(LED_BUILTIN, HIGH);
      delay(5000);
      digitalWrite(LED_BUILTIN, LOW);

}

void Chirp() {
      int _delay = 200;
      for (int i = 0; i < 2; i ++) {
            if ( _delay == -1) break;

            digitalWrite(LED_BUILTIN, HIGH);
            delay(_delay);
            digitalWrite(LED_BUILTIN, LOW);
            delay(_delay);
      }
}

void Blink() {
      int _delay = 200;
      digitalWrite(LED_BUILTIN, HIGH);
      delay(_delay);
      digitalWrite(LED_BUILTIN, LOW);
      delay(_delay);
}
#endif
