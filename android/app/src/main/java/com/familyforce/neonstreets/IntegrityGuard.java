package com.familyforce.neonstreets;

import android.content.Context;
import android.content.pm.PackageInfo;
import android.content.pm.PackageManager;
import android.content.pm.Signature;
import android.os.Build;

import java.security.MessageDigest;
import java.util.Locale;

final class IntegrityGuard {
    private IntegrityGuard() {}

    static boolean isTrustedInstall(Context context) {
        if (BuildConfig.DEBUG) return true;
        String expected = normalize(BuildConfig.EXPECTED_CERT_SHA256);
        if (expected.length() != 64) return false;
        try {
            PackageManager manager = context.getPackageManager();
            PackageInfo info;
            Signature[] signatures;
            if (Build.VERSION.SDK_INT >= 28) {
                info = manager.getPackageInfo(context.getPackageName(),
                        PackageManager.GET_SIGNING_CERTIFICATES);
                signatures = info.signingInfo == null ? null
                        : info.signingInfo.getApkContentsSigners();
            } else {
                info = manager.getPackageInfo(context.getPackageName(),
                        PackageManager.GET_SIGNATURES);
                signatures = info.signatures;
            }
            if (signatures == null || signatures.length != 1) return false;
            byte[] digest = MessageDigest.getInstance("SHA-256")
                    .digest(signatures[0].toByteArray());
            return constantTimeEquals(expected, hex(digest));
        } catch (Exception ignored) {
            return false;
        }
    }

    private static String normalize(String value) {
        return value == null ? "" : value.replace(":", "").trim().toLowerCase(Locale.US);
    }

    private static String hex(byte[] value) {
        StringBuilder out = new StringBuilder(value.length * 2);
        for (byte item : value) out.append(String.format(Locale.US, "%02x", item & 0xff));
        return out.toString();
    }

    private static boolean constantTimeEquals(String left, String right) {
        if (left.length() != right.length()) return false;
        int difference = 0;
        for (int i = 0; i < left.length(); i++) difference |= left.charAt(i) ^ right.charAt(i);
        return difference == 0;
    }
}
