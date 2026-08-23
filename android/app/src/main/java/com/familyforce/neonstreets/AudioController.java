package com.familyforce.neonstreets;

import android.content.Context;
import android.content.res.AssetFileDescriptor;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.media.SoundPool;

import java.io.IOException;
import java.util.HashMap;
import java.util.Map;

final class AudioController {
    static final String CONFIRM = "confirm";
    static final String PUNCH = "punch";
    static final String DAMAGE = "damage";
    static final String PICKUP = "pickup";
    static final String JUMP = "jump";
    static final String VICTORY = "victory";
    static final String SPECIAL = "special";

    private final Context context;
    private final SoundPool soundPool;
    private final Map<String, Integer> sounds = new HashMap<>();
    private MediaPlayer music;
    private String requestedTrack = "audio/menu.ogg";
    private String playingTrack;
    private String loadingTrack;
    private int musicGeneration;
    private boolean musicEnabled = true;
    private boolean sfxEnabled = true;
    private float musicVolume = 0.52f;
    private float sfxVolume = 0.86f;

    AudioController(Context context) {
        this.context = context.getApplicationContext();
        AudioAttributes attributes = new AudioAttributes.Builder()
                .setUsage(AudioAttributes.USAGE_GAME)
                .setContentType(AudioAttributes.CONTENT_TYPE_SONIFICATION)
                .build();
        soundPool = new SoundPool.Builder()
                .setMaxStreams(8)
                .setAudioAttributes(attributes)
                .build();
        load(CONFIRM, "audio/confirm.wav");
        load(PUNCH, "audio/punch.wav");
        load(DAMAGE, "audio/damage.wav");
        load(PICKUP, "audio/pickup.wav");
        load(JUMP, "audio/jump.wav");
        load(VICTORY, "audio/victory.wav");
        load(SPECIAL, "audio/special.wav");
        for (int stage = 1; stage <= 4; stage++) {
            load("stage_" + stage + "_intro", "audio/stage_" + stage + "_intro.wav");
            load("stage_" + stage + "_clear", "audio/stage_" + stage + "_clear.wav");
        }
    }

    private void load(String id, String path) {
        try (AssetFileDescriptor afd = context.getAssets().openFd(path)) {
            sounds.put(id, soundPool.load(afd, 1));
        } catch (IOException ignored) {
            // Every sound has visual/haptic feedback, so missing optional audio
            // never prevents the game from starting.
        }
    }

    void play(String id) {
        if (!sfxEnabled) return;
        Integer sound = sounds.get(id);
        if (sound != null && sound != 0) {
            soundPool.play(sound, sfxVolume, sfxVolume, 1, 0, 1f);
        }
    }

    void playStageSting(int stage, boolean intro) {
        int safeStage = Math.max(1, Math.min(4, stage));
        play("stage_" + safeStage + (intro ? "_intro" : "_clear"));
    }

    synchronized void ensureMusic(String assetPath) {
        requestedTrack = assetPath;
        if (!musicEnabled) return;
        if ((assetPath.equals(playingTrack) || assetPath.equals(loadingTrack)) && music != null) return;
        releaseMusic();
        startMusic(assetPath);
    }

    private void startMusic(String assetPath) {
        if (!musicEnabled || music != null) return;
        try (AssetFileDescriptor afd = context.getAssets().openFd(assetPath)) {
            MediaPlayer next = new MediaPlayer();
            next.setDataSource(afd.getFileDescriptor(), afd.getStartOffset(), afd.getLength());
            final int generation = ++musicGeneration;
            loadingTrack = assetPath;
            music = next;
            next.setAudioAttributes(new AudioAttributes.Builder()
                    .setUsage(AudioAttributes.USAGE_GAME)
                    .setContentType(AudioAttributes.CONTENT_TYPE_MUSIC)
                    .build());
            next.setLooping(true);
            next.setVolume(musicVolume, musicVolume);
            next.setOnPreparedListener(prepared -> {
                synchronized (AudioController.this) {
                    if (music != prepared || generation != musicGeneration
                            || !assetPath.equals(requestedTrack) || !musicEnabled) {
                        try { prepared.release(); } catch (IllegalStateException ignored) {}
                        if (music == prepared) music = null;
                        return;
                    }
                    try {
                        prepared.start();
                        playingTrack = assetPath;
                        loadingTrack = null;
                    } catch (IllegalStateException error) {
                        releaseMusic();
                    }
                }
            });
            next.setOnErrorListener((failed, what, extra) -> {
                synchronized (AudioController.this) {
                    if (music == failed) releaseMusic();
                }
                return true;
            });
            next.prepareAsync();
        } catch (IOException | IllegalStateException | SecurityException ignored) {
            releaseMusic();
        }
    }

    synchronized void pauseMusic() {
        try {
            if (music != null && music.isPlaying()) music.pause();
        } catch (IllegalStateException ignored) {
            releaseMusic();
        }
    }

    synchronized void resumeMusic() {
        if (!musicEnabled) return;
        try {
            if (music == null) startMusic(requestedTrack);
            else if (!music.isPlaying()) music.start();
        } catch (IllegalStateException ignored) {
            releaseMusic();
            startMusic(requestedTrack);
        }
    }

    synchronized void setMusicEnabled(boolean enabled) {
        musicEnabled = enabled;
        if (enabled) resumeMusic();
        else pauseMusic();
    }

    void setSfxEnabled(boolean enabled) {
        sfxEnabled = enabled;
    }

    boolean isMusicEnabled() {
        return musicEnabled;
    }

    boolean isSfxEnabled() {
        return sfxEnabled;
    }

    synchronized void setMusicVolume(float value) {
        musicVolume = Math.max(0f, Math.min(1f, value));
        try {
            if (music != null) music.setVolume(musicVolume, musicVolume);
        } catch (IllegalStateException ignored) {
            releaseMusic();
        }
    }

    void setSfxVolume(float value) {
        sfxVolume = Math.max(0f, Math.min(1f, value));
    }

    private void releaseMusic() {
        musicGeneration++;
        if (music != null) {
            try {
                music.release();
            } catch (IllegalStateException ignored) {
                // A concurrent platform audio teardown must not close the game.
            }
            music = null;
        }
        playingTrack = null;
        loadingTrack = null;
    }

    synchronized void release() {
        releaseMusic();
        soundPool.release();
    }
}
