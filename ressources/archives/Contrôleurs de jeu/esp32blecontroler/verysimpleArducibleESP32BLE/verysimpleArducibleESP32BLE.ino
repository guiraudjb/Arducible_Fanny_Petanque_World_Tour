/**
   This example turns the ESP32 into a Bluetooth LE keyboard that writes the words, presses Enter, presses a media key and then Ctrl+Alt+Delete
*/
#include <BleKeyboard.h>
BleKeyboard bleKeyboard ("Arducible v2", "DIY", 100);
const int Cible1 = 25;
const int Cible2 = 26;
const int Cible3 = 27;

void setup() {
  pinMode(Cible1, INPUT);
  pinMode(Cible2, INPUT);
  pinMode(Cible3, INPUT);
  bleKeyboard.begin();
}

void loop() {
  if (bleKeyboard.isConnected()) {
    if (digitalRead(Cible1)) {
      bleKeyboard.press('e');
//      delay(100);
    }
    else {
      bleKeyboard.release('e');
  //    delay(100);
    }

    if (digitalRead(Cible2)) {
      bleKeyboard.press('r');
    //  delay(100);
    } else {
      bleKeyboard.release('r');
     // delay(100);
    }

    if (digitalRead(Cible3)) {
      bleKeyboard.press('t');
      //delay(100);
    }
    else {
      bleKeyboard.release('t');
      //delay(100);
    }

  }

}
