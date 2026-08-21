package com.familyforce.neonstreets;

import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.net.Uri;
import android.os.Build;
import android.provider.Settings;
import android.util.Log;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.security.MessageDigest;
import java.util.HashSet;
import java.util.Locale;
import java.util.Set;
import java.util.concurrent.atomic.AtomicBoolean;

final class UpdateManager {
    interface Listener {
        void onStatus(String status, boolean busy);
    }

    private static final String TAG = "FamilyForceUpdate";
    private static final String RELEASE_API =
            "https://api.github.com/repos/linkq8/family-force-neon-streets/releases/latest";
    private static final long MAX_APK_BYTES = 250L * 1024L * 1024L;
    private static final int MAX_JSON_BYTES = 1024 * 1024;
    private static final int CONNECT_TIMEOUT_MS = 12_000;
    private static final int READ_TIMEOUT_MS = 25_000;

    private final Activity activity;
    private final Listener listener;
    private final AtomicBoolean busy = new AtomicBoolean(false);
    private volatile boolean stopped;
    private volatile boolean awaitingInstallPermission;
    private volatile File verifiedApk;

    UpdateManager(Activity activity, Listener listener) {
        this.activity = activity;
        this.listener = listener;
    }

    void checkForUpdate() {
        if (stopped || !busy.compareAndSet(false, true)) return;
        publish("CHECKING...", true);
        Thread worker = new Thread(new Runnable() {
            @Override
            public void run() {
                try {
                    checkAndPrepare();
                } catch (Throwable error) {
                    Log.e(TAG, "Update check failed", error);
                    publish("CHECK FAILED", false);
                } finally {
                    busy.set(false);
                }
            }
        }, "FamilyForce-Update");
        worker.setDaemon(true);
        worker.start();
    }

    void onResume() {
        if (!awaitingInstallPermission || verifiedApk == null || !verifiedApk.isFile()) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                && activity.getPackageManager().canRequestPackageInstalls()) {
            awaitingInstallPermission = false;
            launchInstaller(verifiedApk);
        }
    }

    void shutdown() {
        stopped = true;
    }

    private void checkAndPrepare() throws Exception {
        JSONObject release = new JSONObject(readSmallUrl(RELEASE_API));
        String remoteTag = release.optString("tag_name", "").trim();
        if (remoteTag.isEmpty()) throw new IllegalStateException("Release has no tag");
        if (compareVersions(remoteTag, BuildConfig.VERSION_NAME) <= 0) {
            publish("UP TO DATE", false);
            return;
        }

        String wantedName = "family-force-" + BuildConfig.CUSTOMER_ID + ".apk";
        JSONObject asset = findAsset(release.optJSONArray("assets"), wantedName);
        if (asset == null) throw new IllegalStateException("No matching customer APK");
        String digest = asset.optString("digest", "").trim().toLowerCase(Locale.US);
        if (!digest.startsWith("sha256:") || digest.length() != 71) {
            throw new SecurityException("Release has no trusted SHA-256 digest");
        }
        String expectedHash = digest.substring(7);
        long expectedSize = asset.optLong("size", -1L);
        if (expectedSize <= 0L || expectedSize > MAX_APK_BYTES) {
            throw new SecurityException("Unsafe APK size");
        }

        File updateDir = new File(activity.getCacheDir(), "updates");
        if (!updateDir.isDirectory() && !updateDir.mkdirs()) {
            throw new IllegalStateException("Cannot create update cache");
        }
        File partial = new File(updateDir, "family-force-update.part");
        File ready = new File(updateDir, "family-force-update.apk");
        deleteQuietly(partial);
        deleteQuietly(ready);
        publish("DOWNLOADING", true);
        download(asset.getString("browser_download_url"), partial, expectedSize);
        if (!expectedHash.equals(sha256(partial))) {
            deleteQuietly(partial);
            throw new SecurityException("APK digest mismatch");
        }
        verifyArchive(partial);
        if (!partial.renameTo(ready)) {
            deleteQuietly(partial);
            throw new IllegalStateException("Cannot finalize update");
        }
        verifiedApk = ready;
        publish("UPDATE VERIFIED", false);
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                requestPermissionOrInstall();
            }
        });
    }

    private JSONObject findAsset(JSONArray assets, String wantedName) {
        if (assets == null) return null;
        for (int i = 0; i < assets.length(); i++) {
            JSONObject asset = assets.optJSONObject(i);
            if (asset != null && wantedName.equals(asset.optString("name"))) return asset;
        }
        return null;
    }

    private void requestPermissionOrInstall() {
        if (stopped || verifiedApk == null || !verifiedApk.isFile()) return;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O
                && !activity.getPackageManager().canRequestPackageInstalls()) {
            awaitingInstallPermission = true;
            publish("ALLOW INSTALL", false);
            Intent permission = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES,
                    Uri.parse("package:" + activity.getPackageName()));
            if (permission.resolveActivity(activity.getPackageManager()) != null) {
                activity.startActivity(permission);
            } else {
                awaitingInstallPermission = false;
                publish("OPEN SETTINGS", false);
            }
            return;
        }
        launchInstaller(verifiedApk);
    }

    private void launchInstaller(File apk) {
        try {
            Uri contentUri = UpdateFileProvider.uriFor(activity, apk);
            Intent install = new Intent(Intent.ACTION_INSTALL_PACKAGE);
            install.setData(contentUri);
            install.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            install.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            if (install.resolveActivity(activity.getPackageManager()) == null) {
                publish("NO INSTALLER", false);
                return;
            }
            publish("CONFIRM INSTALL", false);
            activity.startActivity(install);
        } catch (Throwable error) {
            Log.e(TAG, "Could not open package installer", error);
            publish("INSTALL FAILED", false);
        }
    }

    private void verifyArchive(File apk) throws Exception {
        PackageManager pm = activity.getPackageManager();
        PackageInfo archive;
        PackageInfo installed;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            archive = pm.getPackageArchiveInfo(apk.getAbsolutePath(), PackageManager.GET_SIGNING_CERTIFICATES);
            installed = pm.getPackageInfo(activity.getPackageName(), PackageManager.GET_SIGNING_CERTIFICATES);
        } else {
            archive = pm.getPackageArchiveInfo(apk.getAbsolutePath(), PackageManager.GET_SIGNATURES);
            installed = pm.getPackageInfo(activity.getPackageName(), PackageManager.GET_SIGNATURES);
        }
        if (archive == null || !activity.getPackageName().equals(archive.packageName)) {
            throw new SecurityException("Package name mismatch");
        }
        long archiveVersion = Build.VERSION.SDK_INT >= Build.VERSION_CODES.P
                ? archive.getLongVersionCode() : archive.versionCode;
        long installedVersion = Build.VERSION.SDK_INT >= Build.VERSION_CODES.P
                ? installed.getLongVersionCode() : installed.versionCode;
        if (archiveVersion <= installedVersion) throw new SecurityException("Not a newer APK");

        Set<String> archiveCerts = certificateHashes(archive);
        Set<String> installedCerts = certificateHashes(installed);
        if (archiveCerts.isEmpty() || !archiveCerts.equals(installedCerts)) {
            throw new SecurityException("Signing certificate mismatch");
        }
        String pinned = normalizeHex(BuildConfig.EXPECTED_CERT_SHA256);
        if (!pinned.isEmpty() && !archiveCerts.contains(pinned)) {
            throw new SecurityException("Signing certificate is not pinned");
        }
    }

    private Set<String> certificateHashes(PackageInfo info) throws Exception {
        Signature[] signatures;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
            if (info.signingInfo == null) return new HashSet<String>();
            signatures = info.signingInfo.hasMultipleSigners()
                    ? info.signingInfo.getApkContentsSigners()
                    : info.signingInfo.getSigningCertificateHistory();
        } else {
            signatures = info.signatures;
        }
        Set<String> hashes = new HashSet<>();
        if (signatures != null) {
            for (Signature signature : signatures) {
                hashes.add(hex(MessageDigest.getInstance("SHA-256").digest(signature.toByteArray())));
            }
        }
        return hashes;
    }

    private String readSmallUrl(String address) throws Exception {
        HttpURLConnection connection = open(address, "application/vnd.github+json");
        try {
            int code = connection.getResponseCode();
            if (code != HttpURLConnection.HTTP_OK) throw new IllegalStateException("GitHub HTTP " + code);
            InputStream input = new BufferedInputStream(connection.getInputStream());
            ByteArrayOutputStream output = new ByteArrayOutputStream();
            byte[] buffer = new byte[8192];
            int total = 0;
            int count;
            while ((count = input.read(buffer)) != -1) {
                total += count;
                if (total > MAX_JSON_BYTES) throw new SecurityException("Release response too large");
                output.write(buffer, 0, count);
            }
            input.close();
            return output.toString("UTF-8");
        } finally {
            connection.disconnect();
        }
    }

    private void download(String address, File target, long expectedSize) throws Exception {
        HttpURLConnection connection = open(address, "application/octet-stream");
        try {
            int code = connection.getResponseCode();
            if (code != HttpURLConnection.HTTP_OK) throw new IllegalStateException("Download HTTP " + code);
            long announced = connection.getContentLengthLong();
            if (announced > MAX_APK_BYTES || (announced > 0L && announced != expectedSize)) {
                throw new SecurityException("Unexpected download size");
            }
            InputStream input = new BufferedInputStream(connection.getInputStream());
            FileOutputStream output = new FileOutputStream(target);
            byte[] buffer = new byte[32 * 1024];
            long total = 0L;
            int count;
            try {
                while ((count = input.read(buffer)) != -1) {
                    total += count;
                    if (total > MAX_APK_BYTES || total > expectedSize) {
                        throw new SecurityException("APK exceeds declared size");
                    }
                    output.write(buffer, 0, count);
                }
                output.getFD().sync();
            } finally {
                output.close();
                input.close();
            }
            if (total != expectedSize) throw new SecurityException("Incomplete APK download");
        } finally {
            connection.disconnect();
        }
    }

    private HttpURLConnection open(String address, String accept) throws Exception {
        URL url = new URL(address);
        requireAllowedUrl(url);
        for (int redirects = 0; redirects <= 5; redirects++) {
            HttpURLConnection connection = (HttpURLConnection) url.openConnection();
            connection.setInstanceFollowRedirects(false);
            connection.setConnectTimeout(CONNECT_TIMEOUT_MS);
            connection.setReadTimeout(READ_TIMEOUT_MS);
            connection.setRequestProperty("Accept", accept);
            connection.setRequestProperty("User-Agent", "FamilyForce-Android-Updater");
            int code = connection.getResponseCode();
            if (code < 300 || code >= 400) return connection;
            String location = connection.getHeaderField("Location");
            connection.disconnect();
            if (location == null) throw new SecurityException("Redirect has no location");
            url = new URL(url, location);
            requireAllowedUrl(url);
        }
        throw new SecurityException("Too many redirects");
    }

    private void requireAllowedUrl(URL url) {
        if (!"https".equalsIgnoreCase(url.getProtocol())) throw new SecurityException("HTTPS required");
        String host = url.getHost().toLowerCase(Locale.US);
        boolean allowed = host.equals("api.github.com") || host.equals("github.com")
                || host.equals("release-assets.githubusercontent.com")
                || host.endsWith(".githubusercontent.com");
        if (!allowed) throw new SecurityException("Unexpected update host");
    }

    private String sha256(File file) throws Exception {
        MessageDigest digest = MessageDigest.getInstance("SHA-256");
        InputStream input = new BufferedInputStream(new FileInputStream(file));
        byte[] buffer = new byte[32 * 1024];
        int count;
        try {
            while ((count = input.read(buffer)) != -1) digest.update(buffer, 0, count);
        } finally {
            input.close();
        }
        return hex(digest.digest());
    }

    static int compareVersions(String left, String right) {
        int[] a = numericVersion(left);
        int[] b = numericVersion(right);
        for (int i = 0; i < Math.max(a.length, b.length); i++) {
            int av = i < a.length ? a[i] : 0;
            int bv = i < b.length ? b[i] : 0;
            if (av != bv) return av < bv ? -1 : 1;
        }
        return 0;
    }

    private static int[] numericVersion(String value) {
        String cleaned = cleanVersion(value);
        String[] parts = cleaned.split("\\.");
        int[] result = new int[Math.min(parts.length, 4)];
        for (int i = 0; i < result.length; i++) {
            String digits = parts[i].replaceAll("[^0-9].*$", "");
            try {
                result[i] = digits.isEmpty() ? 0 : Integer.parseInt(digits);
            } catch (NumberFormatException ignored) {
                result[i] = 0;
            }
        }
        return result;
    }

    private static String cleanVersion(String value) {
        String cleaned = value == null ? "0" : value.trim().toLowerCase(Locale.US);
        if (cleaned.startsWith("v")) cleaned = cleaned.substring(1);
        int dash = cleaned.indexOf('-');
        return dash < 0 ? cleaned : cleaned.substring(0, dash);
    }

    private static String normalizeHex(String value) {
        return value == null ? "" : value.replace(":", "").trim().toLowerCase(Locale.US);
    }

    private static String hex(byte[] bytes) {
        StringBuilder result = new StringBuilder(bytes.length * 2);
        for (byte value : bytes) result.append(String.format(Locale.US, "%02x", value & 0xff));
        return result.toString();
    }

    private void publish(final String status, final boolean working) {
        if (stopped) return;
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                if (!stopped) listener.onStatus(status, working);
            }
        });
    }

    private static void deleteQuietly(File file) {
        if (file != null && file.exists() && !file.delete()) {
            Log.w(TAG, "Could not delete " + file.getName());
        }
    }
}
