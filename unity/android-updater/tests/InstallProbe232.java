package com.familyforce.updates;
import android.app.*;
import android.content.*;
import android.os.Bundle;
import java.lang.reflect.*;
import java.io.File;
/** LOCAL ONLY: use the real activity/session installer with a locally staged verified APK. */
public final class InstallProbe232 extends Instrumentation {
    @Override public void onCreate(Bundle args){super.onCreate(args);start();}
    @Override public void onStart(){
        Bundle result=new Bundle();
        try{
            Activity a=startActivitySync(new Intent(getTargetContext(),UpdateActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            // Finish the bounded network check before injecting this test candidate.
            Thread.sleep(22000);
            runOnMainSync(()->{
                try{
                    ReleasePolicy.Candidate c=new ReleasePolicy.Candidate();c.tag="unity-v0.5.10-repairs";
                    Field candidate=UpdateActivity.class.getDeclaredField("candidate");candidate.setAccessible(true);candidate.set(a,c);
                    Field apk=UpdateActivity.class.getDeclaredField("apk");apk.setAccessible(true);apk.set(a,new File(a.getFilesDir(),"test-update.apk"));
                    Method install=UpdateActivity.class.getDeclaredMethod("installSession");install.setAccessible(true);install.invoke(a);
                }catch(Exception e){throw new RuntimeException(e);}
            });
            Thread.sleep(30000);
            result.putString("stream","Session dispatched; confirm Android UI and inspect installed version.\n");finish(-1,result);
        }catch(Throwable e){result.putString("stream","FAIL "+e);finish(1,result);}
    }
}
