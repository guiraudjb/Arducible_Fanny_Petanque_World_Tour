#include <Keyboard.h>
const int b1 = 2;
const int b2 = 3;
const int b3 = 4;
const int b4 = 5;
const int Cible1 = 6;   
const int Cible2 = 7;   
const int Cible3 = 8;

void setup() {                
  pinMode(b1, INPUT_PULLUP);
  pinMode(b2, INPUT_PULLUP);
  pinMode(b3, INPUT_PULLUP);
  pinMode(b4, INPUT_PULLUP);
  pinMode(Cible1,INPUT);
  pinMode(Cible2,INPUT); 
  pinMode(Cible3,INPUT); 
  Keyboard.begin();
delay(10000);  
}



void loop(){


if(digitalRead(b1)) {
        Keyboard.release(KEY_LEFT_ARROW);
    } else {
        Keyboard.press(KEY_LEFT_ARROW); 
    }
    
    
if(digitalRead(b2)) {
        Keyboard.release(KEY_UP_ARROW); 
    } else {
        Keyboard.press(KEY_UP_ARROW);
    }
        
    if(digitalRead(b3)) {
        Keyboard.release(KEY_DOWN_ARROW);
    } else {
        Keyboard.press(KEY_DOWN_ARROW); 
    }
    
    if(digitalRead(b4)) {
        Keyboard.release(KEY_RIGHT_ARROW); 
    } else {
        Keyboard.press(KEY_RIGHT_ARROW);
    }
    

    if(digitalRead(Cible1)) {
       Keyboard.press('e');  
      
    } else {
    Keyboard.release('e');
    }
    
    if(digitalRead(Cible2)) {
        Keyboard.press('r');
    } else {
        Keyboard.release('r'); 
    }
    if(digitalRead(Cible3)) {
        Keyboard.press('t');
    } else {
        Keyboard.release('t');
    }

  
}
