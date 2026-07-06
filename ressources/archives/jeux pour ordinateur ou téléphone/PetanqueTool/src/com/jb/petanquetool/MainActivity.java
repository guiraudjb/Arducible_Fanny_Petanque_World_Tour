package com.jb.petanquetool;


import java.io.IOException;
import android.animation.ObjectAnimator;
import android.animation.ValueAnimator;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

public class MainActivity extends Activity implements View.OnClickListener {

    private static final String TAG = "MainActivity";
    Button start,rules,retour,btn_plus,btn_moins;
    ImageView imagev;
    TextView NBJOUEUR;
    Intent svc;
    int nbjoueurs=2;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        start=(Button)this.findViewById(R.id.start);
        rules=(Button)this.findViewById(R.id.regles);
        btn_plus=(Button)this.findViewById(R.id.btn_plus);
        btn_moins=(Button)this.findViewById(R.id.btn_moins);
        start.setOnClickListener(this);
        rules.setOnClickListener(this);
        btn_plus.setOnClickListener(this);
        btn_moins.setOnClickListener(this);
        //affichage du nombre de joueurs pour la partie
        NBJOUEUR=(TextView)this.findViewById(R.id.NBJOUEUR);
        NBJOUEUR.setText("2");
        //musique de fond
        svc=new Intent(this, BackgroundSoundService.class);
		startService(svc);
		

    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        getMenuInflater().inflate(R.menu.main, menu);
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        return super.onOptionsItemSelected(item);
    }

    @Override
    public void onClick(View v) {
    	// TODO Auto-generated method stub
    			switch(v.getId())
    	        {
    	            case R.id.start:
    	            	start.setEnabled(false);
    	            	btn_moins.setEnabled(false);
    	            	btn_plus.setEnabled(false);
    	            	rules.setEnabled(false);
    	            	Intent intent = new Intent(this, ActivityPetanque.class);
    	            	intent.putExtra("nbjoueurs", nbjoueurs);
    	            	stopService(svc);
    	            	startActivityForResult(intent, 1000);
    				break;
    	            case R.id.btn_plus:
    	            	if(nbjoueurs<8){
    	            		nbjoueurs++;
    	            		NBJOUEUR.setText(String.valueOf(nbjoueurs));
    	            		btn_moins.setVisibility(View.VISIBLE);
    	            		if(nbjoueurs==8){
    	            			btn_plus.setVisibility(View.INVISIBLE);
    	            		}
    	            	}
    				break;
    	            case R.id.btn_moins:
    	            	if(nbjoueurs>1){
    	            		nbjoueurs--;
    	            		NBJOUEUR.setText(String.valueOf(nbjoueurs));
    	            		btn_plus.setVisibility(View.VISIBLE);
    	            		if(nbjoueurs==1){
    	            			btn_moins.setVisibility(View.INVISIBLE);
    	            		}
    	            	}	
    				break;
    	            case R.id.regles:
    	            	Intent intent2 = new Intent(this, ActivityRegles.class);
    	            	startActivityForResult(intent2, 1000);
    	            	
    				break;
    	            
    	        }
    }
    
    
    @Override
    public void onStart() {
      super.onStart();
    }
	
	@Override
	public void onPause() {
	  //adView.pause();
	  super.onPause();
	  //mBackgroundSound.cancel(true);
	 
	}

	@Override
	public void onResume() {
	  super.onResume();
	  //mBackgroundSound.execute();
	  //adView.resume();
	}
	
	@Override
    public void onStop() {
      super.onStop();
      // The rest of your onStop() code.
      //mHelper.onStop();
    }

	@Override
	public void onDestroy() {
	  //adView.destroy();
	  super.onDestroy();
	}
	
	protected void onActivityResult (int requestCode, int resultCode, Intent data) {
        // on récupère le statut de retour de l'activité 2 c'est à dire l'activité numéro 1000
		start.setEnabled(true);
    	btn_moins.setEnabled(true);
    	btn_plus.setEnabled(true);
    	rules.setEnabled(true);
        super.onActivityResult (requestCode, resultCode, data);
    }
    
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) 
    {
               
        if (keyCode == KeyEvent.KEYCODE_BACK) 
        {
        	stopService(svc);
            return super.onKeyDown(keyCode, event);
        }else{
            return super.onKeyDown(keyCode, event);
        }
    }
}
