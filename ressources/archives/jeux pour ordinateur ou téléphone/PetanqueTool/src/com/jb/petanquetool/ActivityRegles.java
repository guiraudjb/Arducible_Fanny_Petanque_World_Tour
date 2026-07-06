package com.jb.petanquetool;


import java.io.IOException;
import android.app.Activity;
import android.content.Intent;
import android.graphics.Color;
import android.os.Bundle;
import android.util.Log;
import android.view.KeyEvent;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.view.animation.DecelerateInterpolator;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.TextView;
import android.widget.Toast;

public class ActivityRegles extends Activity implements View.OnClickListener {

    private static final String TAG = "MainActivity";
    Button retour;
    ImageView imagev;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_regles);
        retour=(Button)this.findViewById(R.id.retour);
        retour.setOnClickListener(this);

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
    	            case R.id.retour:
    	            	finish();
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
        super.onActivityResult (requestCode, resultCode, data);
    }
    
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) 
    {
               
        if (keyCode == KeyEvent.KEYCODE_BACK) 
        {
        	finish();
            return super.onKeyDown(keyCode, event);
        }else{
            return super.onKeyDown(keyCode, event);
        }
    }
}
