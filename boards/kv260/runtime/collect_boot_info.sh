#!/usr/bin/env bash
set -eu

echo "FPGA_FLYBRAIN_LAB=LAB-HW-05"
echo "=== uname ==="
uname -a

echo "=== os-release ==="
cat /etc/os-release

echo "=== device-tree model ==="
tr -d '\000' </proc/device-tree/model
printf '\n'

echo "=== xmutil boardid ==="
if command -v xmutil >/dev/null 2>&1; then
  sudo xmutil boardid
else
  echo "ERROR=XMUTIL_NOT_FOUND"
fi

echo "=== xmutil bootfw_status ==="
if command -v xmutil >/dev/null 2>&1; then
  sudo xmutil bootfw_status
else
  echo "ERROR=XMUTIL_NOT_FOUND"
fi
