#!/usr/bin/env python3
"""
PASIV Password Scanner
Find "Enter password" strings in VM memory for DMA attack targeting
"""

import os
import sys
import subprocess

class PasswordScanner:
    def __init__(self):
        self.vm_process = None
        self.password_targets = []
        
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
    
    def scan_for_password_strings(self):
        """Scan VM memory for password-related strings"""
        if not self.vm_process:
            return False
            
        print(f"🔍 Scanning VM memory for password strings...")
        
        # Password-related search terms
        search_terms = [
            'Enter password',
            'Enter Password', 
            'ENTER PASSWORD',
            'enter password',
            'Password:',
            'password:',
            'PASSWORD:',
            'Type password',
            'Input password',
            'Login password'
        ]
        
        try:
            # Read memory maps
            with open(f'/proc/{self.vm_process}/maps', 'r') as f:
                maps = f.read()
                
            # Parse memory regions 
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
                            if 1024 < size < 50 * 1024 * 1024:  # 1KB to 50MB
                                memory_regions.append((start_addr, end_addr, size, perms))
            
            print(f"📍 Scanning {len(memory_regions)} memory regions...")
            
            # Search for password strings
            found_targets = {}
            with open(f'/proc/{self.vm_process}/mem', 'rb') as mem_file:
                for start_addr, end_addr, size, perms in memory_regions[:40]:
                    try:
                        mem_file.seek(start_addr)
                        data = mem_file.read(size)
                        
                        # Search for each term
                        for term in search_terms:
                            # Try different encodings
                            patterns = [
                                term.encode('utf-8'),
                                term.encode('utf-16le'),
                                term.encode('utf-16be'),
                                f'"{term}"'.encode('utf-8'),
                                f"'{term}'".encode('utf-8')
                            ]
                            
                            for pattern in patterns:
                                offset = 0
                                while True:
                                    pos = data.find(pattern, offset)
                                    if pos == -1:
                                        break
                                    actual_addr = start_addr + pos
                                    
                                    # Extract context around the found string
                                    context_start = max(0, pos - 30)
                                    context_end = min(len(data), pos + len(pattern) + 30)
                                    context = data[context_start:context_end]
                                    
                                    found_targets[actual_addr] = {
                                        'term': term,
                                        'address': actual_addr,
                                        'perms': perms,
                                        'context': context.decode('utf-8', errors='ignore'),
                                        'original_length': len(term)
                                    }
                                    
                                    offset = pos + 1
                                    
                    except (OSError, PermissionError):
                        continue
                        
            self.password_targets = list(found_targets.values())
            return len(self.password_targets) > 0
            
        except Exception as e:
            print(f"❌ Error scanning memory: {e}")
            return False
    
    def display_targets(self):
        """Display found password targets"""
        if not self.password_targets:
            print("❌ No password strings found")
            return
            
        print(f"\n🎯 Found {len(self.password_targets)} password-related strings:")
        print("=" * 80)
        
        # Group by search term
        by_term = {}
        for target in self.password_targets:
            term = target['term']
            if term not in by_term:
                by_term[term] = []
            by_term[term].append(target)
            
        for term, targets in by_term.items():
            print(f"\n🔍 '{term}' ({len(targets)} instances):")
            for target in targets[:3]:  # Show first 3 of each
                addr = target['address']
                perms = target['perms']
                context = target['context'].replace('\n', '\\n')[:80]
                writable = "✅ WRITABLE" if 'w' in perms else "❌ READ-ONLY"
                print(f"  📍 0x{addr:x} ({perms}) {writable}: ...{context}...")
            if len(targets) > 3:
                print(f"  ... and {len(targets) - 3} more instances")
    
    def get_writable_targets(self):
        """Get targets that can be modified"""
        return [t for t in self.password_targets if 'w' in t['perms']]
    
    def run_scan(self):
        """Execute the password string scan"""
        print("🔐 PASIV Password String Scanner")
        print("=" * 50)
        
        # Find VM process
        print("🔍 Finding VM process...")
        if not self.find_vm_process():
            print("❌ No running VM found")
            return False
            
        print(f"✅ Found VM: PID {self.vm_process}")
        
        # Scan for password strings
        if not self.scan_for_password_strings():
            print("❌ No password strings found")
            return False
            
        # Display results
        self.display_targets()
        
        # Show writable targets
        writable = self.get_writable_targets()
        if writable:
            print(f"\n🎯 ATTACK TARGETS ({len(writable)} writable):")
            print("=" * 50)
            for target in writable[:10]:
                print(f"🎯 0x{target['address']:x}: '{target['term']}' → Ready for modification!")
        
        return True

def main():
    if os.geteuid() != 0:
        print("❌ Root privileges required for memory access")
        return 1
        
    scanner = PasswordScanner()
    scanner.run_scan()
    return 0

if __name__ == "__main__":
    sys.exit(main()) 