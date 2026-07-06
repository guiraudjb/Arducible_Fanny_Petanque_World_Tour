#include <Wire.h> 
#include <LiquidCrystal_I2C.h>
LiquidCrystal_I2C lcd(0x27,20,4);
#include <Adafruit_NeoPixel.h>
#include <Keyboard.h>
#define PIN        10 // 
#define NUMPIXELS 3 // 
Adafruit_NeoPixel pixels(NUMPIXELS, PIN, NEO_GRB + NEO_KHZ800);
const int reserveLedCible = -1; 
int intensiteLed=255;
int nbCibles=3;
int boutonG = 7;
int boutonD = 8;
int cible1 = 11;
int cible2 = 12;
int cible3 = 13;
int Buzzer = 2;
bool statusBoutonG;
bool statusBoutonD;
bool statusCible1;
bool statusCible2;
bool statusCible3;

//variables pour la gestion du jeu

int nbJoueurs = 1;
int oldNbJoueurs = 0;
int joueurEnCours = 1;
int tourEnCours = 1;
int nbTours = 3;
int oldCible[] = {0,0,0};
int cibleEnCours = 1;
int cibleTouchee = 0;
int resteEnCours = 3;
int R=0;
int G=0;
int B=0;
int scores[] = {0,0,0,0,0,0};
int tauxReussite[] = {0,0,0,0,0,0};
int oldClassement[] = {0,0,0,0,0,0};
int classement[] = {0,0,0,0,0,0};
int pointBonus[] = {0,0,0,0,0,0};
boolean killer[] = {0,0,0,0,0,0};
int levels[] = {0,0,0,0,0,0};
boolean initialisation = 1;
boolean partieEnCours = 0;
boolean partieFinie = 0;
bool debugMode=false;
int delaiTemporisation = 1000;
String tabScores[5];

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
    Keyboard.begin();
    for (int cnt = 0; cnt < sizeof(custChar) / 8; cnt++) {
        lcd.createChar(cnt, custChar[cnt]);
    }
    Serial.begin(9600);
    randomSeed(analogRead(0)); //lier la génération de nombre aléatoire au port analogique 1
	
	if (UDADDR & _BV(ADDEN))
  {

  UsbPCGameControler();   // turn the LED on (HIGH is the voltage level)
  }
  else
  {
  credit();    // turn the LED off by making the voltage LOW
  }
	
	
}


void loop()
{
  AcquisitionCapteurs(); 
  Serial.println("BoutonG" + String(statusBoutonG) +" BoutonD" + String(statusBoutonD) + " cible1 " + String(statusCible1) + " cible2 " + String(statusCible2) + " cible3 " + String(statusCible3));
  if (initialisation==true){
    pixels.clear();
    pixels.show();
    InitGame();
  }  
    
  if (partieEnCours==true){trtPartieEnCours();}
  
  if ( partieFinie==true ){trtPartieFinie();}
} 



void GererInterruption()
{
  if ( joueurEnCours == nbJoueurs && tourEnCours == nbTours && resteEnCours == 1 ){
    testKiller();
    partieEnCours = false;
    partieFinie = true;
  }
  else if (  joueurEnCours == nbJoueurs && resteEnCours == 1 ){
    testKiller();
    joueurEnCours = 1;
    resteEnCours = 3;
resetHistoriqueCibles();
    pixels.clear();
    pixels.show();
    tourEnCours++;
    EcranScores();
    EcranTourSuivant();
    EcranJoueurSuivant();
  }
  else if ( resteEnCours != 1 ){
    resteEnCours--; 
  }  
  else
  {
    testKiller();
    joueurEnCours++;
    resteEnCours = 3;
resetHistoriqueCibles();
    pixels.clear();
    pixels.show();
    EcranScores();
    EcranJoueurSuivant();
  }
}


void InitGame(){
  tourEnCours = 1;
  joueurEnCours = 1;
  resteEnCours = 3;
  
  for(int i=1; i<=5; i++){
    scores[i] = 0;
    killer[i] = 0;
    levels[i] = 0;
    pointBonus[i] =0;
    oldClassement[i] = 0;
    classement[i] = 0;
  }
 
  
  statusBoutonG = digitalRead(boutonG);
  statusBoutonD = digitalRead(boutonD); 
    if (statusBoutonG==LOW){
        while(statusBoutonG==LOW){
          AcquisitionCapteurs();
          delay(100);
        }
        if (nbJoueurs == 5){
          nbJoueurs = 1;
        }
        else
        {
          nbJoueurs++;
        }
    }
    if (nbJoueurs != oldNbJoueurs){
      EcranInitialisation();
      oldNbJoueurs=nbJoueurs;
    }
    if (statusBoutonD==LOW){ 
        for (int i = 1; i <= nbJoueurs ; i++) {
          killer[i] = 1;
        } 
      EcranWait();
      Temporisation();  
      initialisation = false;
      partieEnCours = true;  
    }
}

  
void trtPartieEnCours(){
    cibleAleatoire();
    EcranWait();
    Temporisation();
    soundReadyToShot();
    pixels.clear();
    pixels.show();   // Mise a jour de la couleur des leds. 
    EcranEnJeu();
      while(statusBoutonG==HIGH && statusBoutonD==HIGH && statusCible1==LOW && statusCible2==LOW && statusCible3==LOW){
        AcquisitionCapteurs();
        afficherMoniteurSerie();
      }
    determinerCibleTouchee();
      if (cibleTouchee == cibleEnCours){
        scores[joueurEnCours] = scores[joueurEnCours]+1+pointBonus[joueurEnCours];
          if(pointBonus[joueurEnCours] < 2){
          pointBonus[joueurEnCours] = pointBonus[joueurEnCours]+1;
          }
        EcranHit();
        soundHit();
          for (int i=0; i<4;i++){
            pixels.clear();
            pixels.show();
            delay(100);
            pixels.setPixelColor(cibleEnCours+reserveLedCible, pixels.Color(0, intensiteLed, 0));
            pixels.show();   // Mise a jour de la couleur des leds. 
            delay(100);
          }
        pixels.clear();
        pixels.show();
        determinerRang();
          
      }
      else{
        pixels.show();   // Mise a jour de la couleur des leds. 
        EcranMiss();
        soundMiss();
           for (int i=0; i<4;i++){
             pixels.clear();
             pixels.show();
             delay(100);
             pixels.setPixelColor(cibleEnCours+reserveLedCible, pixels.Color(0, 0, intensiteLed));
             pixels.setPixelColor(cibleTouchee+reserveLedCible, pixels.Color(intensiteLed, 0, 0));
             pixels.show();   // Mise a jour de la couleur des leds. 
             delay(100);
           }
         pixels.clear();
         pixels.show();  
         pointBonus[joueurEnCours] = 0;
         killer[joueurEnCours] = 0; 
      }
    GererInterruption();
  }

void trtPartieFinie(){
  //gestion contest
    while(killer[1]==1 || killer[2]==1 || killer[3]==1 || killer[4]==1 || killer[5]==1){
      Serial.println("KILLER STATUS J1 " + String(killer[1]) + String(killer[2]) + String(killer[3]) + String(killer[4]) + String(killer[5]) );   
        for (int i = 1; i <= nbJoueurs ; i++){
          if (killer[i] == 1){
            joueurEnCours = i;
            extraBall();
          }
        } 
    }
  partieFinie = false;
  partieEnCours = false;
  initialisation = true;
  oldNbJoueurs = 0;
  triclassement();
  //credit();
  AfficheFin();
}

void extraBall(){
  resetHistoriqueCibles();
  cibleAleatoire();
  EcranJoueurSuivant();
  lcd.clear();
  EcranTirBonus();
  //EcranWait();
  Temporisation();
  EcranGo();
  pixels.clear();
  pixels.show();   // Mise a jour de la couleur des leds. 
  soundReadyToShot();
  EcranEnJeu();
    while(statusBoutonG==HIGH && statusBoutonD==HIGH && statusCible1==LOW && statusCible2==LOW && statusCible3==LOW){
      AcquisitionCapteurs();
      afficherMoniteurSerie();
    }
  determinerCibleTouchee();
    if (cibleTouchee == cibleEnCours){
      scores[joueurEnCours] = scores[joueurEnCours]+1+pointBonus[joueurEnCours];
      EcranHit();
      soundHit();
        for (int i=0; i<4;i++){
          pixels.clear();
          pixels.show();
          delay(100);
          pixels.setPixelColor(cibleEnCours+reserveLedCible, pixels.Color(0, intensiteLed, 0));
          pixels.show();   // Mise a jour de la couleur des leds. 
          delay(100);
        }
      determinerRang();
       
    }
    else{
      EcranMiss();
      soundMiss();
        for (int i=0; i<4;i++){
          pixels.clear();
          pixels.show();
          delay(100);
          pixels.setPixelColor(cibleEnCours+reserveLedCible, pixels.Color(intensiteLed, 0, 0));
          pixels.show();   // Mise a jour de la couleur des leds. 
          delay(100);
        }
      pointBonus[joueurEnCours] = 0;
      killer[joueurEnCours] = 0; 
    }
}

  


void testKiller(){
  if (killer[joueurEnCours] == 1){
    EcranSansFautes();
  }
}


void triclassement(){
//***********************************************************************************************
// classer classement[] = {0,0,0,0,0};int scores[] = {0,0,0,0,0};
// pour ne pas faire le tri plusieurs fois, sera mis  1  la fin du traitement, remis  0 au dpart de la partie suivante
// remplissage du tableau de classement
classement[1]=1;
classement[2]=2;
classement[3]=3;
classement[4]=4;
classement[5]=5;
// tri  bulle
  do
    { // boucle do/while
    classement[0]=0; // sera utilis dans le tri comme flag de permutation
      for (int i = 1 ; i < 5 ; i++)
        { // on parcourt le tableau
          if (scores[classement[i]]<scores[classement[i+1]])
            { // si le score de l'lment est <  l'lment suivant, on permute
            classement[0]=classement[i];          // on stocke le premier lment
            classement[i]=classement[i+1];          // on remonte le suivant
            classement[i+1]=classement[0];          // on termine la permutation
            classement[0]=1;                // on passe le flag de permutation  1
            } // fin if
          } // fin for
    } 
  while (classement[0]==1); // tant qu'on a fait une permutation, on recommence.
//*******************************************************************************************************   
}



void ScoresStringFin(){
 tabScores[0]=(" 1ER : J" + String(classement[1])+ " SCORE " + String(scores[classement[1]]));
 tabScores[1]=(" 2EM : J" + String(classement[2])+ " SCORE " + String(scores[classement[2]]));
 tabScores[2]=(" 3EM : J"  + String(classement[3])+ " SCORE " + String(scores[classement[3]]));
 tabScores[3]=(" 4EM : J"  + String(classement[4])+ " SCORE " + String(scores[classement[4]]));
 tabScores[4]=(" 5EM : J" + String(classement[5])+ " SCORE " + String(scores[classement[5]]));
}



void AfficheFin(){
  
 // variables pour l'animation
 int indexScrollScore=0;
 unsigned long currentMillis = millis();
 unsigned long previousMillis = millis();
 unsigned long period = 1500;
  
 //EcranWait();
 Temporisation();
 ScoresStringFin(); 
 
 while(statusBoutonD==HIGH){
   
   currentMillis = millis(); // rcupre le temp actuel
   if (currentMillis - previousMillis >= period) { // check si "period" dpasse
     previousMillis = currentMillis;   // sauve
     EcranFinScores(indexScrollScore);
     
     indexScrollScore++;
     if (indexScrollScore>4)
       {indexScrollScore=0;}
   
   }  
  
  AcquisitionCapteurs();
  }
  
  
  delay(500);
  
    while(statusBoutonD==LOW){
      couleurAleatoire();
      delay(200);
      AcquisitionCapteurs();
      tone(Buzzer,450,125);
      delay(125);
      noTone(Buzzer);
    }
}

void determinerRang(){
    if (scores[joueurEnCours] < 1)                               {classement[joueurEnCours]=0;}
    if (scores[joueurEnCours] >0   && scores[joueurEnCours]<3)   {classement[joueurEnCours]=1;}
    if (scores[joueurEnCours] >2   && scores[joueurEnCours]<5)   {classement[joueurEnCours]=2;}
    if (scores[joueurEnCours] >4   && scores[joueurEnCours]<27)  {classement[joueurEnCours]=3;}
    if (scores[joueurEnCours] >26  && scores[joueurEnCours]<42)  {classement[joueurEnCours]=4;}
    if (scores[joueurEnCours] >41  && scores[joueurEnCours]<57)  {classement[joueurEnCours]=5;}
    if (scores[joueurEnCours] >56  && scores[joueurEnCours]<72)  {classement[joueurEnCours]=6;}
    if (scores[joueurEnCours] >71  && scores[joueurEnCours]<87)  {classement[joueurEnCours]=7;}
    if (scores[joueurEnCours] >86  && scores[joueurEnCours]<117) {classement[joueurEnCours]=8;}
    if (scores[joueurEnCours] >116 && scores[joueurEnCours]<147) {classement[joueurEnCours]=9;}
    if (scores[joueurEnCours] >146 && scores[joueurEnCours]<222) {classement[joueurEnCours]=10;}
    if (scores[joueurEnCours] >221 && scores[joueurEnCours]<297) {classement[joueurEnCours]=11;}
    if (scores[joueurEnCours] >296 && scores[joueurEnCours]<447) {classement[joueurEnCours]=12;}
    if (scores[joueurEnCours] >446 && scores[joueurEnCours]<597) {classement[joueurEnCours]=13;}
    if (scores[joueurEnCours] >596 && scores[joueurEnCours]<747) {classement[joueurEnCours]=14;}
    if (scores[joueurEnCours] >746 && scores[joueurEnCours]<897) {classement[joueurEnCours]=15;}
    if (scores[joueurEnCours] >897 && scores[joueurEnCours]<1002){classement[joueurEnCours]=16;}
    if (scores[joueurEnCours] >=1002)                            {classement[joueurEnCours]=17;}
    
    if (classement[joueurEnCours] != oldClassement[joueurEnCours]){
            //desactivation du level up
            LevelUp(classement[joueurEnCours]);  
            oldClassement[joueurEnCours]=classement[joueurEnCours];
          }
    
}


void LevelUp(int level){
  const char* texteGrade[] = {"Essaye encore","Pas mal","Assez bien","Bien","Tres bien","Excellent","Soldat","Soldat d elite","Soldat d'excellence","Guerrier","Grand guerrier",
"Super guerrier","Guerrier legendaire","Mega guerrier","Hyper guerrier","Ultime guerrier","Ultra instinct","Game Breaker",};
  if (level > 17 or level<1){level=0;}
  String Grade= texteGrade[level];
  lcd.clear();
  lcd.setCursor(6,1);
  lcd.print(F("LEVEL UP"));
  lcd.setCursor((20-Grade.length())/2,2);
  lcd.print(Grade);
    for (int i=0;i<3;i++){
      lcd.noDisplay();
      delay(500);
      lcd.display();
      delay(500);
    }
}

void AcquisitionCapteurs()
{
  statusBoutonG = digitalRead(boutonG);
  statusBoutonD = digitalRead(boutonD);
  statusCible1 = digitalRead(cible1);
  statusCible2 = digitalRead(cible2);
  statusCible3 = digitalRead(cible3);
}

void determinerCibleTouchee(){
    if (statusCible1 ==  HIGH){
      cibleTouchee = 1;  
    } 
    if (statusCible2 ==  HIGH){
      cibleTouchee = 2;  
    } 
    if (statusCible3 ==  HIGH){
      cibleTouchee = 3;  
    } 
    if (statusBoutonD ==  LOW){
      cibleTouchee = 0;  
    }
    if (statusBoutonG ==  LOW){
      cibleTouchee = cibleEnCours;  
    } 
}

void Temporisation(){
  for (int T = 1; T <= 1000 ; T++){
    while(statusBoutonD==LOW || statusBoutonG==LOW || statusCible1==HIGH || statusCible2==HIGH || statusCible3==HIGH){
      AcquisitionCapteurs();
      afficherMoniteurSerie();
        if (statusCible1==HIGH){
          pixels.setPixelColor(reserveLedCible+1, pixels.Color(255, 0, 0));
        }
        else{
          pixels.setPixelColor(reserveLedCible+1, pixels.Color(0, 0, 0));
        }
        if (statusCible2==HIGH){
          pixels.setPixelColor(reserveLedCible+2, pixels.Color(255, 0, 0));
        }
        else{
          pixels.setPixelColor(reserveLedCible+2, pixels.Color(0, 0, 0));  
        }
        if (statusCible3==HIGH){
          pixels.setPixelColor(reserveLedCible+3, pixels.Color(255, 0, 0));
        }
        else{
          pixels.setPixelColor(reserveLedCible+3, pixels.Color(0, 0, 0));
        }  
      pixels.show();
      tone(Buzzer,450,125);
      delay(125);
      noTone(Buzzer);
      delay(delaiTemporisation);
    }
  }
}


void cibleAleatoire(){
if (oldCible[0] == 0 && oldCible[1] == 0){
 Serial.println("nouvelle série"); 
while(cibleEnCours == oldCible[2])
    {
      cibleEnCours = random(1, 4);
    }
    oldCible[2] = cibleEnCours;
    oldCible[1]=oldCible[0];
    oldCible[0]=cibleEnCours;
}
 else{ 
  Serial.println("série en cours"); 

    while(cibleEnCours == oldCible[0] || cibleEnCours == oldCible[1])
    {
      cibleEnCours = random(1, 4);
    }
  oldCible[1]=oldCible[0];
  oldCible[0]=cibleEnCours;
 }
}


void resetHistoriqueCibles(){
for(int i=0; i<=1; i++){
oldCible[i] = 0; 
}
}

void couleurAleatoire(){
  R= random(0, 100);
  G= random(0, 255);
  B= random(0, 50);  
    for (int led = 0 ; led < 5 ; led++){
      pixels.setPixelColor(led, pixels.Color(R, G, B));
      pixels.show();  
    }
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



void EcranInitialisation()
{
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(F("Arducible Creative- "));
  lcd.setCursor(0,1);
  lcd.print(F("Common BY-SA 4.0    "));
  lcd.setCursor(0,2);
  lcd.print("Nb joueurs : " + String(nbJoueurs) + "      ");
  lcd.setCursor(0,3);
  lcd.print(F("<- NB JOUEURS  OK ->"));
}

void EcranTourSuivant()
{
  lcd.clear();
  printBigNum(31, 2, 1);
  printBigNum(26, 5, 1);
  printBigNum(32, 8, 1);
  printBigNum(29, 11, 1); 
  printBigNum(tourEnCours,15,1);
  delay(1000);
}

void EcranJoueurSuivant()
{
  lcd.clear();
  printBigNum(21, 6, 1);
  printBigNum(joueurEnCours,10,1);
  soundChangePlayer();
  delay(2000);  
}


void EcranWait()
{
  pixels.clear();
  pixels.show();
  lcd.clear();
  printBigNum(34, 3, 1);
  printBigNum(12, 7, 1);
  printBigNum(20, 11, 1);
  printBigNum(31, 15, 1);
}

void EcranGo()
{
  lcd.clear();  
  printBigNum(18, 7, 1);
  printBigNum(26, 11, 1); 
}

void EcranHit()
{
  pixels.clear();
  pixels.show();
  lcd.clear();
  printBigNum(18, 3, 1);
  printBigNum(26, 7, 1);
  printBigNum(26, 11, 1);
  printBigNum(15, 15, 1);
}

void EcranMiss()
{
  pixels.clear();
  pixels.show();
  lcd.clear();
  printBigNum(24, 3, 1);
  printBigNum(20, 7, 1);
  printBigNum(30, 11, 1);
  printBigNum(30, 15, 1);
}


void EcranEnJeu()
  {
  pixels.setPixelColor(reserveLedCible+cibleEnCours, pixels.Color(0, 0, 255));
  pixels.show();   // Mise a jour de la couleur des leds.  
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print("Tour  : "+ String(tourEnCours) + "   POINTS");
  lcd.setCursor(0,1);
  lcd.print("Joueur: " + String(joueurEnCours));
  lcd.setCursor(0,2);
  lcd.print("Reste : " +  String(resteEnCours) );
  lcd.setCursor(0,3);
  lcd.print("Pts bonus:" + String(pointBonus[joueurEnCours]) +" CIBLE: " + String(cibleEnCours));
  String scorestring = String(scores[joueurEnCours]);
    if (scorestring.length()==3){
      String centaine = String(scorestring.charAt(0));
      printBigNum(centaine.toInt(), 10, 1);
      String decimale = String(scorestring.charAt(1));
      printBigNum(decimale.toInt(), 13, 1);
      String unite = String(scorestring.charAt(2));
      printBigNum(unite.toInt(), 16, 1);
    }
    else if (scorestring.length()==2){
      String decimale = String(scorestring.charAt(0));
      printBigNum(decimale.toInt(), 12, 1);
      String unite = String(scorestring.charAt(1));
      printBigNum(unite.toInt(), 15, 1);
    }
    else{
      String unite = String(scorestring.charAt(0));
      printBigNum(0, 12, 1);
      printBigNum(unite.toInt(), 15, 1);
    }
   
}


void EcranScores(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(F(" TABLEAU DES SCORES"));
  lcd.setCursor(0,1);
  lcd.print("J1 : " + String(scores[1]));
  lcd.setCursor(10,1);
  lcd.print("J4 : " + String(scores[4]));
  lcd.setCursor(0,2);
  lcd.print("J2 : " + String(scores[2]));
  lcd.setCursor(10,2);
  lcd.print("J5 : " + String(scores[5]));
  lcd.setCursor(0,3);
  lcd.print("J3 : " + String(scores[3]));
  delay(6000);
}

void EcranSansFautes()
{
  lcd.clear();  
  printBigNum(30, 4, 0);
  printBigNum(12, 7, 0);
  printBigNum(25, 10, 0); 
  printBigNum(30, 13, 0);
  printBigNum(17, 1, 2); 
  printBigNum(12, 4, 2); 
  printBigNum(32, 7, 2); 
  printBigNum(31, 10, 2); 
  printBigNum(16, 13, 2); 
  printBigNum(30, 16, 2);  
  soundHit();
  delay(4000);
}

void EcranTirBonus()
{
  lcd.clear();  
  printBigNum(31, 0, 0);
  printBigNum(20, 3, 0);
  printBigNum(29, 6, 0); 
  printBigNum(13, 4, 2); 
  printBigNum(26, 7, 2); 
  printBigNum(25, 10, 2); 
  printBigNum(32, 13, 2); 
  printBigNum(30, 16, 2);  
  soundHit();
  delay(1000);
}

void EcranFinScores(int a){
  // affiche 3 lignes de scores et OK pour quitter
 lcd.clear();
 for (int i=0;i<=2;i++){
   lcd.setCursor(0,i);
   lcd.print(tabScores[a]);
   a++;
   if (a>4){a=0;}
 }
 lcd.setCursor(0,3);
 lcd.print(F("                OK"));
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

void soundChangePlayer(){
  for (int cnt = 0; cnt < 5; cnt++) {
  tone(Buzzer,736,125);
  delay(125);
  noTone(Buzzer);
  }
}

void soundReadyToShot(){
  tone(Buzzer,1000,100);
  delay(100);
  noTone(Buzzer);
}





void afficherMoniteurSerie(){
  Serial.println("Status boutonG" + String(statusBoutonG) +" Status boutonD" + String(statusBoutonD) + " Status cible1 " + String(statusCible1) + " Status cible2 " + String(statusCible2) + " Status cible3 " + String(statusCible3));
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
    AcquisitionCapteurs(); 
      if ( statusBoutonG==0 &&  statusBoutonD==0){
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
  }
}

void UsbPCGameControler(){
  lcd.clear();
  lcd.setCursor(0,0);
  lcd.print(F("USB PC CONTOLLER"));
  lcd.setCursor(0,1);
  lcd.print(F("CONNECTED"));
while (true){

    if(digitalRead(cible1)) {
       Keyboard.press('e');  
      
    } else {
    Keyboard.release('e');
    }
    
    if(digitalRead(cible2)) {
        Keyboard.press('r');
    } else {
        Keyboard.release('r'); 
    }
    if(digitalRead(cible3)) {
        Keyboard.press('t');
    } else {
        Keyboard.release('t');
    }
}
}
  
