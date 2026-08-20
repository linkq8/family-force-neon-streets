#!/bin/sh
set -eu

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
ANDROID_PROJECT=$(CDPATH= cd -- "$SCRIPT_DIR/.." && pwd)
WORKSPACE=$(CDPATH= cd -- "$ANDROID_PROJECT/.." && pwd)
PACK=${1:-"$WORKSPACE/customers/family-current"}
PACK=$(CDPATH= cd -- "$PACK" && pwd)
DELIVERY_MODE=${2:-draft}
if [ "$DELIVERY_MODE" != "draft" ] && [ "$DELIVERY_MODE" != "--delivery" ]; then
    echo "Usage: $0 [customer-pack] [--delivery]" >&2
    exit 2
fi

export JAVA_HOME=${JAVA_HOME:-/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home}
export ANDROID_HOME=${ANDROID_HOME:-/Users/essa/Library/Android/sdk}
export ANDROID_SDK_ROOT=${ANDROID_SDK_ROOT:-$ANDROID_HOME}
export FF_RELEASE_KEYSTORE=${FF_RELEASE_KEYSTORE:-"$HOME/.family-force-release/family-force-release.jks"}
export FF_RELEASE_KEY_ALIAS=${FF_RELEASE_KEY_ALIAS:-family-force-release}

python3 "$SCRIPT_DIR/validate_customer_pack.py" "$PACK"
if [ "$DELIVERY_MODE" = "--delivery" ]; then
    python3 "$SCRIPT_DIR/validate_customer_order.py" --delivery "$PACK"
else
    python3 "$SCRIPT_DIR/validate_customer_order.py" "$PACK"
fi
python3 "$SCRIPT_DIR/prepare_customer_icon.py" "$PACK"
python3 "$SCRIPT_DIR/validate_assets.py"
python3 "$SCRIPT_DIR/validate_animation_atlases.py" --allow-nonclustered \
    --assets "$ANDROID_PROJECT/app/src/main/assets"

ORDER_ID=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["orderId"])' "$PACK/customer.json")
SAFE_ID=$(printf '%s' "$ORDER_ID" | tr -cd 'a-z0-9')
test -n "$SAFE_ID"
APPLICATION_ID="com.familyforce.neonstreets.event.$SAFE_ID"

if [ -z "${FF_RELEASE_STORE_PASSWORD:-}" ]; then
    FF_RELEASE_STORE_PASSWORD=$(security find-generic-password -a "$USER" -s family-force-release-store -w)
    export FF_RELEASE_STORE_PASSWORD
fi
if [ -z "${FF_RELEASE_KEY_PASSWORD:-}" ]; then
    FF_RELEASE_KEY_PASSWORD=$(security find-generic-password -a "$USER" -s family-force-release-key -w)
    export FF_RELEASE_KEY_PASSWORD
fi

CERT_SHA=$($JAVA_HOME/bin/keytool -exportcert -alias "$FF_RELEASE_KEY_ALIAS" \
    -keystore "$FF_RELEASE_KEYSTORE" -storepass "$FF_RELEASE_STORE_PASSWORD" \
    | shasum -a 256 | awk '{print $1}')

"$ANDROID_PROJECT/gradlew" --no-daemon -p "$ANDROID_PROJECT" clean \
    :app:assembleRelease :app:lintRelease \
    -PcustomerPack="$PACK" -PcustomerId="$ORDER_ID" \
    -PcustomerApplicationId="$APPLICATION_ID" \
    -PexpectedCertificateSha256="$CERT_SHA"

SOURCE_APK="$ANDROID_PROJECT/app/build/outputs/apk/release/app-release.apk"
OUTPUT_DIR="$WORKSPACE/dist/customers/$ORDER_ID"
OUTPUT_APK="$OUTPUT_DIR/family-force-$ORDER_ID.apk"
test -f "$SOURCE_APK"
mkdir -p "$OUTPUT_DIR"
cp "$SOURCE_APK" "$OUTPUT_APK"

APKSIGNER="$ANDROID_HOME/build-tools/34.0.0/apksigner"
"$APKSIGNER" verify --verbose --print-certs "$OUTPUT_APK" > "$OUTPUT_DIR/signature-report.txt"
APK_SHA=$(shasum -a 256 "$OUTPUT_APK" | awk '{print $1}')
printf '%s  %s\n' "$APK_SHA" "$(basename "$OUTPUT_APK")" > "$OUTPUT_DIR/SHA256SUMS.txt"
cp "$PACK/customer.json" "$OUTPUT_DIR/customer.json"

python3 "$SCRIPT_DIR/verify_customer_apk.py" --apk "$OUTPUT_APK" --pack "$PACK" \
    --aapt "$ANDROID_HOME/build-tools/34.0.0/aapt" \
    --report "$OUTPUT_DIR/apk-verification.json"

echo "APK: $OUTPUT_APK"
echo "SHA-256: $APK_SHA"
echo "Package: $APPLICATION_ID"
echo "Mode: $DELIVERY_MODE"
