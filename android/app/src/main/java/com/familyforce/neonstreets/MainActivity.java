package com.familyforce.neonstreets;

import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.view.Window;
import android.view.WindowManager;
import android.view.KeyEvent;
import android.view.MotionEvent;
import android.widget.TextView;
import android.graphics.Color;

public final class MainActivity extends Activity {
    private GameView gameView;

    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        requestWindowFeature(Window.FEATURE_NO_TITLE);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        if (!IntegrityGuard.isTrustedInstall(this)) {
            showIntegrityFailure();
            return;
        }
        gameView = new GameView(this);
        gameView.setAutomatedFullStageTest(BuildConfig.DEBUG
                && getIntent().getBooleanExtra("familyforce.fullStageTest", false));
        setContentView(gameView);
        gameView.setFocusable(true);
        gameView.setFocusableInTouchMode(true);
        gameView.requestFocus();
        enterImmersiveMode();
    }

    private void showIntegrityFailure() {
        TextView message = new TextView(this);
        message.setText("This copy could not be verified.\nPlease install the original Family Force APK.");
        message.setTextColor(Color.WHITE);
        message.setBackgroundColor(Color.rgb(8, 13, 35));
        message.setTextSize(22f);
        message.setGravity(android.view.Gravity.CENTER);
        message.setPadding(48, 48, 48, 48);
        setContentView(message);
    }

    private void enterImmersiveMode() {
        getWindow().getDecorView().setSystemUiVisibility(
                View.SYSTEM_UI_FLAG_IMMERSIVE_STICKY
                        | View.SYSTEM_UI_FLAG_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_FULLSCREEN
                        | View.SYSTEM_UI_FLAG_LAYOUT_HIDE_NAVIGATION
                        | View.SYSTEM_UI_FLAG_LAYOUT_STABLE);
    }

    @Override
    protected void onResume() {
        super.onResume();
        enterImmersiveMode();
        if (gameView != null) {
            gameView.requestFocus();
            gameView.resumeGame();
        }
    }

    @Override
    protected void onPause() {
        if (gameView != null) gameView.pauseGame();
        super.onPause();
    }

    @Override
    public void onTrimMemory(int level) {
        if (gameView != null) gameView.trimMemory(level);
        super.onTrimMemory(level);
    }

    @Override
    protected void onDestroy() {
        if (gameView != null) gameView.shutdown();
        super.onDestroy();
    }

    @Override
    public void onWindowFocusChanged(boolean hasFocus) {
        super.onWindowFocusChanged(hasFocus);
        if (hasFocus) {
            enterImmersiveMode();
            if (gameView != null) gameView.requestFocus();
        }
    }

    @Override
    public void onBackPressed() {
        if (gameView == null || !gameView.handleBack()) super.onBackPressed();
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        try {
            if (gameView != null && gameView.onKeyDown(keyCode, event)) return true;
            return super.onKeyDown(keyCode, event);
        } catch (Throwable runtimeError) {
            if (gameView != null) {
                gameView.recordInputFailure(runtimeError);
                gameView.enterStateSafe();
            }
            return true;
        }
    }

    @Override
    public boolean dispatchKeyEvent(KeyEvent event) {
        try {
            if (gameView == null || event == null) return super.dispatchKeyEvent(event);
            int action = event.getAction();
            if (action == KeyEvent.ACTION_DOWN) {
                if (gameView.onKeyDown(event.getKeyCode(), event)) return true;
            } else if (action == KeyEvent.ACTION_UP) {
                if (gameView.onKeyUp(event.getKeyCode(), event)) return true;
            }
            return super.dispatchKeyEvent(event);
        } catch (Throwable runtimeError) {
            if (gameView != null) {
                gameView.recordInputFailure(runtimeError);
                gameView.enterStateSafe();
            }
            return true;
        }
    }

    @Override
    public boolean onKeyUp(int keyCode, KeyEvent event) {
        try {
            if (gameView != null && gameView.onKeyUp(keyCode, event)) return true;
            return super.onKeyUp(keyCode, event);
        } catch (Throwable runtimeError) {
            if (gameView != null) {
                gameView.recordInputFailure(runtimeError);
                gameView.enterStateSafe();
            }
            return true;
        }
    }

    @Override
    public boolean dispatchGenericMotionEvent(MotionEvent event) {
        try {
            if (gameView != null && gameView.onGenericMotionEvent(event)) return true;
            return super.dispatchGenericMotionEvent(event);
        } catch (Throwable runtimeError) {
            if (gameView != null) {
                gameView.recordInputFailure(runtimeError);
                gameView.enterStateSafe();
            }
            return true;
        }
    }
}
