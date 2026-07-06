package com.jb.petanquetool;

import android.os.Build;

import android.os.Bundle;
import android.os.Message;
import android.util.DisplayMetrics;
import android.util.Log;
import android.util.TypedValue;
import android.os.Handler;
import android.os.CountDownTimer;
import android.widget.*;
import android.widget.TableRow.LayoutParams;
import android.annotation.TargetApi;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.res.Configuration;
import android.content.res.Resources;
import android.graphics.Color;
import android.media.AudioAttributes;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.media.MediaPlayer.OnCompletionListener;
//import android.content.DialogInterface.OnClickListener;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.LayoutInflater;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.view.animation.Animation;
import android.view.animation.TranslateAnimation;
import android.media.SoundPool;
import android.media.SoundPool.OnLoadCompleteListener;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import android.speech.RecognitionListener;
import android.speech.RecognizerIntent;
import android.speech.SpeechRecognizer;

import static com.nineoldandroids.view.ViewPropertyAnimator.animate;


public class ActivityPetanque extends Activity implements OnClickListener {

		TextView score_personne;//score de la personne
		Resources res;
		boolean victoire;
		boolean finpartie;
		boolean masteron;
		public Handler handler;
		MediaPlayer mediaPlayer;
		Button scoreJ1,scoreJ2, scoreJ3,scoreJ4, scoreJ5, scoreJ6, scoreJ7, scoreJ8;
		Button btn_oui,btn_non,btn_rejouer,btn_quitter;
		LinearLayout linearLayoutNbJ,mainLayout;
		RelativeLayout fondLayout;
		TextView NBTOURSTEXT,NUMJTOURTEXT,NBCIBLETEXT,TEXTtoucher;
		ImageView plateau;
		View optionRejouer;
		LayoutInflater inflater;
		int nbjoueurs=1;
		//numéro de tour des joueurs
		int nbTours;
		//tableau des joueurs ayant touché consécutivement une boule
		int [] bouleTouche;
		//tableau des scores des joueurs
		int [] TabScores;
		//tableau des cibles des joueurs
		float [] TabTauxReussite;
		int [] TabCibles;
		//tableau du nombre de tir effectué par chaque joueur
		int [] TabNbTirsEffectues;
		//tableau des bonus atteint par les joueurs
		int [] TabBonusAcquis;
		//tableau des points bonus actuel des joueurs
		int [] TabPointsBonus;
		//tableau du nombre de cibles atteintes par joueur
		int [] TabCiblesatteintes;
		//tableau des masters
		boolean [] TabMasters;
		//nombre de boules totales
		int nbboulesTot;
		//numéro du joueur qui va joueur
		int joueurencours;
		//numéro de la boule a lancé par tour (1,2 ou 3)
		int NBoule;
		SoundPool soundPool;
		ImageView fleche;
		TranslateAnimation anim;
		//taille de l'écran en pixels
		int height=0;
		int width=0;
		float pourcentX=0;
		float pourcentY=0;
		Intent intent;
		
	    @Override
	    public void onCreate(Bundle savedInstanceState) {
	        super.onCreate(savedInstanceState);
	        setContentView(R.layout.activity_petanque);
	        linearLayoutNbJ= (LinearLayout)this.findViewById(R.id.linearLayoutNbJ);
	        inflater = (LayoutInflater)getSystemService(Context.LAYOUT_INFLATER_SERVICE);
	        mainLayout= (LinearLayout)this.findViewById(R.id.mainLayout);
	        fondLayout= (RelativeLayout)this.findViewById(R.id.fondLayout);
	        fleche=(ImageView)this.findViewById(R.id.fleche);
			Bundle extras = getIntent().getExtras();
			nbjoueurs = extras.getInt("nbjoueurs");
			Log.i("nbjoueurs",String.valueOf(nbjoueurs));
			res=getResources();
			//plateau=(ImageView)this.findViewById(R.id.plateau);
			NBTOURSTEXT=(TextView)this.findViewById(R.id.NUMBTOURJ);
			NUMJTOURTEXT=(TextView)this.findViewById(R.id.NBTOURJ);
			NBCIBLETEXT=(TextView)this.findViewById(R.id.NBCIBLEJ);
			TEXTtoucher=(TextView)this.findViewById(R.id.toucher);
			scoreJ1= (Button)this.findViewById(R.id.scoreJ1);
			scoreJ2= (Button)this.findViewById(R.id.scoreJ2);
			scoreJ3= (Button)this.findViewById(R.id.scoreJ3);
			scoreJ4= (Button)this.findViewById(R.id.scoreJ4);
			scoreJ5= (Button)this.findViewById(R.id.scoreJ5);
			scoreJ6= (Button)this.findViewById(R.id.scoreJ6);
			scoreJ7= (Button)this.findViewById(R.id.scoreJ7);
			scoreJ8= (Button)this.findViewById(R.id.scoreJ8);
			btn_oui= (Button)this.findViewById(R.id.btn_oui);
			btn_oui.setOnClickListener(this);
			btn_non= (Button)this.findViewById(R.id.btn_non);
			btn_non.setOnClickListener(this);
			//initialisation des tableaux
			bouleTouche = new int [nbjoueurs];
			TabScores = new int [nbjoueurs];
			TabPointsBonus= new int [nbjoueurs];
			TabBonusAcquis= new int [nbjoueurs];
			TabNbTirsEffectues= new int [nbjoueurs];
			TabCibles= new int [nbjoueurs];
			TabMasters= new boolean [nbjoueurs];
			TabCiblesatteintes= new int [nbjoueurs];
			TabTauxReussite= new float [nbjoueurs];
			DisplayMetrics displaymetrics = new DisplayMetrics(); 
	        getWindowManager().getDefaultDisplay().getMetrics(displaymetrics); 
	        height = displaymetrics.heightPixels; 
	        width = displaymetrics.widthPixels;
			init();
	        
	    }
	    
	    private void goAnimFleche(int cible){
	    	
	    	//determination des coordonnées X et Y en fonction de la taille de l'écran 
	    	//taille image (480,320)
	    	pourcentX=(float)(height/480);
	    	pourcentY=(float)(width/320);
	    	Log.i("width ", "="+width);
	    	Log.i("height ", "="+height);
	    	Log.i("pourcentX ", "="+pourcentX);
	    	Log.i("pourcentY ", "="+pourcentY);
	    	//position en X et en Y de la fleche
	    	int posY=0;
	    	int posXEnd=0;
	    	int posYEnd=0;
	    	//Log.i("lance l'anim","anim lancer");
	    	switch(cible){
	    		case 0:
	    			posY=120;
	    			posXEnd=145;
	    			posYEnd=135;
	    		break;
	    		case 1:
	    			posY=95;
	    			posXEnd=63;
	    			posYEnd=110;
		    	break;
	    		case 2:
	    			posY=95;
	    			posXEnd=223;
	    			posYEnd=110;
		    	break;
	    		case 3:
	    			posY=60;
	    			posXEnd=72;
	    			posYEnd=75;
		    	break;
	    		case 4:
	    			posY=60;
	    			posXEnd=217;
	    			posYEnd=75;
		    	break;
	    		case 5:
	    			posY=50;
	    			posXEnd=143;
	    			posYEnd=65;
		    	break;
	    		case 6:
	    			posY=95;
	    			posXEnd=144;
	    			posYEnd=110;
		    	break;
	    	}
	    	anim=new TranslateAnimation(posXEnd*pourcentX,posXEnd*pourcentX,posY*pourcentY,posYEnd*pourcentY);
    		anim.setDuration(1500);
    		anim.setFillAfter(true);
    		anim.setRepeatCount(Animation.INFINITE);
    		fleche.startAnimation(anim);
	    	//fleche.animate().translationX(posXEnd).translationY(posYEnd).setDuration(500);
	    	
	    }
	    
	    private void init() {
	    	if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
				createNewSoundPool();
			}else{
				createOldSoundPool();
			}
			nbboulesTot=0;
			joueurencours=1;
			NBoule=1;
	    	nbTours=0;
	    	victoire=false;
	    	finpartie=false;
	    	masteron=false;
	    	nbboulesTot=nbjoueurs*30;
			int tailleTab=TabScores.length;
			for(int i=0; i<tailleTab;i++){
				TabScores[i]=0;
				TabBonusAcquis[i]=0;
				TabPointsBonus[i]=0;
				TabNbTirsEffectues[i]=0;
				TabCibles[i]=0;
				TabMasters[i]=false;
				TabCiblesatteintes[i]=0;
				TabTauxReussite[i]=0;
			}
			//affichage des scores des joueurs
			scoreJ1.setText("J1" + "\n" + "0");
			scoreJ1.setEnabled(false);
			affichageScoreText(1);
			scoreJ2.setText("J2" + "\n" + "0");
			scoreJ2.setEnabled(false);
			scoreJ3.setText("J3" + "\n" + "0");
			scoreJ3.setEnabled(false);
			scoreJ4.setText("J4" + "\n" + "0");
			scoreJ4.setEnabled(false);
			scoreJ5.setText("J5" + "\n" + "0");
			scoreJ5.setEnabled(false);
			scoreJ6.setText("J6" + "\n" + "0");
			scoreJ6.setEnabled(false);
			scoreJ7.setText("J7" + "\n" + "0");
			scoreJ7.setEnabled(false);
			scoreJ8.setText("J8" + "\n" + "0");
			scoreJ8.setEnabled(false);
			//rendre invisible les joueurs qui ne participe pas
			displaynbJScore();
			NBTOURSTEXT.setText("1");
			NUMJTOURTEXT.setText("J1");
			NBTOURSTEXT.setText("1");
			NBCIBLETEXT.setText("1");
			//NBBALLTEXT.setText("1");
			TEXTtoucher.setText(res.getString(R.string.toucher));
			goAnimFleche(0);
	    }
	    
	    private void obtenirReplay(){
	    	setActivityBackground(4);
	    	fleche.setVisibility(View.INVISIBLE);
	    	optionRejouer = inflater.inflate(R.layout.menu_rejouer, mainLayout, false);
	    	mainLayout.addView(optionRejouer);
	    	mainLayout.removeView(fondLayout);
	    	TableLayout tl = (TableLayout) findViewById(R.id.tabres);
            TableRow tr;
            float scoretot=0f;
            LayoutParams layoutParams = new LayoutParams(LayoutParams.FILL_PARENT,
                    LayoutParams.FILL_PARENT);
            layoutParams.setMargins(1, 1, 1, 1);
            layoutParams.weight = 1.0f;
            tr = new TableRow(ActivityPetanque.this);
            tr.setLayoutParams(new LayoutParams(LayoutParams.FILL_PARENT,
                            LayoutParams.WRAP_CONTENT));
            tr.addView(generateTextView(getString(R.string.joueur), layoutParams,0));
            tr.addView(generateTextView(getString(R.string.score), layoutParams,0));
            tr.addView(generateTextView(getString(R.string.reussite), layoutParams,0));
            tr.addView(generateTextView(getString(R.string.total), layoutParams,0));
            tl.addView(tr, layoutParams);
            for (int i = 0; i < nbjoueurs; i++) {
                tr = new TableRow(ActivityPetanque.this);
                tr.setLayoutParams(new LayoutParams(LayoutParams.FILL_PARENT,
                        LayoutParams.WRAP_CONTENT));
                //affiche le numéro du joueur
                tr.addView(generateTextView(String.valueOf(i+1), layoutParams,1));
                //affiche le score du joueur
                tr.addView(generateTextView(String.valueOf(TabScores[i]), layoutParams,1));
                //affiche le pourcentage de réussite du joueur
                tr.addView(generateTextView(String.valueOf(TabTauxReussite[i]), layoutParams,1));
                //affcihe le score total du joueur
                scoretot=TabScores[i]+TabTauxReussite[i];
                tr.addView(generateTextView(String.valueOf(scoretot), layoutParams,1));
                //affiche la ligne complète
                tl.addView(tr, layoutParams);
            }
	    	btn_rejouer= (Button)optionRejouer.findViewById(R.id.rejouer);
	    	btn_rejouer.setOnClickListener(new View.OnClickListener() {
	            @Override
	            public void onClick(View v) {
	            	mainLayout.removeView(optionRejouer);
	            	mainLayout.addView(fondLayout);
	            	//unbindDrawables(optionLayout);
	            	btn_rejouer.setEnabled(false);
	            	btn_quitter.setEnabled(false);
	            	init();
	            	fleche.setVisibility(View.VISIBLE);
	           	 	btn_oui.setEnabled(true);
					btn_non.setEnabled(true);
					setActivityBackground(1);
	            }
	        });
	        btn_quitter= (Button)optionRejouer.findViewById(R.id.quitter);
	        btn_quitter.setOnClickListener(new View.OnClickListener() {
	            @Override
	            public void onClick(View v) {
	            	mainLayout.removeView(optionRejouer);
	            	finish();
	            	btn_rejouer.setEnabled(false);
	            	btn_quitter.setEnabled(false);
	            }
	        });
	        
	    }
	    
	    public TextView generateTextView(String string, LayoutParams ly, int cible) {
	        TextView result = new TextView(this);
	        //result.setBackgroundColor(Color.WHITE);
	        result.setBackgroundColor(Color.argb(180, 255, 255, 255));
	        result.setTextColor(Color.argb(255, 12, 76, 192));
	        result.setGravity(Gravity.CENTER);
	        result.setPadding(1, 1, 1, 1);
	        result.setText(string);
	        if(cible==0){
	        	result.setTextSize(TypedValue.COMPLEX_UNIT_SP,17);
	        }else{
	        	result.setTextSize(TypedValue.COMPLEX_UNIT_SP,15);
	        }
	        result.setVisibility(View.VISIBLE);
	        result.setLayoutParams(ly);
	        return result;
	   }
	    
	    public int pxToDp(int px) {
	        DisplayMetrics displayMetrics = this.getResources().getDisplayMetrics();
	        int dp = Math.round(px / (displayMetrics.xdpi / DisplayMetrics.DENSITY_DEFAULT));
	        return dp;
	    }
	    
	    public int dpToPx(int dp) {
	        DisplayMetrics displayMetrics = this.getResources().getDisplayMetrics();
	        int px = Math.round(dp * (displayMetrics.xdpi / DisplayMetrics.DENSITY_DEFAULT));       
	        return px;
	    }
	    
	    private void affichageScoreText(int indice){
	    	switch(indice){
	    	case 1:
	    		scoreJ1.setBackgroundResource(R.drawable.btn_cyan);
	    		scoreJ2.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ3.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ4.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ5.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ6.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ7.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ8.setBackgroundResource(R.drawable.btn_red);
	    	break;
	    	case 2:
	    		scoreJ1.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ2.setBackgroundResource(R.drawable.btn_cyan);
	    		scoreJ3.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ4.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ5.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ6.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ7.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ8.setBackgroundResource(R.drawable.btn_red);
	    	break;
	    	case 3:
	    		scoreJ1.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ2.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ3.setBackgroundResource(R.drawable.btn_cyan);
	    		scoreJ4.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ5.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ6.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ7.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ8.setBackgroundResource(R.drawable.btn_red);
	    	break;
	    	case 4:
	    		scoreJ1.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ2.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ3.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ4.setBackgroundResource(R.drawable.btn_cyan);
	    		scoreJ5.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ6.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ7.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ8.setBackgroundResource(R.drawable.btn_red);
	    	break;
	    	case 5:
	    		scoreJ1.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ2.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ3.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ4.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ5.setBackgroundResource(R.drawable.btn_cyan);
	    		scoreJ6.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ7.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ8.setBackgroundResource(R.drawable.btn_red);
	    	break;
	    	case 6:
	    		scoreJ1.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ2.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ3.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ4.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ5.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ6.setBackgroundResource(R.drawable.btn_cyan);
	    		scoreJ7.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ8.setBackgroundResource(R.drawable.btn_red);
	    	break;
	    	case 7:
	    		scoreJ1.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ2.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ3.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ4.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ5.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ6.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ7.setBackgroundResource(R.drawable.btn_cyan);
	    		scoreJ8.setBackgroundResource(R.drawable.btn_red);
	    	break;
	    	case 8:
	    		scoreJ1.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ2.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ3.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ4.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ5.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ6.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ7.setBackgroundResource(R.drawable.btn_red);
	    		scoreJ8.setBackgroundResource(R.drawable.btn_cyan);
	    	break;
	    	
	    	}
	    }
	    
	    private void displaynbJScore(){
	    	if(nbjoueurs<8){
				switch(nbjoueurs){
				case 1:
					 scoreJ2.setVisibility(View.INVISIBLE);
					 scoreJ3.setVisibility(View.INVISIBLE);
					 scoreJ4.setVisibility(View.INVISIBLE);
					 linearLayoutNbJ.setVisibility(View.INVISIBLE);	
				break;
				case 2:
					 scoreJ3.setVisibility(View.INVISIBLE);
					 scoreJ4.setVisibility(View.INVISIBLE);
					 linearLayoutNbJ.setVisibility(View.INVISIBLE);	
				break;
				case 3:
					 scoreJ4.setVisibility(View.INVISIBLE);
					 linearLayoutNbJ.setVisibility(View.INVISIBLE);	
				break;
				case 4:
					linearLayoutNbJ.setVisibility(View.INVISIBLE);	
				break;
				case 5:
					 scoreJ6.setVisibility(View.INVISIBLE);
					 scoreJ7.setVisibility(View.INVISIBLE);
					 scoreJ8.setVisibility(View.INVISIBLE);	
				 break;
				 case 6:
					 scoreJ7.setVisibility(View.INVISIBLE);
					 scoreJ8.setVisibility(View.INVISIBLE);	
				 break;	
				 case 7:
					 scoreJ8.setVisibility(View.INVISIBLE);	
				 break;		
				}
			}
	    }
	    
	    @Override
	    public boolean onKeyDown(int keyCode, KeyEvent event) 
	    {          
	        if (keyCode == KeyEvent.KEYCODE_BACK) 
	        {   
	           affichageAlertDialog();
	           return true;
	        }
	        else
	        {
	           return super.onKeyDown(keyCode, event);
	        }
	           
	     }

		@Override
		public void onClick(View v) {
			// TODO Auto-generated method stub
			switch(v.getId())
	        {
	            case R.id.btn_oui:
	            		BouleToucher();
	            break;
	            case R.id.btn_non:
	            		BouleNonToucher();
		        break;
	        
	        }
			 
		}
		
		private void affichageAlertDialog(){
			AlertDialog.Builder builder = new AlertDialog.Builder(this);
	           builder.setMessage(R.string.dialogretour)
	              .setCancelable(false)
	              .setPositiveButton(R.string.oui, new DialogInterface.OnClickListener() {
	                 public void onClick(DialogInterface dialog, int id) {	
	                	 finish();
	                 }
	              })
	              .setNegativeButton(R.string.non, new DialogInterface.OnClickListener() {
	                 public void onClick(DialogInterface dialog, int id) {
	                 }
	              });
	            AlertDialog alert = builder.create();
	            alert.show();
		}
		
		private void BouleNonToucher(){
			launchSound(R.raw.pas_toucher);
			TabNbTirsEffectues[joueurencours-1]= TabNbTirsEffectues[joueurencours-1] + 1;
			TabPointsBonus[joueurencours-1]=0;
			TabMasters[joueurencours-1] = false;
			actualiseMasterON();
			actualiseflagfinpartie();
			calculTauxReussite();
			/*Log.i("BouleNonToucher","BouleNonToucher");
			Log.i("joueurencours", "="+joueurencours);
			Log.i("finpartie", "="+finpartie);
			Log.i("NBoule", "="+NBoule);
			Log.i("masteron", "="+masteron);
			Log.v("valeur", "="+TabNbTirsEffectues[joueurencours-1]);*/
			//teste la vrai fin de la partie
			if ((joueurencours == nbjoueurs) && (NBoule == 3)) {
				if((finpartie == true) && (masteron == false)){
					//affichage du menu de fin
					obtenirReplay();
				}else{
					Log.i("appel nextTurn","BouleNonToucher");
					nextTurn();
				}
			}else{
				//nextTarget();
				if (NBoule > 2) {
					nextPlayer();
				}else{
					nextBall();
				}
			}
			affichageScore(joueurencours-1);
			affichageScoreText(joueurencours);
			//affichagePlateau(TabCibles[joueurencours-1]);
			//NUMJTOURTEXT.setText(String.valueOf(nbTours+1));
 		    //NUMJTOURTEXT.setText("J"+joueurencours);
			afficher();
			
		}
		
		
		private void BouleToucher(){
			
			launchSound(R.raw.toucher);
			Log.i("bouleToucher","ok");
			Log.v("valeurjoueur","="+joueurencours);
			Log.v("valeur", "="+TabNbTirsEffectues[joueurencours-1]);
			TabNbTirsEffectues[joueurencours-1] = TabNbTirsEffectues[joueurencours-1] + 1;
			TabCiblesatteintes[joueurencours-1] =  TabCiblesatteintes[joueurencours-1] + 1;
			TabScores[joueurencours-1]=1 + TabPointsBonus[joueurencours-1] + TabScores[joueurencours-1];
			TabPointsBonus[joueurencours-1]=TabPointsBonus[joueurencours-1]+1;
			//TabBonusAcquis[joueurencours-1]=TabBonusAcquis[joueurencours-1]+TabPointsBonus[joueurencours-1];
			actualiseMasterON();
			actualiseflagfinpartie();
			calculTauxReussite();
			//teste la vrai fin de la partie
			if ((joueurencours == nbjoueurs) && (NBoule == 3)){
				if((finpartie == true) && (masteron == false)){
					obtenirReplay();
				}else{
					nextTarget();
					affichageScore(joueurencours-1);
					Log.i("appel de nextTurn","BouleToucher");
					nextTurn();
				}
			}else{
				nextTarget();
				if (NBoule > 2) {
						//Log.i("appel","nextPlayer()");
						affichageScore(joueurencours-1);
						nextPlayer();
				}else{
						//Log.i("appel","nextBall()");
						nextBall();
				}	
			}
			affichageScore(joueurencours-1);
			affichageScoreText(joueurencours);
			//affichagePlateau(TabCibles[joueurencours-1]);
			//NUMJTOURTEXT.setText(String.valueOf(nbTours+1));
 		    //NUMJTOURTEXT.setText("J"+joueurencours);
 		    afficher();
			
		}
		
		private void nextPlayer(){
			Log.i("joueur suivant","joueur"+nbjoueurs);
			if (joueurencours < nbjoueurs) {
				joueurencours++;
			}else{
				joueurencours = 1;
			}
			NBoule = 1;
			setActivityBackground(1);
			goAnimFleche(TabCibles[joueurencours-1]);
		}
		
		private void nextTarget(){
			if (TabCiblesatteintes[joueurencours-1] < 7) {
				TabCibles[joueurencours-1] = TabCibles[joueurencours-1]+1;
			}else{
				TabCibles[joueurencours-1] = (int) (Math.random() * 6);
			}
			goAnimFleche(TabCibles[joueurencours-1]);
		}
		
		private void nextTurn(){
			nbTours++;
			joueurencours=1;
			NBoule=1;
			Log.i("tour suivant","tour"+nbTours);
			setActivityBackground(1);
			goAnimFleche(TabCibles[0]);
		}
		
		private void nextBall(){
			if (NBoule < 3) { 
				NBoule++;
				setActivityBackground(NBoule);
			}
			Log.i("boule suivante","NBoule"+NBoule);
		}
		
		private void actualiseMasterON(){
			 masteron=false;
			 //Log.i("master","="+masteron);
			 if ((TabCiblesatteintes[joueurencours-1] > 6) && (TabNbTirsEffectues[joueurencours-1] < 10)) {
						TabMasters[joueurencours-1]=true;
						Log.i("TabMasters[joueurencours-1]","="+masteron);
			 }
			 for (int i = 0; i<nbjoueurs;i++){
				if (TabMasters[i]==true) {
					masteron=true;
					Log.i("TabMasters[i]","="+i+" "+masteron);
					break;
				}
			 }
		}
		
		private void actualiseflagfinpartie(){
			//finpartie=false;
			for (int i = 0; i<nbjoueurs;i++){
				  if (TabCiblesatteintes[i]>6) {
					  finpartie=true;
					  Log.i("fin partie","ok");
					  break;
				  }
			}
			if (nbTours > 8) {
				    finpartie=true;
			}		
			
		}
		
		private void calculTauxReussite(){
			float result = TabCiblesatteintes[joueurencours-1] * 100 /  TabNbTirsEffectues[joueurencours-1];
			TabTauxReussite[joueurencours-1]=round(result, 2);
		}
		
		private void afficher(){
			NBTOURSTEXT.setText(String.valueOf(nbTours+1));
			NUMJTOURTEXT.setText(String.valueOf(joueurencours));
			NBCIBLETEXT.setText(String.valueOf(TabCibles[joueurencours-1]+1));
			//NBBALLTEXT.setText(String.valueOf(NBoule));
		}
		
		private void trieResultat(){
			int indice=0;
			float max=TabScores[0];
			for(int i=1;i<nbjoueurs;i++){
				if(max<TabScores[i]){
					indice=i;
					max=TabScores[i];
				}
			}
			indice++;
			//Toast.makeText(this, "Meilleur joueur J"+indice, Toast.LENGTH_LONG).show();
			//Toast.makeText(this, "avec le score de "+max, Toast.LENGTH_LONG).show();
		}
		
		//calcul du score des joueurs et affichage
		private void affichageScore(int indice){
			switch(indice){
			case 0:
				scoreJ1.setText("J1" + "\n" + String.valueOf(TabScores[joueurencours-1]));
				break;
			case 1:
				scoreJ2.setText("J2" + "\n" + String.valueOf(TabScores[joueurencours-1]));
				break;
			case 2:
				scoreJ3.setText("J3" + "\n" + String.valueOf(TabScores[joueurencours-1]));
				break;
			case 3:
				scoreJ4.setText("J4" + "\n" + String.valueOf(TabScores[joueurencours-1]));
				break;
			case 4:
				scoreJ5.setText("J5" + "\n" + String.valueOf(TabScores[joueurencours-1]));
				break;
			case 5:
				scoreJ6.setText("J6" + "\n" + String.valueOf(TabScores[joueurencours-1]));
				break;
			case 6:
				scoreJ7.setText("J7" + "\n" + String.valueOf(TabScores[joueurencours-1]));
				break;
			case 7:
				scoreJ8.setText("J8" + "\n" + String.valueOf(TabScores[joueurencours-1]));
				break;
			}
			
		}
		
		public static float round(float d, int decimalPlace) {
	        BigDecimal bd = new BigDecimal(Float.toString(d));
	        bd = bd.setScale(decimalPlace, BigDecimal.ROUND_HALF_UP);
	        return bd.floatValue();
	    }
		
		public void setActivityBackground(int cible) {
			
		    switch(cible){
				case 1:
					fondLayout.setBackgroundResource(R.drawable.coup1);
				break;
				case 2:
					fondLayout.setBackgroundResource(R.drawable.coup2);
				break;
				case 3:
					fondLayout.setBackgroundResource(R.drawable.coup3);
				break;
				case 4:
					fondLayout.setBackgroundResource(R.drawable.fini);
				break;
		    }
		}
		
		//lancement des sons
		public void launchSound(int raw){
				
					Log.i("lancer un son","lancer");
					btn_oui.setEnabled(false);
     				btn_non.setEnabled(false);
     				btn_oui.setVisibility(View.INVISIBLE);
     				btn_non.setVisibility(View.INVISIBLE);
					soundPool.load(this, raw, 1);
					soundPool.setOnLoadCompleteListener(new OnLoadCompleteListener()
					 {
					    @Override
					    public void onLoadComplete(SoundPool soundPool, int sampleId,int status) {
					    	btn_oui.setEnabled(true);
		     				btn_non.setEnabled(true);
		     				soundPool.play(sampleId, 1, 1, status, status, 1f);
		     				btn_oui.setVisibility(View.VISIBLE);
		     				btn_non.setVisibility(View.VISIBLE);
					 }
					 });
		}
		
		
		
		@TargetApi(Build.VERSION_CODES.LOLLIPOP)
		protected void createNewSoundPool(){
			AudioAttributes attributes = new AudioAttributes.Builder()
			.setUsage(AudioAttributes.USAGE_GAME)
			.setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
			.build();
			soundPool = new SoundPool.Builder()
			.setAudioAttributes(attributes)
			.build();
		}
		@SuppressWarnings("deprecation")
		protected void createOldSoundPool(){
			soundPool = new SoundPool(20,AudioManager.STREAM_MUSIC,0);
		}
		
	    
}
