#!/bin/bash

# PASIV - Launch VM in Text Console Mode

set -e

# Configuration
VM_NAME="ubuntu-desktop-vulnerable"
VM_MEMORY="4G"
VM_CORES="2"
DISK_IMAGE="vm_images/ubuntu-desktop-vulnerable.qcow2"
ISO_FILE="iso_files/ubuntu-22.04.5-desktop-amd64.iso"
SHARED_MEMORY_FILE="/dev/shm/pasiv_vulnerable_memory"
SHARED_MEMORY_SIZE="4G"
SSH_PORT="2222"
QMP_SOCKET="/tmp/pasiv_vulnerable_qmp.sock"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}PASIV - Launching VM in Console Mode${NC}"
echo "====================================="

# Check boot type
BOOT_FROM_ISO=""
KERNEL_APPEND=""
if [ -f "$ISO_FILE" ]; then
    echo -e "${YELLOW}ISO file found - will boot from ISO for installation${NC}"
    BOOT_FROM_ISO="-cdrom $ISO_FILE -boot d"
    KERNEL_APPEND=""
else
    echo -e "${YELLOW}No ISO file - booting existing installation${NC}"
    KERNEL_ARGS="nokaslr nosmap nosmep mds=off l1tf=off spectre_v2=off spec_store_bypass_disable=off console=ttyS0"
    KERNEL_APPEND="-append \"$KERNEL_ARGS\""
fi

# Create shared memory file
echo -e "${GREEN}Setting up shared memory file: $SHARED_MEMORY_FILE${NC}"
rm -f "$SHARED_MEMORY_FILE"
fallocate -l "$SHARED_MEMORY_SIZE" "$SHARED_MEMORY_FILE"
chmod 666 "$SHARED_MEMORY_FILE"

# Remove existing QMP socket
rm -f "$QMP_SOCKET"

echo ""
echo -e "${GREEN}Starting VM in console mode...${NC}"
echo -e "${YELLOW}VM will appear in this terminal window${NC}"
echo -e "${RED}To exit QEMU console: Ctrl+A then X${NC}"
echo ""

# Launch QEMU with console display
exec qemu-system-x86_64 \
    -enable-kvm \
    -m "$VM_MEMORY" \
    -smp "$VM_CORES" \
    -drive file="$DISK_IMAGE",format=qcow2 \
    $BOOT_FROM_ISO \
    -object memory-backend-file,id=mem,size="$VM_MEMORY",mem-path="$SHARED_MEMORY_FILE",share=on \
    -numa node,memdev=mem \
    -netdev user,id=net0,hostfwd=tcp::${SSH_PORT}-:22 \
    -device e1000,netdev=net0 \
    -serial stdio \
    -display curses \
    -qmp unix:"$QMP_SOCKET",server,nowait \
    $KERNEL_APPEND \
    -name "$VM_NAME" 