origineBaseX = 0;
origineBaseY = 0;
origineBaseZ = 0;
positonHPX=100;
positonHPY=40;
hauteurFacade = 190;
largeurFacade = 140;
epaisseurFacade = 2;
epaisseurCoteBas = 2;
epaisseurCotes = 4;
origineArduinoX = origineBaseX+10;
origineArduinoY = origineBaseY+epaisseurCoteBas+6;
origineEcranX = 21;
origineEcranY = hauteurFacade-70;
origineEcranZ = 0;
hauteurFixationEcran = epaisseurFacade+5;
hauteurFixationArduino = epaisseurFacade+8;
hauteurBoutons=origineEcranY-22;
hauteurCibles=hauteurFacade/4;
rayonBoutons = 6.1;
rayonCibles = 8;

translate([origineBaseX,origineBaseY,origineBaseZ]){
union(){

difference(){
cube(size=[largeurFacade, hauteurFacade, epaisseurFacade]); //facade
//coté haut
translate([origineBaseX,origineBaseY+hauteurFacade-epaisseurCotes-0.1,origineBaseZ]){
   cube(size=[largeurFacade, epaisseurCotes+0.1,epaisseurFacade+50]);
}
//coté gauche
translate([origineBaseX,origineBaseY,origineBaseZ]){

cube(size=[epaisseurCotes+0.1, hauteurFacade,epaisseurFacade]); //cube
}
//coté droit
translate([origineBaseX+largeurFacade-epaisseurCotes-0.1,origineBaseY,origineBaseZ]){

cube(size=[epaisseurCotes, hauteurFacade,epaisseurFacade+0.1]); //cube
}
//coté bas
translate([origineBaseX,origineBaseY,origineBaseZ]){

    cube(size=[largeurFacade, epaisseurCoteBas+0.1,epaisseurFacade]);

}

translate([largeurFacade-10,hauteurFacade/2]){//support écran inférieur gauche

cylinder(h=epaisseurFacade, r=1.5, $fn=200);
}


translate([origineBaseX+10,origineBaseY+4,0]){//support écran inférieur gauche

cylinder(h=3, r=1.5, $fn=200);
}


translate([largeurFacade-10,origineBaseY+4,0]){//support écran inférieur gauche

cylinder(h=3, r=1.5, $fn=200);

}

translate([origineBaseX+10,hauteurFacade-10,0]){//support écran inférieur gauche

cylinder(h=3, r=1.5, $fn=200);
}


translate([largeurFacade-10,hauteurFacade-10]){//support écran inférieur gauche

cylinder(h=3, r=1.5, $fn=200);
}


translate([origineBaseX+10,hauteurFacade/2,0]){//support écran inférieur gauche
 cylinder(h=3, r=1.5, $fn=200);
}



translate([largeurFacade/2,hauteurFacade/2,0]){//fixation arriere    

cylinder(h=3, r=1.5, $fn=200);
}

translate([largeurFacade/2,hauteurFacade*3/4,0]){//fixation arriere    

cylinder(h=3, r=1.5, $fn=200);
}

translate([largeurFacade/2,hauteurFacade*1/4,0]){//fixation arriere    

cylinder(h=3, r=1.5, $fn=200);
}


translate([positonHPX+12,positonHPY+32,0]){//fixation arriere    

cylinder(h=3, r=3, $fn=200);
}

translate([positonHPX+12,positonHPY+80,0]){//fixation arriere    

cylinder(h=3, r=6.1, $fn=200);
}


}

translate([positonHPX,positonHPY,0]){//support écran inférieur gauche
difference(){    
cylinder(h=hauteurFixationEcran+epaisseurFacade, r=3, $fn=200);
cylinder(h=hauteurFixationEcran+epaisseurFacade, r=1.5, $fn=200);
}
}
translate([positonHPX,positonHPY+63,0]){//support écran inférieur gauche
difference(){    
cylinder(h=hauteurFixationEcran+epaisseurFacade, r=3, $fn=200);
cylinder(h=hauteurFixationEcran+epaisseurFacade, r=1.5, $fn=200);
}
}

translate([positonHPX+24,positonHPY+63,0]){//support écran inférieur gauche
difference(){    
cylinder(h=hauteurFixationEcran+epaisseurFacade, r=3, $fn=200);
cylinder(h=hauteurFixationEcran+epaisseurFacade, r=1.5, $fn=200);
}
}


translate([positonHPX+24,positonHPY,0]){//support écran inférieur gauche
difference(){    
cylinder(h=hauteurFixationEcran+epaisseurFacade, r=3, $fn=200);
cylinder(h=hauteurFixationEcran+epaisseurFacade, r=1.5, $fn=200);
}
}


}
}

/*

//cube(size=[largeurFacade, hauteurFacade, epaisseurFacade]); 


//cotés boitier
//difference(){
translate([origineBaseX,origineBaseY,origineBaseZ]){
cube(size=[largeurFacade, 2, epaisseurFacade]); //cube
}
translate([origineArduinoX+9,origineArduinoY-epaisseurCoteBas-6,hauteurFixationArduino+2]){
cube(size=[15, 2, hauteurFixationArduino+10]); //cube
}
translate([origineArduinoX+40,origineArduinoY-epaisseurCoteBas-6,hauteurFixationArduino+2]){
cube(size=[10, 2, hauteurFixationArduino+11]); //cube
}

translate([origineArduinoX+80,origineArduinoY-epaisseurCoteBas-6,hauteurFixationArduino+2]){
cube(size=[19.7, 2, 15]); //cube
}
//}


//coté haut


translate([origineBaseX,origineBaseY-epaisseurCotes+hauteurFacade-epaisseurCotes,origineBaseZ]){
    cube(size=[largeurFacade-epaisseurCotes, epaisseurCotes,epaisseurFacade+2]);
}


//fin coté haut
//coté gauche


translate([origineBaseX+epaisseurCotes,origineBaseY,origineBaseZ]){

cube(size=[epaisseurCotes, hauteurFacade-epaisseurCotes,epaisseurFacade+2]); //cube
}


//fin coté gauche



translate([origineBaseX+largeurFacade-epaisseurCotes-4,origineBaseY,origineBaseZ]){

cube(size=[epaisseurCotes, hauteurFacade-epaisseurCotes,epaisseurFacade+2]); //cube
}
//fin coté droit



translate([origineBaseX+10,origineBaseY+4,0]){//support écran inférieur gauche
difference(){    
cylinder(h=2, r=3, $fn=200);
cylinder(h=3, r=1.5, $fn=200);
}
}

translate([largeurFacade-10,origineBaseY+4,0]){//support écran inférieur gauche
difference(){    
cylinder(h=2, r=3, $fn=200);
cylinder(h=3, r=1.5, $fn=200);
}
}

translate([origineBaseX+10,hauteurFacade-10,0]){//support écran inférieur gauche
difference(){    
cylinder(h=2, r=3, $fn=200);
cylinder(h=3, r=1.5, $fn=200);
}
}

translate([largeurFacade-10,hauteurFacade-10]){//support écran inférieur gauche
difference(){    
cylinder(h=2, r=3, $fn=200);
cylinder(h=3, r=1.5, $fn=200);
}
}

translate([origineBaseX+10,hauteurFacade/2,0]){//support écran inférieur gauche
difference(){    
cylinder(h=2, r=3, $fn=200);
cylinder(h=3, r=1.5, $fn=200);
}
}

translate([largeurFacade-10,hauteurFacade/2]){//support écran inférieur gauche
difference(){    
cylinder(h=epaisseurFacade, r=3, $fn=200);
cylinder(h=epaisseurFacade, r=1.5, $fn=200);
}
}



}}
}
 */   
