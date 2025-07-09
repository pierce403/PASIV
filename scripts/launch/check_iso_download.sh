#!/bin/bash

# PASIV - Check Ubuntu ISO Download Progress

ISO_FILE="iso_files/ubuntu-22.04.5-desktop-amd64.iso"
EXPECTED_SIZE="4762707968"  # 4.4GB in bytes

echo "PASIV - Ubuntu ISO Download Status"
echo "=================================="

if pgrep -f "wget.*ubuntu.*iso" > /dev/null; then
    echo "✓ Download is currently running"
    
    if [ -f "$ISO_FILE" ]; then
        CURRENT_SIZE=$(stat -c%s "$ISO_FILE" 2>/dev/null || echo "0")
        PERCENTAGE=$((CURRENT_SIZE * 100 / EXPECTED_SIZE))
        
        echo "📁 File: $ISO_FILE"
        echo "📊 Progress: $PERCENTAGE% ($CURRENT_SIZE / $EXPECTED_SIZE bytes)"
        echo "⏱️  ETA: Check the wget output in the background terminal"
        
        # Show recent download progress
        echo ""
        echo "Recent progress (last few lines of wget):"
        ps aux | grep wget | grep -v grep
    else
        echo "❌ ISO file not found yet"
    fi
else
    if [ -f "$ISO_FILE" ]; then
        CURRENT_SIZE=$(stat -c%s "$ISO_FILE" 2>/dev/null || echo "0")
        
        if [ "$CURRENT_SIZE" = "$EXPECTED_SIZE" ]; then
            echo "✅ Download completed successfully!"
            echo "📁 File: $ISO_FILE"
            echo "📊 Size: $CURRENT_SIZE bytes (4.4GB)"
            echo ""
            echo "Ready to launch VM with: ./scripts/launch/launch_vulnerable_desktop.sh"
        else
            echo "⚠️  Download incomplete or failed"
            echo "📁 File: $ISO_FILE"
            echo "📊 Current size: $CURRENT_SIZE bytes"
            echo "📊 Expected size: $EXPECTED_SIZE bytes"
        fi
    else
        echo "❌ No download found. Start download with:"
        echo "cd iso_files && wget https://releases.ubuntu.com/jammy/ubuntu-22.04.5-desktop-amd64.iso"
    fi
fi 