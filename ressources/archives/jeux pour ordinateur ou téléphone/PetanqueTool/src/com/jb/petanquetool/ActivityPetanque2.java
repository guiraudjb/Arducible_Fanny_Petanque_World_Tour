package com.jb.petanquetool;

import android.os.Build;


import android.os.Bundle;
import android.os.Message;
import android.util.Log;
import android.os.Handler;
import android.os.CountDownTimer;
import android.widget.*;
import android.annotation.TargetApi;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.res.Resources;
import android.media.AudioAttributes;
import android.media.AudioManager;
import android.media.MediaPlayer;
import android.media.MediaPlayer.OnCompletionListener;
//import android.content.DialogInterface.OnClickListener;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.View;
import android.view.View.OnClickListener;
import android.widget.Toast;
import android.media.SoundPool;
import android.media.SoundPool.OnLoadCompleteListener;
import java.math.BigDecimal;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;


public class ActivityPetanque2 extends Activity implements OnClickListener {

		TextView score_personne;//score de la personne
		Resources res;
		boolean victoire;
		boolean finpartie;
		boolean masteron;
		public Handler handler;
		MediaPlayer mediaPlayer;
		Button scoreJ1,scoreJ2, scoreJ3,scoreJ4, scoreJ5, scoreJ6, scoreJ7, scoreJ8;
		Button btn_oui,btn_non;
		LinearLayout linearLayoutNbJ,mainLayout,linearLayoutScore,linearLayoutFinal;
		TextView NBTOURTEXT,NUMJTOURTEXT,NBCIBLETEXT,TEXTtoucher;
		ImageView plateau;
		int nbjoueur=1;
		//numéro de tour des joueurs
		int nbTour;
		//tableau des joueurs ayant touché consécutivement une boule
		int [] bouleTouche;
		//tableau des scores des joueurs
		float [] TabScore;
		//tableau des cibles des joueurs
		float [] TabTauxReussite;
		int [] TabCible;
		//tableau du nombre de tir effectué par chaque joueur
		int [] TabNbTirsEffectues;
		//tableau des bonus atteint par les joueurs
		int [] TabBonusAcquis;
		//tableau des points bonus actuel des joueurs
		int [] TabPointsBonus;
		//tableau des masters
		boolean [] TabMaster;
		//nombre de boules totales
		int nbboulesTot;
		//numéro du joueur qui va joueur
		int joueurencour;
		//numéro de la boule a lancé par tour (1,2 ou 3)
		int NBoule;
		SoundPool soundPool;
		
	    @Override
	    public void onCreate(Bundle savedInstanceState) {
	        super.onCreate(savedInstanceState);
	        setContentView(R.layout.activity_petanque);
	        linearLayoutNbJ= (LinearLayout)this.findViewById(R.id.linearLayoutNbJ);
	        //linearLayoutScore= (LinearLayout)this.findViewById(R.id.linearLayoutScore);
	        //linearLayoutFinal= (LinearLayout)this.findViewById(R.id.linearLayoutFinal);
	        mainLayout= (LinearLayout)this.findViewById(R.id.mainLayout);
			Bundle extras = getIntent().getExtras();
			nbjoueur = extras.getInt("NBJOUEUR");
			res=getResources();
			//plateau=(ImageView)this.findViewById(R.id.plateau);
			NBTOURTEXT=(TextView)this.findViewById(R.id.NBTOURJ);
			NUMJTOURTEXT=(TextView)this.findViewById(R.id.NUMBTOURJ);
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
			bouleTouche = new int [nbjoueur];
			TabScore = new float [nbjoueur];
			TabPointsBonus= new int [nbjoueur];
			TabBonusAcquis= new int [nbjoueur];
			TabNbTirsEffectues= new int [nbjoueur];
			TabCible= new int [nbjoueur];
			TabMaster= new boolean [nbjoueur];
			init();
	        
	    }
	    
	    private void init() {
	    	if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.LOLLIPOP) {
				createNewSoundPool();
			}else{
				createOldSoundPool();
			}
			nbboulesTot=0;
			joueurencour=1;
			NBoule=1;
	    	nbTour=0;
	    	victoire=false;
	    	finpartie=false;
	    	nbboulesTot=nbjoueur*30;
			int tailleTab=TabScore.length;
			for(int i=0; i<tailleTab;i++){
				TabScore[i]=0;
				TabBonusAcquis[i]=0;
				TabPointsBonus[i]=0;
				TabNbTirsEffectues[i]=0;
				TabCible[i]=0;
				TabMaster[i]=false;
			}
			//affichage des scores des joueurs
			scoreJ1.setText("J1" + "\n" + "000");
			scoreJ1.setEnabled(false);
			affichageScoreText(1);
			scoreJ2.setText("J2" + "\n" + "000");
			scoreJ2.setEnabled(false);
			scoreJ3.setText("J3" + "\n" + "000");
			scoreJ3.setEnabled(false);
			scoreJ4.setText("J4" + "\n" + "000");
			scoreJ4.setEnabled(false);
			scoreJ5.setText("J5" + "\n" + "000");
			scoreJ5.setEnabled(false);
			scoreJ6.setText("J6" + "\n" + "000");
			scoreJ6.setEnabled(false);
			scoreJ7.setText("J7" + "\n" + "000");
			scoreJ7.setEnabled(false);
			scoreJ8.setText("J8" + "\n" + "000");
			scoreJ8.setEnabled(false);
			//rendre invisible les joueurs qui ne participe pas
			displaynbJScore();
			NBTOURTEXT.setText("1");
			NUMJTOURTEXT.setText("J1");
			NBTOURTEXT.setText("1");
			NBCIBLETEXT.setText("1");
			TEXTtoucher.setText(res.getString(R.string.toucher));
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
	    	if(nbjoueur<8){
				switch(nbjoueur){
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
	            	if(finpartie==true){
	            		init();
		           	 	btn_oui.setEnabled(true);
						btn_non.setEnabled(true);
						setActivityBackground(1);
						linearLayoutScore.setVisibility(View.VISIBLE);
						linearLayoutFinal.setVisibility(View.GONE);
	            	}else{
	            		BouleToucher();
	            	}
	            break;
	            case R.id.btn_non:
	            	if(finpartie==true){
	            		finish();
	            	}else{
	            		BouleNonToucher();
	            	}
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
			TabNbTirsEffectues[joueurencour-1]=TabNbTirsEffectues[joueurencour-1]++;
			TabPointsBonus[joueurencour-1]=0;
			//calcul score + affichage
			calculScore(joueurencour-1);
			if (NBoule < 3) {
			   NBoule++;
			   setActivityBackground(NBoule);
		    }else{
		    	NBoule=1;
		    	setActivityBackground(NBoule);
			    if (joueurencour < nbjoueur) {
			       joueurencour++;
			       NUMJTOURTEXT.setText("J"+joueurencour);
			       affichageScoreText(joueurencour);
			    }else{
			        if (nbTour < 9 && victoire == false){
			           nbTour++;
			           joueurencour = 1;
			           NBTOURTEXT.setText(String.valueOf(nbTour+1));
		    		   NUMJTOURTEXT.setText("J"+joueurencour);
		    		   affichageScoreText(joueurencour);
			        }else{
			            finpartie=true;
			            //    trier valeurs des joueurs
			            trieResultat();
			            //    afficher resultats
			        }

			    }

			 }
			 if(finpartie==true){
				//lancement fin de la partie
				//Toast.makeText(this, "A faire prochainement fin de la partie", Toast.LENGTH_LONG).show();
				btn_oui.setEnabled(false);
				btn_non.setEnabled(false);
				setActivityBackground(4);
				//displayReplay();
				linearLayoutScore.setVisibility(View.GONE);
				linearLayoutFinal.setVisibility(View.VISIBLE);
				TEXTtoucher.setText(res.getString(R.string.dialogreplay));
			 }else{
					affichagePlateau(TabCible[joueurencour-1]+1);
			 }
		}
		
		
		private void BouleToucher(){
			launchSound(R.raw.toucher);
			TabNbTirsEffectues[joueurencour-1]=TabNbTirsEffectues[joueurencour-1]+1;
			TabPointsBonus[joueurencour-1]=TabPointsBonus[joueurencour-1]+1;
			TabBonusAcquis[joueurencour-1]=TabBonusAcquis[joueurencour-1]+TabPointsBonus[joueurencour-1];
			if (TabCible[joueurencour-1] < 6) {
				TabCible[joueurencour-1]=TabCible[joueurencour-1]+1;
				//Toast.makeText(this, "TabCible"+TabCible[joueurencour-1], Toast.LENGTH_LONG).show();
			}else{
				TabCible[joueurencour-1]=TabCible[joueurencour-1]+1;
				//calcul score + affichage
				calculScore(joueurencour-1);
			    victoire = true;
			    NBoule = 3;
			}
			if (NBoule < 3) {
				//calcul score + affichage
				calculScore(joueurencour-1);
			    NBoule++;
			    setActivityBackground(NBoule);
		    }else{
			    if (joueurencour < nbjoueur) {
			    	    if(victoire==false){
				    		//calcul score + affichage
							calculScore(joueurencour-1);
			    	    }
			            joueurencour++;
			            NUMJTOURTEXT.setText("J"+joueurencour);
			            affichageScoreText(joueurencour);
			            NBoule=1;
			            setActivityBackground(NBoule);
			    }else{
			            if (nbTour < 9 && victoire == false){
			            	//calcul score + affichage
							calculScore(joueurencour-1);
			            	nbTour++;
			                joueurencour = 1;
			                NBTOURTEXT.setText(String.valueOf(nbTour+1));
			    			NUMJTOURTEXT.setText("J"+joueurencour);
			    			affichageScoreText(joueurencour);
			                NBoule=1;
			                setActivityBackground(NBoule);
			            }else{
			                finpartie=true;
			            //  trier valeurs des joueurs
			                trieResultat();
			            //  afficher resultats
			            }

			     }

			}
			if(finpartie==true){
				//lancement fin de la partie
				btn_oui.setEnabled(false);
				btn_non.setEnabled(false);
				linearLayoutScore.setVisibility(View.GONE);
				linearLayoutFinal.setVisibility(View.VISIBLE);
				TEXTtoucher.setText(res.getString(R.string.dialogreplay));
				setActivityBackground(4);
				//displayReplay();
			}else{
				affichagePlateau(TabCible[joueurencour-1]+1);
			}
		}
		
		private void trieResultat(){
			int indice=0;
			float max=TabScore[0];
			for(int i=1;i<nbjoueur;i++){
				if(max<TabScore[i]){
					indice=i;
					max=TabScore[i];
				}
			}
			indice++;
			//Toast.makeText(this, "Meilleur joueur J"+indice, Toast.LENGTH_LONG).show();
			//Toast.makeText(this, "avec le score de "+max, Toast.LENGTH_LONG).show();
		}
		
		//calcul du score des joueurs et affichage
		private void calculScore(int indice){
			TabScore[joueurencour-1]=TabCible[joueurencour-1];
			//Toast.makeText(this, String.valueOf(TabCible[joueurencour-1]), Toast.LENGTH_LONG).show();
			TabScore[joueurencour-1]=TabScore[joueurencour-1]/(nbTour*3+NBoule);
			TabScore[joueurencour-1]=TabScore[joueurencour-1]*100;
			TabScore[joueurencour-1]=round(TabScore[joueurencour-1], 2);
			TabScore[joueurencour-1]+=TabBonusAcquis[joueurencour-1];
			switch(indice){
			case 0:
				scoreJ1.setText("J1" + "\n" + String.valueOf(TabScore[joueurencour-1]));
				break;
			case 1:
				scoreJ2.setText("J2" + "\n" + String.valueOf(TabScore[joueurencour-1]));
				break;
			case 2:
				scoreJ3.setText("J3" + "\n" + String.valueOf(TabScore[joueurencour-1]));
				break;
			case 3:
				scoreJ4.setText("J4" + "\n" + String.valueOf(TabScore[joueurencour-1]));
				break;
			case 4:
				scoreJ5.setText("J5" + "\n" + String.valueOf(TabScore[joueurencour-1]));
				break;
			case 5:
				scoreJ6.setText("J6" + "\n" + String.valueOf(TabScore[joueurencour-1]));
				break;
			case 6:
				scoreJ7.setText("J7" + "\n" + String.valueOf(TabScore[joueurencour-1]));
				break;
			case 7:
				scoreJ8.setText("J8" + "\n" + String.valueOf(TabScore[joueurencour-1]));
				break;
			}
			
		}
		
		public static float round(float d, int decimalPlace) {
	        BigDecimal bd = new BigDecimal(Float.toString(d));
	        bd = bd.setScale(decimalPlace, BigDecimal.ROUND_HALF_UP);
	        return bd.floatValue();
	    }
		
		private void affichagePlateau(int cible){
			NBCIBLETEXT.setText(String.valueOf(cible));
			/*switch(cible){
			case 1:
				//affichage de la boule 1
				//plateau.setImageResource(R.drawable.plateau1);
				
				break;
			case 2:
				plateau.setImageResource(R.drawable.plateau2);
				break;
			case 3:
				plateau.setImageResource(R.drawable.plateau3);
				break;
			case 4:
				plateau.setImageResource(R.drawable.plateau4);
				break;
			case 5:
				plateau.setImageResource(R.drawable.plateau5);
				break;
			case 6:
				plateau.setImageResource(R.drawable.plateau6);
				break;
			case 7:
				plateau.setImageResource(R.drawable.plateau7);
				break;
			}*/
		}
		
		public void setActivityBackground(int cible) {
			
		    switch(cible){
				case 1:
					mainLayout.setBackgroundResource(R.drawable.coup1);
				break;
				case 2:
					mainLayout.setBackgroundResource(R.drawable.coup2);
				break;
				case 3:
					mainLayout.setBackgroundResource(R.drawable.coup3);
				break;
				case 4:
					mainLayout.setBackgroundResource(R.drawable.fini);
				break;
		    }
		}
		
		//lancement des sons
		public void launchSound(int raw){
				
					Log.i("lancer un son","lancer");
					btn_oui.setEnabled(true);
     				btn_non.setEnabled(true);
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
		  			/*mediaPlayer = MediaPlayer.create(getApplicationContext(), raw);
		  			//mediaPlayer.setVolume(1.0f,1.0f);
		  			mediaPlayer.setVolume(1.0f,1.0f);
		  			mediaPlayer.start();
		  			mediaPlayer.setOnCompletionListener(new OnCompletionListener()
					{

						@Override
						// Libérons les ressources lorsque la musique est terminée
						public void onCompletion(MediaPlayer mediaPlayer) {
							// TODO Auto-generated method stub
							mediaPlayer.release();
						}
						
					});*/
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
