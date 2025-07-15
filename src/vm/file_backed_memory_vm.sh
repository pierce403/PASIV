#!/bin/bash
#
# PASIV File-Backed Memory VM
# Launch VM with memory-backend-file for direct DMA attacks
#

VM_NAME="pasiv-file-backed"
MEMORY_SIZE="4G"
MEMORY_FILE="./pasiv_vm_memory.img"
DISK_IMAGE="/var/lib/libvirt/images/pasiv/ubuntu-desktop-vulnerable.qcow2"

echo "🚀 PASIV File-Backed Memory VM Launcher"
echo "========================================"

# Create memory backing file
echo "📁 Creating memory backing file: $MEMORY_FILE"
sudo rm -f "$MEMORY_FILE"
sudo truncate -s "$MEMORY_SIZE" "$MEMORY_FILE"
sudo chmod 666 "$MEMORY_FILE"

echo "✅ Memory file created: $(ls -lh $MEMORY_FILE)"

# Stop existing VM if running
echo "🛑 Stopping existing VM..."
sudo virsh destroy ubuntu-desktop-vulnerable-simple 2>/dev/null || true

echo "🚀 Starting VM with file-backed memory..."

# Launch QEMU with file-backed memory
sudo qemu-system-x86_64 \
    -name "$VM_NAME" \
    -m "$MEMORY_SIZE" \
    -object memory-backend-file,id=pc.ram,size="$MEMORY_SIZE",mem-path="$MEMORY_FILE",share=on \
    -machine pc-q35-9.2,memory-backend=pc.ram \
    -accel kvm \
    -cpu host \
    -smp 2 \
    -drive file="$DISK_IMAGE",format=qcow2,if=virtio \
    -netdev user,id=net0,hostfwd=tcp::2222-:22 \
    -device e1000,netdev=net0 \
    -vga qxl \
    -spice port=5901,addr=127.0.0.1,disable-ticketing=on \
    -device qemu-xhci \
    -device usb-tablet \
    -daemonize \
    -pidfile "./pasiv_vm.pid"

if [ $? -eq 0 ]; then
    echo "✅ VM started successfully!"
    echo "📊 VM Details:"
    echo "   - Name: $VM_NAME"  
    echo "   - Memory: $MEMORY_SIZE"
    echo "   - Memory file: $MEMORY_FILE"
    echo "   - SPICE GUI: localhost:5901"
    echo "   - SSH: localhost:2222"
    echo ""
    echo "🖥️  GUI Access:"
    echo "   - Connect: remote-viewer spice://localhost:5901"
    echo "   - Alternative: virt-viewer spice://localhost:5901"
    echo ""
    echo "🎯 DMA Attack Info:"
    echo "   - Direct memory access: $MEMORY_FILE"
    echo "   - File size: $(ls -lh $MEMORY_FILE | awk '{print $5}')"
    echo "   - Writable by user: $(ls -l $MEMORY_FILE | cut -c1-10)"
    echo ""
    echo "🔥 Ready for file-based DMA attacks!"
else
    echo "❌ Failed to start VM"
    exit 1
fi 