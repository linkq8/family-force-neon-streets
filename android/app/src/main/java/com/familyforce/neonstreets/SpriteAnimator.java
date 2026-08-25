package com.familyforce.neonstreets;

import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import android.graphics.Rect;
import android.graphics.RectF;

/**
 * Allocation-free fixed-tick sprite-atlas player.
 *
 * <p>The game simulation runs at 60 Hz. Each clip declares a visual frame
 * rate, and this class advances with an integer accumulator so animation is
 * deterministic and independent of render cadence.</p>
 */
final class SpriteAnimator {
    static final int MIN_CHARACTER_CLIP_FPS = 12;
    private Bitmap atlas;
    private Bitmap[] clips;
    private int columns;
    private int rows;
    private int cellWidth;
    private int cellHeight;
    private int row;
    private int frame;
    private int frameCount;
    private int fps;
    private int accumulator;
    private boolean loop;
    private boolean finished;
    private boolean frameChanged;

    void bind(Bitmap bitmap, int atlasColumns, int atlasRows,
              int atlasCellWidth, int atlasCellHeight) {
        atlas = bitmap;
        clips = null;
        columns = atlasColumns;
        rows = atlasRows;
        cellWidth = atlasCellWidth;
        cellHeight = atlasCellHeight;
        row = frame = accumulator = 0;
        frameCount = Math.max(1, atlasColumns);
        fps = MIN_CHARACTER_CLIP_FPS;
        loop = true;
        finished = false;
        frameChanged = true;
    }

    /** Bind one independently decoded image per action. Every image is one row. */
    void bindClips(Bitmap[] actionClips, int clipColumns,
                   int clipCellWidth, int clipCellHeight) {
        atlas = null;
        clips = actionClips;
        columns = clipColumns;
        rows = actionClips == null ? 0 : actionClips.length;
        cellWidth = clipCellWidth;
        cellHeight = clipCellHeight;
        row = frame = accumulator = 0;
        frameCount = Math.max(1, clipColumns);
        fps = MIN_CHARACTER_CLIP_FPS;
        loop = true;
        finished = false;
        frameChanged = true;
    }

    boolean isBound() {
        Bitmap bitmap = bitmap();
        return bitmap != null && !bitmap.isRecycled()
                && columns > 0 && rows > 0 && cellWidth > 0 && cellHeight > 0;
    }

    Bitmap bitmap() {
        if (clips == null) return atlas;
        return row >= 0 && row < clips.length ? clips[row] : null;
    }

    boolean isBoundTo(Bitmap[] actionClips) {
        return clips == actionClips && isBound();
    }

    float cellAspectRatio() {
        return cellHeight > 0 ? cellWidth / (float) cellHeight : 1f;
    }

    void clear() {
        atlas = null;
        clips = null;
        columns = rows = cellWidth = cellHeight = 0;
        row = frame = accumulator = 0;
        frameCount = 1;
        finished = false;
        frameChanged = false;
    }

    void play(int clipRow, int frames, int clipFps, boolean shouldLoop,
              boolean restart) {
        int safeRow = Math.max(0, Math.min(Math.max(0, rows - 1), clipRow));
        int safeFrames = Math.max(1, Math.min(columns, frames));
        int safeFps = Math.max(MIN_CHARACTER_CLIP_FPS, Math.min(60, clipFps));
        if (!restart && row == safeRow && frameCount == safeFrames
                && fps == safeFps && loop == shouldLoop && !finished) return;
        row = safeRow;
        frameCount = safeFrames;
        fps = safeFps;
        loop = shouldLoop;
        frame = 0;
        accumulator = 0;
        finished = false;
        frameChanged = true;
    }

    void step() {
        frameChanged = false;
        if (!isBound() || finished) return;
        accumulator += fps;
        while (accumulator >= 60) {
            accumulator -= 60;
            int next = frame + 1;
            if (next >= frameCount) {
                if (loop) next = 0;
                else {
                    next = frameCount - 1;
                    finished = true;
                }
            }
            if (next != frame) {
                frame = next;
                frameChanged = true;
            }
            if (finished) break;
        }
    }

    int row() {
        return row;
    }

    int frame() {
        return frame;
    }

    boolean enteredFrame(int target) {
        return frameChanged && frame == target;
    }

    boolean finished() {
        return finished;
    }

    void draw(Canvas canvas, Paint paint, Rect source, RectF destination) {
        if (!isBound()) return;
        int sx = frame * cellWidth;
        int sy = clips == null ? row * cellHeight : 0;
        source.set(sx, sy, sx + cellWidth, sy + cellHeight);
        canvas.drawBitmap(bitmap(), source, destination, paint);
    }
}
