/**
 * This example turns the ESP32 into a Bluetooth LE keyboard that writes the words, presses Enter, presses a media key and then Ctrl+Alt+Delete
 */
#include <BleKeyboard.h>
BleKeyboard bleKeyboard("ArduciblePetanqueGame");
#include <Arduino.h>
#include <TM1637Display.h>
#include <Adafruit_NeoPixel.h>
#define PIN        14 // On Trinket or Gemma, suggest changing this to 1
#define NUMPIXELS 3 // Popular NeoPixel ring size
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
#define CLK 16
#define DIO 17
#define TEST_DELAY   1000
TM1637Display display(CLK, DIO);
#include <ToneESP32.h>
#define BUZZER_PIN 12
#define BUZZER_CHANNEL 0
ToneESP32 buzzer(BUZZER_PIN, BUZZER_CHANNEL);

const int Cible1 = 25;
const int Cible2 = 26;
const int Cible3 = 27;
const int btn1 = 8;
const int btn2 = 9;
int Buzzer = 12;
int timeToHitGlobalSetting = 200;
int timeToHit = 20;
int targetToHit = 2;
int oldTargetToHit = 2;
int numberTargetToHit = 9;
int score = 0;
bool malus = 0;

unsigned long timer;
unsigned long timer2;

const uint8_t SEG_GOOO[] = {
  SEG_G,
  SEG_A | SEG_C | SEG_D | SEG_E | SEG_G | SEG_F,           // G
  SEG_A | SEG_B | SEG_C | SEG_D | SEG_E | SEG_F,   // O
  SEG_G,

};


void setup() {
  bleKeyboard.begin();
  pinMode(Cible1, INPUT);
  pinMode(Cible2, INPUT);
  pinMode(Cible3, INPUT);
  pinMode(btn1, INPUT_PULLUP);
  pinMode(btn2, INPUT_PULLUP);
  randomSeed(analogRead(0));
  display.setBrightness(0x0f);


}

void loop() {
  if(bleKeyboard.isConnected()) {
    display.setSegments(SEG_GOOO);
    if(digitalRead(Cible1)){
    Serial.println("e");
    bleKeyboard.press('e');
    delay(100);
    bleKeyboard.release('e');
    delay(100);
    }
        if(digitalRead(Cible2)){
    Serial.println("r");
    bleKeyboard.press('r');
    delay(100);
    bleKeyboard.release('r');
    delay(100);
        }
            if(digitalRead(Cible3)){
    Serial.println("t");
    bleKeyboard.press('t');
    delay(100);
    bleKeyboard.release('t');
    delay(100);
      }
  }
  else{
 score = 0;

    for (int i = 0; i < numberTargetToHit; i++) {
      if(bleKeyboard.isConnected()) {
        break;
      }
      timeToHit = timeToHitGlobalSetting;
      RandomTarget();
      if ( i % 3 == 0 ){
      countdown();
      }
      showTarget();
      while (timeToHit > 0) {
      if (! digitalRead(btn1) && ! digitalRead(btn2)) {
      //tone(Buzzer, 950, 100);
      }
      if(bleKeyboard.isConnected()) {
        break;
      }
      
      if (millis() - timer > 100 ) {
            timer = millis();
            timeToHit = timeToHit - 1;
            display.showNumberDecEx(timeToHit, (0x80 >> 2), false);
          }
      if (digitalRead(Cible1)) {
        if (targetToHit == 1) {
          pixels.setPixelColor(0, pixels.Color(0, 255, 0));
          pixels.show();
          score = score + timeToHit;
            if (malus == 1) {
              score = score - 100;
              malus = 0;
            }
          display.showNumberDecEx(score, true);
          soundHit();
          delay(2000);
          break;
        }
        else
        {
          malus = 1;
          soundMiss();
          pixels.setPixelColor(0, pixels.Color(255, 0, 0));
          pixels.show();

        }

      }

      if (digitalRead(Cible2)) {

        if (targetToHit == 2) {
          pixels.setPixelColor(1, pixels.Color(0, 255, 0));
          pixels.show();
          score = score + timeToHit;
            if (malus == 1) {
            score = score - 100;
            malus = 0;
            }
          display.showNumberDecEx(score, true);
          soundHit();
          delay(2000);
          break;
        }
        else
        {
          malus = 1;
          soundMiss();
          pixels.setPixelColor(1, pixels.Color(255, 0, 0));
          pixels.show(); pixels.show();
        }

      }

      if (digitalRead(Cible3)) {

        if (targetToHit == 3) {
          pixels.setPixelColor(2, pixels.Color(0, 255, 0));
          pixels.show();
          score = score + timeToHit;
            if (malus == 1) {
              score = score - 100;
              malus = 0;
          }
          display.showNumberDecEx(score, true);
          soundHit();
          delay(2000);
          break;
        }
        else
        {
          malus = 1;
          soundMiss();
          pixels.setPixelColor(2, pixels.Color(255, 0, 0));
          pixels.show();
        }
      }
    }
  }
  pixels.clear();
  pixels.show();
  if (malus == 1) {
    score = score - 100;
    malus = 0;
  }
  display.showNumberDecEx(score, true);
//  Musique();
     
  


}
}


void RandomTarget() {
  while (targetToHit == oldTargetToHit)
  {
    targetToHit = random(1, 4);
  }
  oldTargetToHit = targetToHit;

}

void showTarget() {
  pixels.clear();
  pixels.show();
  pixels.setPixelColor(targetToHit - 1, pixels.Color(0, 0, 255));
  pixels.show();   // Mise a jour de la couleur des leds.
}

void countdown() {
  buzzer.tone(523,100);
  display.showNumberDec(3, false); // Expect: __3_
  delay(TEST_DELAY);
  buzzer.tone(523,100);
  display.showNumberDec(2, false); // Expect: __2_
  delay(TEST_DELAY);
  buzzer.tone(523,100);
  display.showNumberDec(1, false); // Expect: __1_
  delay(TEST_DELAY);
  buzzer.tone(1046,1000);
 display.setSegments(SEG_GOOO);
  delay(TEST_DELAY);
}

void soundHit() {
  buzzer.tone(988, 125);
  delay(125);
  //buzzer.noTone();
  buzzer.tone(1319, 600);
  delay(600);
  //buzzer.noTone();
}

void soundMiss() {
  buzzer.tone(350, 1000);

}
