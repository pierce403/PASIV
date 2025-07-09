#!/bin/bash

# PASIV - Launch Vulnerable Ubuntu Desktop Target
# This script launches an Ubuntu Desktop VM configured for DMA attack testing
# with browser memory analysis capabilities.

set -e  # Exit on any error

# Configuration
VM_NAME="ubuntu-desktop-vulnerable"
VM_MEMORY="4G"  # 4GB RAM for desktop environment + browsers
VM_CORES="2"
DISK_IMAGE="vm_images/ubuntu-desktop-vulnerable.qcow2"
ISO_FILE="iso_files/ubuntu-22.04.5-desktop-amd64.iso"
SHARED_MEMORY_FILE="/dev/shm/pasiv_vulnerable_memory"
SHARED_MEMORY_SIZE="4G"
SSH_PORT="2222"
VNC_PORT="5901"
QMP_SOCKET="/tmp/pasiv_vulnerable_qmp.sock"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}PASIV - Launching Vulnerable Ubuntu Desktop Target${NC}"
echo "=================================================="

# Check if QEMU is installed
if ! command -v qemu-system-x86_64 &> /dev/null; then
    echo -e "${RED}Error: qemu-system-x86_64 not found. Please install QEMU.${NC}"
    exit 1
fi

# Check if disk image exists
if [ ! -f "$DISK_IMAGE" ]; then
    echo -e "${RED}Error: VM disk image not found: $DISK_IMAGE${NC}"
    echo "Run this from the PASIV project root directory."
    exit 1
fi

# Check if we're doing initial installation (ISO exists) or booting existing VM
BOOT_FROM_ISO=""
if [ -f "$ISO_FILE" ]; then
    echo -e "${YELLOW}ISO file found - will boot from ISO for installation${NC}"
    BOOT_FROM_ISO="-cdrom $ISO_FILE -boot d"
else
    echo -e "${YELLOW}No ISO file - booting existing installation${NC}"
fi

# Create shared memory file for DMA attacks
echo -e "${GREEN}Setting up shared memory file: $SHARED_MEMORY_FILE${NC}"
rm -f "$SHARED_MEMORY_FILE"  # Remove if exists
fallocate -l "$SHARED_MEMORY_SIZE" "$SHARED_MEMORY_FILE"
chmod 666 "$SHARED_MEMORY_FILE"

# Remove existing QMP socket
rm -f "$QMP_SOCKET"

echo -e "${GREEN}VM Configuration:${NC}"
echo "  Name: $VM_NAME"
echo "  Memory: $VM_MEMORY"
echo "  CPU Cores: $VM_CORES"
echo "  Disk: $DISK_IMAGE"
echo "  Shared Memory: $SHARED_MEMORY_FILE ($SHARED_MEMORY_SIZE)"
echo "  SSH Port: localhost:$SSH_PORT"
echo "  VNC Display: localhost:$VNC_PORT"
echo "  QMP Socket: $QMP_SOCKET"
echo ""

echo -e "${YELLOW}Security Configuration (VULNERABLE):${NC}"
echo "  ✗ KASLR disabled (nokaslr kernel parameter)"
echo "  ✗ IOMMU disabled (no memory protection)"
echo "  ✗ Shared memory accessible to host"
echo "  ✗ Direct memory access enabled"
echo ""

echo -e "${RED}WARNING: This VM is intentionally vulnerable for research purposes!${NC}"
echo -e "${RED}Only use in isolated testing environments.${NC}"
echo ""

# Construct kernel command line arguments for vulnerability
KERNEL_ARGS="nokaslr nosmap nosmep mds=off l1tf=off spectre_v2=off spec_store_bypass_disable=off"

echo -e "${GREEN}Starting QEMU...${NC}"
echo "Use Ctrl+Alt+G to release mouse cursor from QEMU window"
echo "VNC available at: localhost:$VNC_PORT"
echo "SSH will be available at: ssh -p $SSH_PORT username@localhost"
echo ""

# Launch QEMU with vulnerable configuration
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
    -vga std \
    -vnc ":1" \
    -monitor qmp:unix:"$QMP_SOCKET",server,nowait \
    -append "$KERNEL_ARGS" \
    -name "$VM_NAME" \
    -daemonize

echo -e "${GREEN}VM launched successfully!${NC}"
echo ""
echo "Next steps:"
echo "1. Connect via VNC to localhost:$VNC_PORT to complete Ubuntu installation"
echo "2. During installation, configure a user account for SSH access"
echo "3. After installation, SSH access will be available at port $SSH_PORT"
echo "4. Install browsers (Firefox, Chrome) for memory attack testing"
echo "5. Shared memory file $SHARED_MEMORY_FILE is ready for DMA analysis tools"
echo ""
echo "To stop the VM: pkill -f \"$VM_NAME\""
echo "To monitor QMP: echo '{\"execute\":\"query-status\"}' | socat - unix:$QMP_SOCKET" 