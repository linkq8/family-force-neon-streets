# In-game GitHub updater — request223

The Unity main menu opens a non-exported native Android activity. It checks the
public `linkq8/family-force-neon-streets` release list, including pre-releases.
No login, token, paid service, browser, or background polling is used.

## Publishing contract for all future Unity APK releases

- Tag: `unity-vMAJOR.MINOR.PATCH-description`. Increment the numeric version.
- APK: `FamilyForceUnity*.apk`, uploaded to that tag, with GitHub's SHA-256 digest.
- Keep package `com.familyforce.neonstreets.unityprototype` and the same signing key.
- Increment Android versionCode; versionName must start with the tag's same numeric version.
- Do not publish QA probes. Releases for the legacy Android engine are excluded.

The updater chooses the highest semantic version, not upload order. Equal versions
are not reinstalled. It scans at most 1,000 releases and reports an error if exhausted.
Missing digest or mismatched asset naming is ineligible, never silently trusted.

## Download/install behavior

User checks, reviews version/size, chooses Download, then Install. Downloads remain
in private cache, are bounded by announced size and SHA-256, and are checked for
package ID, greater Android versionCode, matching versionName and signing certificate.
Only HTTPS and GitHub's specific release/CDN hosts are allowed. TLS verification
is the platform default. A read-only non-exported provider shares exactly one file
with the Android installer via a temporary URI permission; no storage permission.

Android 8+ may require the user to allow installations from this game. Returning
from Settings restores the Install button. Installation remains user-confirmed.
Back cancels an active download. Process death/cancel means retry from the start;
this is not a resumable background downloader. Existing app data is not cleared.
Devices with policy/Advanced Protection restrictions may refuse side-loaded updates.
This direct-distribution test build is not a Play Store update implementation.

## Build and test

Run `unity/tools/build_android_updater.py` before Unity build if Java/manifest changes.
It builds `Assets/Plugins/Android/FamilyForceUpdater.aar` using the installed SDK/JDK,
without third-party dependencies. Then execute `BuildFamilyForce.BuildUpdaterRelease`.

`build_updater_test_probe.py` creates a **LOCAL-ONLY** same-package v0.5.4 probe in
Builds/Updater223 for disposable-emulator testing. It contains the production updater
plus 15 instrumentation assertions, no Unity game. Never install on the user's phone
or upload it. Start instrumentation with `am instrument -w
com.familyforce.neonstreets.unityprototype/com.familyforce.updates.PolicyTests`.
After the real release exists, the probe can test its actual download and installation.

References: [GitHub releases API](https://docs.github.com/en/rest/releases/releases),
[Android package installation permission](https://developer.android.com/reference/android/content/pm/PackageManager#canRequestPackageInstalls()),
[Unity AAR plug-ins](https://docs.unity3d.com/6000.0/Documentation/Manual/AndroidAARPlugins.html).

## UI boundary

Local extension of the game's existing gold/midnight menu, not the commercial-guide
web design system. Native text and buttons support font scaling, keyboard/D-pad and
scrolling in portrait/landscape. No new character art, motion, or gameplay changes.
