

origineBaseX = 0;
origineBaseY = 0;
origineBaseZ = 0;
hauteurFacade = 190;
largeurFacade = 140;
epaiseurFacade = 4;
epaiseurCoteBas = 2;
epaisseurCotes = 4;
origineArduinoX = origineBaseX+10;
origineArduinoY = origineBaseY+epaiseurCoteBas+6;
origineEcranX = 21;
origineEcranY = hauteurFacade-70;
origineEcranZ = 0;
hauteurFixationEcran = epaiseurFacade+5;
hauteurFixationArduino = epaiseurFacade+8;
hauteurBoutons=origineEcranY-22;
hauteurCibles=hauteurFacade/4;
rayonBoutons = 6.1;
rayonCibles = 8;

translate([origineBaseX,origineBaseY,origineBaseZ]){
union(){
difference(){
cube(size=[largeurFacade, hauteurFacade, epaiseurFacade]); //cube facade
translate([origineEcranX,origineEcranY,origineEcranZ]){
cube(size=[98.3, 42.3, epaiseurFacade]);} // trou écran
translate([140/3,hauteurBoutons,origineEcranZ]){
cylinder(h=epaiseurFacade, r=rayonBoutons, $fn=200); //bouton1
}
translate([2*140/3,hauteurBoutons,origineEcranZ]){
cylinder(h=epaiseurFacade, r=rayonBoutons, $fn=200); //bouton2
}

translate([largeurFacade/4,hauteurCibles,0]){
cylinder(h=hauteurFixationEcran, r=rayonCibles, $fn=200); //cible1
}
translate([largeurFacade/2,hauteurCibles,0]){
cylinder(h=hauteurFixationEcran, r=rayonCibles, $fn=200); //cible2
}

translate([largeurFacade*3/4,hauteurCibles,0]){
cylinder(h=hauteurFixationEcran, r=rayonCibles, $fn=200); //cible3
}


}

translate([origineEcranX+2.5,origineEcranY-7.5,0]){//support écran inférieur gauche
difference(){    
cylinder(h=hauteurFixationEcran, r=3, $fn=200);
cylinder(h=hauteurFixationEcran, r=1.5, $fn=200);
}
}

translate([origineEcranX+95.5,origineEcranY-7.5,0]){//support écran inférieur droit
difference(){    
cylinder(h=hauteurFixationEcran, r=3, $fn=200);
cylinder(h=hauteurFixationEcran, r=1.5, $fn=200);
}
}

translate([origineEcranX+2.5,origineEcranY+47.5,0]){//support écran supérieur gauche
difference(){    
cylinder(h=hauteurFixationEcran, r=3, $fn=200);
cylinder(h=hauteurFixationEcran, r=1.5, $fn=200);
}
}

translate([origineEcranX+95.5,origineEcranY+47.5,0]){//support écran supérieur droit
difference(){    
cylinder(h=hauteurFixationEcran, r=3, $fn=200);
cylinder(h=hauteurFixationEcran, r=1.5, $fn=200);
}
}

//arrière écran
translate([origineEcranX,origineEcranY-6,0]){//barre basse
difference(){    
cube(size=[98.3, 3, hauteurFixationEcran]);
}
}

translate([origineEcranX,origineEcranY+42.8,0]){//barre basse
difference(){    
cube(size=[98.3, 3, hauteurFixationEcran]);
}
}


translate([largeurFacade/4,hauteurCibles,0]){//cylindre arrière cible 1
difference(){    
cylinder(h=hauteurFixationEcran, r=rayonCibles+2, $fn=200);
cylinder(h=hauteurFixationEcran, r=rayonCibles, $fn=200);
}
}

translate([largeurFacade/2,hauteurCibles,0]){//cylindre arrière cible 2
difference(){    
cylinder(h=hauteurFixationEcran, r=rayonCibles+2, $fn=200);
cylinder(h=hauteurFixationEcran, r=rayonCibles, $fn=200);
}
}

translate([largeurFacade*3/4,hauteurCibles,0]){//cylindre arrière cible 3
difference(){    
cylinder(h=hauteurFixationEcran, r=rayonCibles+2, $fn=200);
cylinder(h=hauteurFixationEcran, r=rayonCibles, $fn=200);
}
}
//supports arduino
translate([origineArduinoX+3.6,origineArduinoY+17.3,0]){//support inférieur gauche
difference(){    
cylinder(h=hauteurFixationArduino, r=3, $fn=200);
cylinder(h=hauteurFixationArduino, r=1.5, $fn=200);
}
}

translate([origineArduinoX+51.8,origineArduinoY+16,0]){//support inférieur droit
difference(){    
cylinder(h=hauteurFixationArduino, r=3, $fn=200);
cylinder(h=hauteurFixationArduino, r=1.5, $fn=200);
}
}

translate([origineArduinoX+18.8,origineArduinoY+68.1,0]){//support supérieur gauche
difference(){    
cylinder(h=hauteurFixationArduino, r=3, $fn=200);
cylinder(h=hauteurFixationArduino, r=1.5, $fn=200);
}
}


translate([origineArduinoX+46.7,origineArduinoY+68.1,0]){//support supérieur droit
difference(){    
cylinder(h=hauteurFixationArduino, r=3, $fn=200);
cylinder(h=hauteurFixationArduino, r=1.5, $fn=200);
}
}

//cotés boitier
difference(){
translate([origineBaseX,origineBaseY,origineBaseZ]){

cube(size=[largeurFacade, 2, epaiseurFacade+50]); //cube
}


translate([origineArduinoX+9,origineArduinoY-epaiseurCoteBas-6,hauteurFixationArduino+2]){
cube(size=[15, 2, hauteurFixationArduino+10]); //cube
}
translate([origineArduinoX+40,origineArduinoY-epaiseurCoteBas-6,hauteurFixationArduino+2]){
cube(size=[10, 2, hauteurFixationArduino+11]); //cube
}

translate([origineArduinoX+80,origineArduinoY-epaiseurCoteBas-6,hauteurFixationArduino+2]){
cube(size=[19.7, 2, 15]); //cube
}
}


//coté haut
translate([origineBaseX,origineBaseY+hauteurFacade-epaisseurCotes,origineBaseZ]){
    cube(size=[largeurFacade, epaisseurCotes,epaiseurFacade+50]);
}

translate([origineBaseX,origineBaseY-epaisseurCotes+hauteurFacade-epaisseurCotes,origineBaseZ]){
    cube(size=[largeurFacade, epaisseurCotes,epaiseurFacade+48]);
}


//fin coté haut
//coté gauche
translate([origineBaseX,origineBaseY,origineBaseZ]){

cube(size=[epaisseurCotes, hauteurFacade,epaiseurFacade+50]); //cube
}

translate([origineBaseX+epaisseurCotes,origineBaseY,origineBaseZ]){

cube(size=[epaisseurCotes, hauteurFacade,epaiseurFacade+48]); //cube
}


//fin coté gauche

//coté droit
translate([origineBaseX+largeurFacade-epaisseurCotes,origineBaseY,origineBaseZ]){

cube(size=[epaisseurCotes, hauteurFacade,epaiseurFacade+50]); //cube
}

translate([origineBaseX+largeurFacade-epaisseurCotes-4,origineBaseY,origineBaseZ]){

cube(size=[epaisseurCotes, hauteurFacade,epaiseurFacade+48]); //cube
}
//fin coté droit

translate([largeurFacade/4,hauteurCibles,0]){
cylinder(h=0.2, r=rayonCibles, $fn=200); //cible1
}
translate([largeurFacade/2,hauteurCibles,0]){
cylinder(h=0.2, r=rayonCibles, $fn=200); //cible2
}

translate([largeurFacade*3/4,hauteurCibles,0]){
cylinder(h=0.2, r=rayonCibles, $fn=200); //cible3
}

translate([origineBaseX+10,origineBaseY+4,0]){//support écran inférieur gauche
difference(){    
cylinder(h=48+epaiseurFacade, r=3, $fn=200);
cylinder(h=50+epaiseurFacade, r=1.5, $fn=200);
}
}

translate([largeurFacade-10,origineBaseY+4,0]){//support écran inférieur gauche
difference(){    
cylinder(h=48+epaiseurFacade, r=3, $fn=200);
cylinder(h=50+epaiseurFacade, r=1.5, $fn=200);
}
}

translate([origineBaseX+10,hauteurFacade-10,0]){//support écran inférieur gauche
difference(){    
cylinder(h=48+epaiseurFacade, r=3, $fn=200);
cylinder(h=50+epaiseurFacade, r=1.5, $fn=200);
}
}

translate([largeurFacade-10,hauteurFacade-10]){//support écran inférieur gauche
difference(){    
cylinder(h=48+epaiseurFacade, r=3, $fn=200);
cylinder(h=50+epaiseurFacade, r=1.5, $fn=200);
}
}

translate([origineBaseX+10,hauteurFacade/2,0]){//support écran inférieur gauche
difference(){    
cylinder(h=48+epaiseurFacade, r=3, $fn=200);
cylinder(h=50+epaiseurFacade, r=1.5, $fn=200);
}
}

translate([largeurFacade-10,hauteurFacade/2]){//support écran inférieur gauche
difference(){    
cylinder(h=48+epaiseurFacade, r=3, $fn=200);
cylinder(h=50+epaiseurFacade, r=1.5, $fn=200);
}
}



}
}
    
