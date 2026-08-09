#!/bin/bash
# GhostFrame v2 — UserLAnd Ubuntu Environment Setup
# Run this INSIDE UserLAnd Ubuntu terminal

echo "[ GhostFrame Setup — UserLAnd ]"
sudo apt update && sudo apt upgrade -y

# Core build dependencies
sudo apt install -y     python3-pip python3-venv git zip unzip     openjdk-17-jdk autoconf libtool pkg-config     zlib1g-dev libncurses5-dev libffi-dev libssl-dev     cmake libsqlite3-dev

# Python virtual environment
python3 -m venv ~/ghostframe-venv
source ~/ghostframe-venv/bin/activate

pip install --upgrade pip
pip install buildozer cython kivy

echo ""
echo "[ DONE ] Environment ready."
echo "Next: Copy frontend files and run build_apk.sh"
