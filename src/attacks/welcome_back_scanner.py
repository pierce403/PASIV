#!/usr/bin/env python3
"""
PASIV Welcome Back Scanner
Simple scanner to find all instances of "Welcome back" in VM memory
"""

import os
import sys
import subprocess

class WelcomeBackScanner:
    def __init__(self):
        self.vm_process = None
        self.targets_found = []
        
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
    
    def scan_for_welcome_back(self):
        """Scan all memory for 'Welcome back' strings"""
        search_patterns = [
            "Welcome back",
            "Welcome Back", 
            "WELCOME BACK",
            "welcome back",
            b"Welcome back",
            b"Welcome Back",
            b"WELCOME BACK", 
            b"welcome back"
        ]
        
        try:
            # Read memory maps
            with open(f'/proc/{self.vm_process}/maps', 'r') as f:
                maps = f.read()
                
            # Parse ALL memory regions (readable)
            memory_regions = []
            for line in maps.split('\n'):
                if line.strip() and ('r-' in line or 'rw' in line):
                    parts = line.split()
                    if len(parts) >= 2:
                        addr_range = parts[0]
                        perms = parts[1]
                        if '-' in addr_range:
                            start_str, end_str = addr_range.split('-')
                            start_addr = int(start_str, 16)
                            end_addr = int(end_str, 16)
                            size = end_addr - start_addr
                            # Include all reasonable regions
                            if 512 < size < 100 * 1024 * 1024:  # 512B to 100MB
                                memory_regions.append((start_addr, end_addr, size, perms))
            
            print(f"🔍 Scanning {len(memory_regions)} memory regions for 'Welcome back'...")
            
            # Search for "Welcome back" in all regions
            found_locations = []
            with open(f'/proc/{self.vm_process}/mem', 'rb') as mem_file:
                for i, (start_addr, end_addr, size, perms) in enumerate(memory_regions):
                    try:
                        print(f"   Scanning region {i+1}/{len(memory_regions)}: 0x{start_addr:x}-0x{end_addr:x} ({perms})")
                        
                        mem_file.seek(start_addr)
                        data = mem_file.read(size)
                        
                        # Check each pattern
                        for pattern in search_patterns:
                            if isinstance(pattern, str):
                                pattern_bytes = pattern.encode('utf-8')
                            else:
                                pattern_bytes = pattern
                                
                            offset = 0
                            while True:
                                pos = data.find(pattern_bytes, offset)
                                if pos == -1:
                                    break
                                    
                                actual_addr = start_addr + pos
                                
                                # Extract context around the found string
                                context_start = max(0, pos - 30)
                                context_end = min(len(data), pos + len(pattern_bytes) + 30)
                                context = data[context_start:context_end]
                                
                                found_info = {
                                    'address': actual_addr,
                                    'permissions': perms,
                                    'pattern': pattern if isinstance(pattern, str) else pattern.decode('utf-8', errors='ignore'),
                                    'context': context.decode('utf-8', errors='ignore'),
                                    'region_start': start_addr,
                                    'region_size': size
                                }
                                
                                found_locations.append(found_info)
                                print(f"      🎯 FOUND at 0x{actual_addr:x}: '{pattern}' ({perms})")
                                
                                offset = pos + 1
                                
                    except (OSError, PermissionError) as e:
                        print(f"      ❌ Cannot read region: {e}")
                        continue
                        
            self.targets_found = found_locations
            return len(found_locations) > 0
            
        except Exception as e:
            print(f"❌ Error during scan: {e}")
            return False
    
    def display_results(self):
        """Display all found targets with details"""
        if not self.targets_found:
            print("\n❌ No 'Welcome back' strings found in VM memory")
            return
            
        print(f"\n🎯 FOUND {len(self.targets_found)} 'Welcome back' targets:")
        print("=" * 80)
        
        for i, target in enumerate(self.targets_found, 1):
            addr = target['address']
            perms = target['permissions']
            pattern = target['pattern']
            context = target['context'].replace('\n', '\\n')
            writable = "✅ WRITABLE" if 'w' in perms else "❌ READ-ONLY"
            
            print(f"\n{i}. Target at 0x{addr:x}")
            print(f"   Pattern: '{pattern}'")
            print(f"   Permissions: {perms} {writable}")
            print(f"   Context: ...{context[:60]}...")
            print(f"   Region: 0x{target['region_start']:x} (size: {target['region_size']} bytes)")
    
    def run_scan(self):
        """Execute the Welcome back scan"""
        print("🔍 PASIV Welcome Back Scanner")
        print("=" * 50)
        
        # Find VM process
        print("🔍 Finding VM process...")
        if not self.find_vm_process():
            print("❌ No running VM found")
            return False
            
        print(f"✅ Found VM process: PID {self.vm_process}")
        
        # Scan for Welcome back
        print(f"\n🔍 Scanning VM memory for 'Welcome back'...")
        if not self.scan_for_welcome_back():
            print("❌ No 'Welcome back' strings found")
            return False
            
        # Display results
        self.display_results()
        
        return True

def main():
    if os.geteuid() != 0:
        print("❌ Root privileges required for memory access")
        return 1
        
    scanner = WelcomeBackScanner()
    scanner.run_scan()
    return 0

if __name__ == "__main__":
    sys.exit(main()) 