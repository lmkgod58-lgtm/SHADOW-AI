#!/bin/bash
# GhostFrame v2 — APK Builder
# Run this INSIDE UserLAnd Ubuntu (after setup_userland.sh)

source ~/ghostframe-venv/bin/activate

mkdir -p ~/ghostframe-apk
cp -r /sdcard/Download/ghostframe-chat-v2/frontend/* ~/ghostframe-apk/
cd ~/ghostframe-apk

echo "[ IMPORTANT ] Edit main.py and set your BACKEND_URL:"
echo "    nano ~/ghostframe-apk/main.py"
echo "    Find: BACKEND_URL = "https://your-app.up.railway.app""
echo "    Replace with your actual Railway URL"
echo ""
read -p "Press ENTER after you have edited BACKEND_URL..."

echo "[ Building APK — first build takes 20-40 minutes ]"
buildozer android debug

echo ""
echo "[ DONE ] APK location:"
ls -la ~/ghostframe-apk/bin/*.apk
echo ""
echo "Install on Android:"
echo "    cp ~/ghostframe-apk/bin/*.apk /sdcard/Download/"
echo "    Then install from Downloads app"
