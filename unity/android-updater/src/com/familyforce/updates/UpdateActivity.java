package com.familyforce.updates;

import android.app.*;
import android.content.*;
import android.content.pm.*;
import android.net.Uri;
import android.os.*;
import android.provider.Settings;
import android.graphics.Color;
import android.view.*;
import android.widget.*;
import org.json.*;
import java.io.*;
import java.net.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.concurrent.*;

/**
 * Operate: extend the existing midnight/gold game menu, not the commercial-guide website.
 * Show installed version, check result, download progress and one next action. Native controls
 * support touch, D-pad, font scaling and a scrollable landscape screen. Installation is explicit.
 */
public final class UpdateActivity extends Activity {
    private final ExecutorService worker=Executors.newSingleThreadExecutor();
    private volatile boolean cancelled;
    private volatile HttpURLConnection connection;
    private TextView status;
    private ProgressBar progress;
    private Button action, back;
    private ReleasePolicy.Candidate candidate;
    private String installed;
    private boolean ready;
    private File apk;
    private final int ink=Color.rgb(245,247,239), gold=Color.rgb(250,198,46);

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        apk=new File(getCacheDir(),"updates/update.apk");
        try {installed=getPackageManager().getPackageInfo(getPackageName(),0).versionName;}
        catch(Exception e){installed="0.0.0";}
        ScrollView scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setBackgroundColor(Color.rgb(12,15,31));
        LinearLayout box=new LinearLayout(this);box.setOrientation(LinearLayout.VERTICAL);box.setPadding(dp(28),dp(16),dp(28),dp(16));
        scroll.addView(box,new ScrollView.LayoutParams(-1,-2));setContentView(scroll);
        TextView title=label("Check New Updates",26,gold);box.addView(title);
        box.addView(label("Installed: "+installed+"  •  Unity test releases",14,ink));
        status=label("Checking GitHub…",18,ink);status.setPadding(0,dp(14),0,dp(10));box.addView(status);
        progress=new ProgressBar(this,null,android.R.attr.progressBarStyleHorizontal);progress.setMax(100);box.addView(progress,new LinearLayout.LayoutParams(-1,dp(8)));
        action=new Button(this);action.setText("Checking…");action.setEnabled(false);action.setMinHeight(dp(48));box.addView(action);
        back=new Button(this);back.setText("Back to game");back.setMinHeight(dp(48));back.setOnClickListener(v->finish());box.addView(back);
        check();
    }
    private int dp(int n){return Math.round(n*getResources().getDisplayMetrics().density);}
    private TextView label(String s,int size,int color){TextView t=new TextView(this);t.setText(s);t.setTextSize(size);t.setTextColor(color);return t;}
    private void ui(Runnable r){runOnUiThread(()->{if(!isFinishing()&&!isDestroyed())r.run();});}
    private void check(){
        cancelled=false;ready=false;candidate=null;progress.setIndeterminate(true);action.setEnabled(false);action.setText("Checking…");
        status.setText("Checking GitHub for this game's latest Unity APK…");
        worker.execute(()->{
            try {
                ReleasePolicy.Candidate found=null;
                // Paginate the published channel; GitHub /latest omits our pre-releases.
                for(int page=1;page<=10;page++) {
                    if(cancelled)return;
                    JSONArray list=new JSONArray(fetch(ReleasePolicy.API+page));
                    found=ReleasePolicy.choose(list,installed,found);
                    if(list.length()<100)break;
                    if(page==10)throw new IOException("Release list is too large. Please try again later.");
                }
                final ReleasePolicy.Candidate result=found;
                ui(()->{
                    candidate=result;progress.setIndeterminate(false);progress.setProgress(0);action.setEnabled(true);
                    if(result==null){status.setText("You're up to date.\nNo newer compatible Unity APK is published.");action.setText("Check again");action.setOnClickListener(v->check());}
                    else {status.setText("Update available: "+result.version+"\nDownload: "+String.format(Locale.US,"%.1f MB",result.size/1048576.0)+"\nYour game data stays in place. Android will ask before installing.");action.setText("Download update");action.setOnClickListener(v->download());}
                });
            }catch(Exception e){error(e);}
        });
    }
    private HttpURLConnection open(String address,boolean download) throws IOException {
        for(int redirect=0;redirect<6;redirect++){
            if(cancelled)throw new IOException("Cancelled");
            if(download&&!ReleasePolicy.allowedDownload(address))throw new IOException("Untrusted download address.");
            HttpURLConnection c=(HttpURLConnection)new URL(address).openConnection();connection=c;
            c.setInstanceFollowRedirects(false);c.setConnectTimeout(15000);c.setReadTimeout(20000);
            c.setRequestProperty("User-Agent","FamilyForce-Android-Updater");c.setRequestProperty("Accept",download?"application/octet-stream":"application/vnd.github+json");
            int code=c.getResponseCode();
            if(code>=300&&code<400){String next=c.getHeaderField("Location");c.disconnect();if(!download||next==null)throw new IOException("Unexpected server redirect.");address=new URL(new URL(address),next).toString();continue;}
            if(code==403||code==429){c.disconnect();throw new IOException("GitHub is temporarily limiting requests. Try again later.");}
            if(code!=200){c.disconnect();throw new IOException("GitHub returned HTTP "+code+". Try again later.");}
            return c;
        }
        throw new IOException("Too many download redirects.");
    }
    private String fetch(String url) throws IOException {
        HttpURLConnection c=open(url,false);
        try(InputStream in=c.getInputStream();ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] b=new byte[8192];int n;while((n=in.read(b))!=-1){if(cancelled)throw new IOException("Cancelled");if(out.size()+n>8*1024*1024)throw new IOException("Release response too large.");out.write(b,0,n);}
            return out.toString("UTF-8");
        }finally{c.disconnect();connection=null;}
    }
    private void download(){
        cancelled=false;action.setEnabled(false);action.setText("Downloading…");back.setText("Cancel download");progress.setIndeterminate(false);
        status.setText("Downloading update… Keep this screen open.");
        worker.execute(()->{
            File part=new File(apk.getParentFile(),"update.part");
            try {
                if(!apk.getParentFile().isDirectory()&&!apk.getParentFile().mkdirs())throw new IOException("Cannot create download folder.");
                if(apk.exists()&&!apk.delete())throw new IOException("Cannot replace old update.");
                // Download, installer staging, extracted code and optimization coexist
                // during an update. This is a conservative budget, not an OS guarantee.
                long free=getCacheDir().getUsableSpace();
                long budget=candidate.size*3+128L*1024*1024;
                if(free<budget)throw new IOException("Low internal storage: "+(free/1048576)+" MB free. Please free at least "+(budget/1048576)+" MB total for download and installation, then retry. Do not uninstall the game.");
                HttpURLConnection c=open(candidate.url,true);MessageDigest hash=MessageDigest.getInstance("SHA-256");
                long count=0;int last=-1;
                try(InputStream in=c.getInputStream();FileOutputStream out=new FileOutputStream(part)){
                    byte[] b=new byte[65536];int n;
                    while((n=in.read(b))!=-1){
                        if(cancelled)throw new IOException("Cancelled");count+=n;if(count>candidate.size)throw new IOException("Unexpected APK size.");out.write(b,0,n);hash.update(b,0,n);
                        int percent=(int)(count*100/candidate.size);if(percent!=last){last=percent;ui(()->{progress.setProgress(percent);status.setText("Downloading update… "+percent+"%\nKeep this screen open. Back cancels the download.");});}
                    }
                }finally{c.disconnect();connection=null;}
                if(count!=candidate.size||!hex(hash.digest()).equals(candidate.sha))throw new IOException("Download verification failed. Retry on a stable connection.");
                validatePackage(part);
                if(cancelled)throw new IOException("Cancelled");
                if(!part.renameTo(apk))throw new IOException("Cannot save verified update.");
                ui(()->{ready=true;showInstall();});
            }catch(Exception e){part.delete();error(e);}
        });
    }
    @SuppressWarnings("deprecation")
    private void validatePackage(File file) throws Exception {
        PackageManager pm=getPackageManager();
        PackageInfo next=pm.getPackageArchiveInfo(file.getPath(),PackageManager.GET_SIGNATURES);
        PackageInfo current=pm.getPackageInfo(getPackageName(),PackageManager.GET_SIGNATURES);
        if(next==null||!getPackageName().equals(next.packageName))throw new IOException("This APK is not for this game.");
        long nv=Build.VERSION.SDK_INT>=28?next.getLongVersionCode():next.versionCode;
        long cv=Build.VERSION.SDK_INT>=28?current.getLongVersionCode():current.versionCode;
        if(nv<=cv||ReleasePolicy.compare(next.versionName,installed)<=0||ReleasePolicy.compare(next.versionName,candidate.tag)!=0)throw new IOException("APK version is not a newer matching update.");
        if(next.signatures==null||current.signatures==null||!new HashSet<>(Arrays.asList(next.signatures)).equals(new HashSet<>(Arrays.asList(current.signatures))))throw new IOException("APK signature does not match this game.");
    }
    private static String hex(byte[] b){StringBuilder s=new StringBuilder();for(byte v:b)s.append(String.format(Locale.US,"%02x",v&255));return s.toString();}
    private boolean needsPermission(){return Build.VERSION.SDK_INT>=26&&!getPackageManager().canRequestPackageInstalls();}
    private void showInstall(){
        progress.setIndeterminate(false);progress.setProgress(100);back.setText("Back to game");action.setEnabled(true);
        if(needsPermission()){
            status.setText("Download verified.\nAllow this game to install updates in Android Settings, then return here. Installation always needs your confirmation.");
            action.setText("Allow update installation");
        }else{status.setText("Update ready. File integrity, game identity and signature verified.\nTap Install update to open Android's confirmation.");action.setText("Install update");}
        action.setOnClickListener(v->{try{
            if(needsPermission()){startActivity(new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,Uri.parse("package:"+getPackageName())));return;}
            Uri uri=Uri.parse("content://"+getPackageName()+".updates/update.apk");
            Intent intent=new Intent(Intent.ACTION_VIEW).setDataAndType(uri,"application/vnd.android.package-archive");
            intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);intent.setClipData(ClipData.newRawUri("Game update",uri));startActivity(intent);
        }catch(Exception e){status.setText("Android could not open the installer. Check device restrictions and try again.");}});
    }
    @Override protected void onResume(){super.onResume();if(ready)showInstall();}
    private void error(Exception e){
        if(cancelled)return;
        android.util.Log.w("FFUpdater","Update failed",e);
        String reason=(e instanceof java.net.SocketException || e instanceof java.net.SocketTimeoutException
            || e instanceof java.net.UnknownHostException || e instanceof javax.net.ssl.SSLException)
            ? "Couldn't reach GitHub. Check your connection and try again."
            : e instanceof IOException ? e.getMessage() : "Could not read or verify the update. Please try again.";
        ui(()->{progress.setIndeterminate(false);progress.setProgress(0);status.setText("Update not completed.\n"+reason);back.setText("Back to game");action.setText("Try again");action.setEnabled(true);action.setOnClickListener(v->check());});
    }
    @Override protected void onDestroy(){cancelled=true;HttpURLConnection c=connection;if(c!=null)c.disconnect();worker.shutdownNow();super.onDestroy();}
}
