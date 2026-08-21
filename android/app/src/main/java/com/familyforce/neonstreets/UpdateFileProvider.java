package com.familyforce.neonstreets;

import android.content.ContentProvider;
import android.content.ContentValues;
import android.content.Context;
import android.database.Cursor;
import android.database.MatrixCursor;
import android.net.Uri;
import android.os.ParcelFileDescriptor;
import android.provider.OpenableColumns;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;

/** Read-only, single-directory provider for an already verified update APK. */
public final class UpdateFileProvider extends ContentProvider {
    private static final String APK_NAME = "family-force-update.apk";

    static Uri uriFor(Context context, File file) {
        if (file == null || !APK_NAME.equals(file.getName())) {
            throw new IllegalArgumentException("Unexpected update file");
        }
        return new Uri.Builder()
                .scheme("content")
                .authority(context.getPackageName() + ".updates")
                .appendPath(APK_NAME)
                .build();
    }

    @Override
    public boolean onCreate() {
        return true;
    }

    @Override
    public String getType(Uri uri) {
        return "application/vnd.android.package-archive";
    }

    @Override
    public ParcelFileDescriptor openFile(Uri uri, String mode) throws FileNotFoundException {
        if (!"r".equals(mode)) throw new FileNotFoundException("Read only");
        File update = resolveVerifiedFile(uri);
        return ParcelFileDescriptor.open(update, ParcelFileDescriptor.MODE_READ_ONLY);
    }

    @Override
    public Cursor query(Uri uri, String[] projection, String selection,
                        String[] selectionArgs, String sortOrder) {
        File update;
        try {
            update = resolveVerifiedFile(uri);
        } catch (FileNotFoundException error) {
            return null;
        }
        String[] columns = projection == null
                ? new String[] { OpenableColumns.DISPLAY_NAME, OpenableColumns.SIZE }
                : projection;
        MatrixCursor cursor = new MatrixCursor(columns, 1);
        Object[] values = new Object[columns.length];
        for (int i = 0; i < columns.length; i++) {
            if (OpenableColumns.DISPLAY_NAME.equals(columns[i])) values[i] = APK_NAME;
            else if (OpenableColumns.SIZE.equals(columns[i])) values[i] = update.length();
        }
        cursor.addRow(values);
        return cursor;
    }

    private File resolveVerifiedFile(Uri uri) throws FileNotFoundException {
        Context context = getContext();
        if (context == null || uri == null || uri.getPathSegments().size() != 1
                || !APK_NAME.equals(uri.getLastPathSegment())) {
            throw new FileNotFoundException("Unknown update URI");
        }
        File directory = new File(context.getCacheDir(), "updates");
        File update = new File(directory, APK_NAME);
        try {
            if (!update.getCanonicalFile().getParentFile().equals(directory.getCanonicalFile())
                    || !update.isFile()) {
                throw new FileNotFoundException("Update unavailable");
            }
        } catch (IOException error) {
            throw new FileNotFoundException("Update path invalid");
        }
        return update;
    }

    @Override
    public Uri insert(Uri uri, ContentValues values) {
        throw new UnsupportedOperationException("Read only");
    }

    @Override
    public int delete(Uri uri, String selection, String[] selectionArgs) {
        throw new UnsupportedOperationException("Read only");
    }

    @Override
    public int update(Uri uri, ContentValues values, String selection, String[] selectionArgs) {
        throw new UnsupportedOperationException("Read only");
    }
}
