package com.familyforce.updates;

import android.app.Instrumentation;
import android.os.Bundle;
import org.json.*;

/** Device-only QA harness; never included in the released AAR/APK. */
public final class PolicyTests extends Instrumentation {
    private int checks;
    private void check(boolean ok,String name){checks++;if(!ok)throw new AssertionError(name);}
    private JSONObject release(String tag,String name) throws Exception {
        JSONObject a=new JSONObject().put("name",name).put("state","uploaded").put("size",100)
            .put("digest","sha256:"+new String(new char[64]).replace('\0','a'))
            .put("browser_download_url",ReleasePolicy.PREFIX+tag+"/"+name);
        return new JSONObject().put("tag_name",tag).put("draft",false).put("prerelease",true).put("assets",new JSONArray().put(a));
    }
    private ReleasePolicy.Candidate pick(JSONObject r) throws Exception{return ReleasePolicy.choose(new JSONArray().put(r),"0.5.4-test",null);}
    @Override public void onCreate(Bundle args){super.onCreate(args);start();}
    @Override public void onStart(){
        Bundle result=new Bundle();
        try {
            check(ReleasePolicy.compare("unity-v0.5.10-updates","0.5.9")>0,"Numeric ordering");
            check(ReleasePolicy.compare("unity-v0.5.5-updates","0.5.5-local")==0,"Same version");
            check(pick(release("unity-v0.5.5-updates","FamilyForceUnity-Updates.apk"))!=null,"Include pre-release");
            check(pick(release("unity-v0.5.4-old","FamilyForceUnity-Old.apk"))==null,"No downgrade");
            check(pick(release("v99.0.0","FamilyForceUnity-Wrong.apk"))==null,"Legacy channel excluded");
            check(pick(release("unity-v0.5.5-updates","OtherGame.apk"))==null,"Wrong asset");
            JSONObject draft=release("unity-v0.5.5-updates","FamilyForceUnity-Updates.apk").put("draft",true);
            check(pick(draft)==null,"Draft excluded");
            JSONObject bad=release("unity-v0.5.5-updates","FamilyForceUnity-Updates.apk");
            bad.getJSONArray("assets").getJSONObject(0).put("digest","");check(pick(bad)==null,"Missing digest");
            bad.getJSONArray("assets").getJSONObject(0).put("digest","sha256:"+new String(new char[64]).replace('\0','a')).put("browser_download_url","https://evil.example/a.apk");
            check(pick(bad)==null,"Foreign repository");
            check(!ReleasePolicy.allowedDownload("http://github.com/linkq8/family-force-neon-streets/releases/download/x/a.apk"),"HTTPS required");
            check(!ReleasePolicy.allowedDownload("https://release-assets.githubusercontent.com.evil.example/a"),"Host suffix attack");
            check(!ReleasePolicy.allowedDownload("https://evil@release-assets.githubusercontent.com/a"),"User info rejected");
            check(ReleasePolicy.allowedDownload("https://release-assets.githubusercontent.com/a"),"GitHub CDN allowed");
            check(!ReleasePolicy.allowedDownload("https://github.com/another/repo/a.apk"),"Other repo rejected");
            JSONArray unordered=new JSONArray().put(release("unity-v0.6.0","FamilyForceUnity-New.apk")).put(release("unity-v0.5.5","FamilyForceUnity-Older.apk"));
            check(ReleasePolicy.choose(unordered,"0.5.4",null).tag.equals("unity-v0.6.0"),"Highest semantic version");
            result.putString("stream","PASS "+checks+" release-policy checks\n");finish(-1,result);
        }catch(Throwable t){result.putString("stream","FAIL "+t);finish(1,result);}
    }
}
