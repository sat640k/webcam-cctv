#!/bin/bash
cd `dirname $0`

# 既に起動していたら、何もせず抜ける
ps ax | grep -v 'grep' | grep 'python3 main.py'
if [ "$?" -eq 0 ]; then
  echo "process exist."
  exit 0
fi

# カメラのUSB接続をリセット
echo "cam initialyze."
CAM_VENDOR_ID=`lsusb | grep 'Logitech, Inc. Webcam C270' | awk '{print $6}' | awk -F':' '{print $1}'`
CAM_PRODUCT_ID=`lsusb | grep 'Logitech, Inc. Webcam C270' | awk '{print $6}' | awk -F':' '{print $2}'`
if [ -z "$CAM_VENDOR_ID" -o -z "$CAM_PRODUCT_ID" ]; then
  echo "no cam, error."
  exit 1
fi
sudo usb_modeswitch -v 0x${CAM_VENDOR_ID} -p 0x${CAM_PRODUCT_ID} --reset-usb

# 監視スクリプト開始
echo "start cam."
python3 main.py

