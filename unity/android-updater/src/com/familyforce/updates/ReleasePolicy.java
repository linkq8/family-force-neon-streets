package com.familyforce.updates;

import org.json.*;
import java.net.URI;
import java.util.regex.*;

/** Only this repository's Unity APK channel, including its published pre-releases. */
public final class ReleasePolicy {
    public static final String API = "https://api.github.com/repos/linkq8/family-force-neon-streets/releases?per_page=100&page=";
    public static final String PREFIX = "https://github.com/linkq8/family-force-neon-streets/releases/download/";
    public static final long MAX_APK = 512L * 1024 * 1024;
    public static final class Candidate {
        public String tag, url, sha, version;
        public long size;
    }
    public static int compare(String a, String b) {
        int[] x = version(a), y = version(b);
        for (int i=0;i<3;i++) { int c=Integer.compare(x[i],y[i]); if(c!=0)return c; }
        return 0;
    }
    private static int[] version(String s) {
        Matcher m=Pattern.compile("^(?:unity-v)?(\\d{1,6})\\.(\\d{1,6})\\.(\\d{1,6})(?:$|[-+].*)").matcher(s);
        if(!m.matches())throw new IllegalArgumentException("Invalid version");
        return new int[]{Integer.parseInt(m.group(1)),Integer.parseInt(m.group(2)),Integer.parseInt(m.group(3))};
    }
    public static Candidate choose(JSONArray releases, String installed, Candidate best) throws JSONException {
        for(int i=0;i<releases.length();i++) {
            JSONObject r=releases.getJSONObject(i); String tag=r.optString("tag_name");
            if(r.optBoolean("draft") || !tag.startsWith("unity-v"))continue;
            try { if(compare(tag,installed)<=0 || (best!=null && compare(tag,best.tag)<=0))continue; }
            catch(IllegalArgumentException bad){continue;}
            JSONArray assets=r.optJSONArray("assets"); if(assets==null)continue;
            for(int j=0;j<assets.length();j++) {
                JSONObject a=assets.getJSONObject(j);
                String name=a.optString("name"), url=a.optString("browser_download_url"), digest=a.optString("digest");
                long size=a.optLong("size");
                if(!name.matches("FamilyForceUnity[A-Za-z0-9._-]*\\.apk") || !"uploaded".equals(a.optString("state"))
                    || !url.equals(PREFIX+tag+"/"+name) || !digest.matches("sha256:[a-fA-F0-9]{64}")
                    || size<=0 || size>MAX_APK)continue;
                Candidate c=new Candidate();c.tag=tag;c.version=tag.substring(7);c.url=url;
                c.sha=digest.substring(7).toLowerCase(java.util.Locale.ROOT);c.size=size;best=c;break;
            }
        }
        return best;
    }
    public static boolean allowedDownload(String url) {
        try {
            URI u=new URI(url);String h=u.getHost();
            return "https".equals(u.getScheme()) && u.getUserInfo()==null && (u.getPort()==-1 || u.getPort()==443)
                && (("github.com".equals(h) && url.startsWith(PREFIX))
                || "release-assets.githubusercontent.com".equals(h) || "objects.githubusercontent.com".equals(h));
        } catch(Exception e){return false;}
    }
}
