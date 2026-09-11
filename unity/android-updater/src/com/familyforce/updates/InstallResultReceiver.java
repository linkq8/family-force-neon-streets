package com.familyforce.updates;
import android.content.*;
import android.content.pm.PackageInstaller;
public final class InstallResultReceiver extends BroadcastReceiver {
    @Override public void onReceive(Context context,Intent intent){
        int code=intent.getIntExtra(PackageInstaller.EXTRA_STATUS,PackageInstaller.STATUS_FAILURE);
        if(code==PackageInstaller.STATUS_PENDING_USER_ACTION){
            Intent confirm=intent.getParcelableExtra(Intent.EXTRA_INTENT);
            try {if(confirm==null)throw new IllegalStateException("Missing confirmation");confirm.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);context.startActivity(confirm);return;}
            catch(Exception e){save(context,"Android could not open installation confirmation. Return to the game and retry.");return;}
        }
        String detail=intent.getStringExtra(PackageInstaller.EXTRA_STATUS_MESSAGE);
        String reason=code==PackageInstaller.STATUS_SUCCESS?"Update installed successfully."
            : code==PackageInstaller.STATUS_FAILURE_STORAGE?"Not enough internal storage."
            : code==PackageInstaller.STATUS_FAILURE_CONFLICT?"Update conflicts with the installed package/signature."
            : code==PackageInstaller.STATUS_FAILURE_INCOMPATIBLE?"APK is incompatible with this device."
            : code==PackageInstaller.STATUS_FAILURE_BLOCKED?"Installation blocked by device policy."
            : code==PackageInstaller.STATUS_FAILURE_ABORTED?"Installation cancelled."
            : "Installation failed.";
        save(context,reason+"\nStatus: "+code+(detail==null?"":"\n"+detail));
    }
    private static void save(Context context,String text){context.getSharedPreferences("ff_install",0).edit().putString("result",text).putString("last_result",text).apply();}
}
