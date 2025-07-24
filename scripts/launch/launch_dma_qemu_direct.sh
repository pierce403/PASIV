#!/bin/bash

# PASIV - Direct QEMU Launch with File-Backed Memory for DMA
# This script launches the VM with memory directly accessible via file

set -e

# Configuration
VM_NAME="pasiv-dma-vm"
VM_MEMORY="4G"
VM_CORES="2"
DISK_IMAGE="/var/lib/libvirt/images/pasiv/ubuntu-desktop-vulnerable.qcow2"
MEMORY_FILE="/tmp/pasiv_vm_memory.raw"  # Use /tmp for easier access
SSH_PORT="2222"
VNC_PORT="5901"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}PASIV - Direct QEMU with File-Backed Memory${NC}"
echo "=============================================="

# Check if disk image exists
if [ ! -f "$DISK_IMAGE" ]; then
    echo -e "${RED}Error: VM disk image not found: $DISK_IMAGE${NC}"
    exit 1
fi

# Create memory file (4GB)
echo -e "${GREEN}Creating memory file: $MEMORY_FILE${NC}"
rm -f "$MEMORY_FILE"
fallocate -l 4G "$MEMORY_FILE"
chmod 666 "$MEMORY_FILE"

echo -e "${GREEN}VM Configuration:${NC}"
echo "  Memory: $VM_MEMORY"
echo "  CPU Cores: $VM_CORES"  
echo "  Disk: $DISK_IMAGE"
echo "  Memory File: $MEMORY_FILE"
echo "  SSH Port: localhost:$SSH_PORT"
echo "  VNC Port: localhost:$VNC_PORT"
echo ""

echo -e "${YELLOW}DMA Configuration:${NC}"
echo "  ✓ File-backed memory: $MEMORY_FILE"
echo "  ✓ Memory sharing enabled"
echo "  ✓ Direct memory access for attacks"
echo ""

echo -e "${RED}Starting QEMU with DMA-accessible memory...${NC}"

# Launch QEMU with proper file-backed memory
exec qemu-system-x86_64 \
    -enable-kvm \
    -m "$VM_MEMORY" \
    -smp "$VM_CORES" \
    -drive file="$DISK_IMAGE",format=qcow2 \
    -object memory-backend-file,id=mem,size="$VM_MEMORY",mem-path="$MEMORY_FILE",share=on \
    -numa node,memdev=mem \
    -netdev user,id=net0,hostfwd=tcp::${SSH_PORT}-:22 \
    -device e1000,netdev=net0 \
    -vga std \
    -display gtk,show-cursor=on \
    -vnc ":1" \
    -name "$VM_NAME" 