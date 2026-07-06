#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27,20,4);
#include <Adafruit_NeoPixel.h>
#define PIN        10 // 
#define NUMPIXELS 3 // 
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
const int reserveLedCible = -1; 
int intensiteLed=255;
int boutonG = 7;
int boutonD = 8;
int cible1 = 11;
int cible2 = 12;
int cible3 = 13;
int Buzzer = 2;
int cibleEnCours = 0;
int cibleTouchee = 0;
int GameTimer = 120;
int currentMillis=0;
int previousMillis=0;
int ListeCibles[] = {1,3,2,3,1,2,1,2,3};
int posCible=0;
int Score=0;

uint8_t custChar[8][8] = {
{
  B11111,
  B11111,
  B11111,
  B00000,
  B00000,
  B00000,
  B00000,
  B00000
},// Small top line - 0

{
  B00000,
  B00000,
  B00000,
  B00000,
  B00000,
  B11111,
  B11111,
  B11111
},// Small bottom line - 1


{
  B11111,
  B00000,
  B00000,
  B00000,
  B00000,
  B11111,
  B11111,
  B11111
},// Small lines top and bottom -2


{
  B11111,
  B11111,
  B11111,
  B00000,
  B00000,
  B00000,
lcd.setCursor(0,0);
  B11111,
  B11111
}, // -3



{
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B01111,
  B00111
},// Left bottom chamfer full - 4

{
  B11100,
  B11110,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111
},// Right top chamfer full -5


{
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11110,
  B11100
},// Right bottom chamfer full -6

{
  B00111,
  B01111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111,
  B11111
},// Left top chamfer full -7
 
};

// Define our numbers 0 thru 9
// 254 is blank and 255 is the "Full Block"
uint8_t bigNums[38][6] = {
  {7, 0, 5, 4, 1, 6}, //0
  {0, 5, 254, 1, 255, 1},     //1
  {0, 0, 5, 4, 2, 2},         //2
  {3, 3, 5, 2, 2, 6},         //3
  {4, 1, 5, 254, 254, 255},   //4
  {255, 3, 3, 2, 2, 6},       //5 
  {7, 3, 3, 4, 2, 6},         //6 
  {0, 0, 5, 254, 7, 254},     //7 
  {7, 3, 5, 4, 2, 6},         //8 
  {7, 3, 5, 254, 254, 6},     //9
  {0, 3, 5, 254, 2, 254},//? 10
  {254, 255, 254, 254, 2, 254},//! 11 
 {7, 3, 5, 255, 254, 255}, //A 12
 {255, 3, 6, 255, 2, 5}, //B 13
 {7, 0, 0, 4, 1, 1}, //C 14
 {255, 0, 5, 255, 1, 6}, //D 15
 {255, 3, 3, 255, 2, 2}, //E 16
 {255, 3, 3, 255, 254, 254}, //F 17
 {7, 0, 0, 4, 1, 5}, //G 18
{255, 1, 255, 255, 254, 255},  //H 19
 {0, 255, 0, 1, 255, 1}, //I 20
 {254, 254, 255,1,1, 6}, //J 21
 {255, 1, 6, 255, 254, 5}, //K 22
 {255, 254, 254, 255, 1, 1}, //L 23
 {5,1,7,255,254,255}, //M 24
 {5,1,255,255,0,4}, //N 25
 {7, 0, 5, 4, 1, 6}, //O 26
 {255, 3, 5, 255, 254, 254}, //P 27
 {7,0,5,4,1,255}, //Q 28
 {255, 3, 5, 255, 254,5}, //R 29
 {7, 3, 3, 2, 2,6}, //S 30
 {0, 255, 0, 254, 255, 254}, //T 31
 {255, 254, 255, 4, 1, 6}, //U 32
 {5, 254, 7, 4, 1, 6}, //V 33
 {5, 1, 7, 4,255, 6}, //W 34
 {4, 1, 6, 7, 254, 5}, //X 35
 {4,1,6,254,255,254}, //Y 36
 {0,3,6,7,2,1}, //Z 37
  
};


void setup() {                
    pinMode(boutonG, INPUT_PULLUP);
    pinMode(boutonD, INPUT_PULLUP);
    pinMode(cible1,INPUT);
    pinMode(cible2,INPUT); 
    pinMode(cible3,INPUT);
    pixels.begin();
    pixels.clear();
    pixels.show(); 
    lcd.init();
    lcd.backlight();

    for (int cnt = 0; cnt < sizeof(custChar) / 8; cnt++) {
        lcd.createChar(cnt, custChar[cnt]);
    }
    Serial.begin(9600);
    randomSeed(analogRead(0)); //lier la génération de nombre aléatoire au port analogique 1
	
 // credit();    // turn the LED off by making the voltage LOW
	RunNewGame();
	}


void loop()
{
    currentMillis = millis();
if (currentMillis - previousMillis > 1000){
    previousMillis=currentMillis;
    currentMillis = millis();
    GameTimer = GameTimer - 1;
    AffichageTimer();
}
if (GameTimer <= 0){
  Ending();
}
  
  if (digitalRead(cible1)){
  cibleTouchee=1;
  checkGoodTargetHitted();
  }

  if (digitalRead(cible2)){
  cibleTouchee=2;
  checkGoodTargetHitted();
  }
    if (digitalRead(cible3)){
  cibleTouchee=3;
  checkGoodTargetHitted();
  }




}

void RunNewGame(){
cibleEnCours=ListeCibles[posCible];
posCible=0;
GameTimer=120;
Score=0;
  getReady();
  pixels.clear();
  pixels.show();
  pixels.setPixelColor(cibleEnCours+reserveLedCible, pixels.Color(0, intensiteLed, 0));

  pixels.show();   // Mise a jour de la couleur des leds. 
  previousMillis=millis();
}

void checkGoodTargetHitted(){
if (cibleTouchee==cibleEnCours){
  soundHit();
  GameTimer=GameTimer+5;
  Score=Score+1;
  AffichageTimer();
  if(posCible < 8){
    posCible=posCible+1;
    cibleEnCours=ListeCibles[posCible];
   }
   else
   {
    Ending();
   }

  pixels.clear();
  pixels.show();
  delay(100);
  pixels.setPixelColor(cibleEnCours+reserveLedCible, pixels.Color(0, intensiteLed, 0));
  pixels.show();   // Mise a jour de la couleur des leds. 
  
}
else
{
  GameTimer=GameTimer-1;
  Score=Score-1;
  soundMiss();
  AffichageTimer();

}
}


void soundHit(){
  tone(Buzzer,988,125);
  delay(125);
  noTone(Buzzer);
  tone(Buzzer,1319,600);
  delay(600);
  noTone(Buzzer);
}

void soundMiss(){
  tone(Buzzer,450,500);
  delay(500);
  noTone(Buzzer);
  tone(Buzzer,350,600);
  delay(600);
  noTone(Buzzer);
}


void AffichageTimer(){
   lcd.clear();
    String scorestring = String(GameTimer);
    if (scorestring.length()==3){
      String centaine = String(scorestring.charAt(0));
      printBigNum(centaine.toInt(), 5, 1);
      String decimale = String(scorestring.charAt(1));
      printBigNum(decimale.toInt(), 8, 1);
      String unite = String(scorestring.charAt(2));
      printBigNum(unite.toInt(), 11, 1);
    }
    else if (scorestring.length()==2){
      String decimale = String(scorestring.charAt(0));
      printBigNum(decimale.toInt(), 8, 1);
      String unite = String(scorestring.charAt(1));
      printBigNum(unite.toInt(), 11, 1);
    }
    else{
      String unite = String(scorestring.charAt(0));
      printBigNum(0, 8, 1);
      printBigNum(unite.toInt(), 11, 1);
    }
    lcd.setCursor(0,3);
    lcd.print(F("Points : "));
    lcd.setCursor(9,3);
    lcd.print(Score);
  
}

void printBigNum(int number, int startCol, int startRow) {
  // Position cursor to requested position (each char takes 3 cols plus a space col)
  lcd.setCursor(startCol, startRow);
  // Each number split over two lines, 3 chars per line. Retrieve character
  // from the main array to make working with it here a bit easier.
  uint8_t thisNumber[6];
  for (int cnt = 0; cnt < 6; cnt++) {
    thisNumber[cnt] = bigNums[number][cnt];
  }
  // First line (top half) of digit
  for (int cnt = 0; cnt < 3; cnt++) {
    lcd.print((char)thisNumber[cnt]);
  }
  // Now position cursor to next line at same start column for digit
  lcd.setCursor(startCol, startRow + 1);
  // 2nd line (bottom half)
  for (int cnt = 3; cnt < 6; cnt++) {
    lcd.print((char)thisNumber[cnt]);
  }
}






void credit(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(F("Arducible CC BY-SA 4"));
  lcd.setCursor(0,1);
  lcd.print(F("    BY GUIRAUD JB   "));
  lcd.setCursor(0,2);
  lcd.print(F("create.arduino.cc/"));
  lcd.setCursor(0,3);
  lcd.print(F("projecthub/guiraudjb"));
  // temporisation et appel du mode debug  
  unsigned long currentMillis = millis();
  unsigned long previousMillis = millis();
  while (currentMillis - previousMillis < 7000){
    currentMillis = millis();
/*      if ( statusBoutonG==0 &&  statusBoutonD==0){
          while (true){
          AcquisitionCapteurs();
          lcd.clear();
          lcd.setCursor(0,0);
          lcd.print("BG " + String(statusBoutonG) +" BD " + String(statusBoutonD) );
          lcd.setCursor(0,1);
          lcd.print(" C1 " + String(statusCible1) + " C2 " + String(statusCible2) + " C3 " + String(statusCible3));
          delay(100);  
          } 
      }
      */
  }
}

  void Ending(){
  lcd.clear();
  pixels.clear();
  pixels.show();
  tone(Buzzer,450,125);
  delay(600);
  noTone(Buzzer);
  tone(Buzzer,450,125);
  delay(600);
  noTone(Buzzer);
  tone(Buzzer,450,125);
  delay(600);
  noTone(Buzzer);
  
  lcd.setCursor(0,0);
  lcd.print(F("FINAL SCORE"));
  String scorestring = String(GameTimer+Score);
    if (scorestring.length()==3){
      String centaine = String(scorestring.charAt(0));
      printBigNum(centaine.toInt(), 5, 1);
      String decimale = String(scorestring.charAt(1));
      printBigNum(decimale.toInt(), 8, 1);
      String unite = String(scorestring.charAt(2));
      printBigNum(unite.toInt(), 11, 1);
    }
    else if (scorestring.length()==2){
      String decimale = String(scorestring.charAt(0));
      printBigNum(decimale.toInt(), 8, 1);
      String unite = String(scorestring.charAt(1));
      printBigNum(unite.toInt(), 11, 1);
    }
    else{
      String unite = String(scorestring.charAt(0));
      printBigNum(0, 8, 1);
      printBigNum(unite.toInt(), 11, 1);
    }
lcd.setCursor(0,3);
    lcd.print(F("Points : "));
    lcd.setCursor(9,3);
    lcd.print(Score);

lcd.setCursor(0,0);
    lcd.print(F("Temps restant : "));
    lcd.setCursor(16,0);
    lcd.print(GameTimer);
    
    
  delay(20000);
    lcd.clear();

  RunNewGame();  
}

void getReady(){

  lcd.clear();
  pixels.clear();
  pixels.show();
  lcd.setCursor(5,2);
  lcd.print(F("GET READY!"));
  tone(Buzzer,450,250);
  delay(1000);
  noTone(Buzzer);
  tone(Buzzer,450,250);
  delay(1000);
  noTone(Buzzer);
  tone(Buzzer,750,500);
  delay(500);
  noTone(Buzzer);
  lcd.clear();
}
