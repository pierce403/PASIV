#!/usr/bin/env python3
"""
PASIV MetaMask Live Memory Scanner
Find all MetaMask-related text in running VM memory for DMA attack targets
"""

import os
import re
import sys
import subprocess

class MetaMaskLiveScanner:
    def __init__(self):
        self.vm_process = None
        self.metamask_strings = []
        
    def find_vm_process(self):
        """Find the running QEMU VM process"""
        try:
            result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if 'qemu-system-x86_64' in line and 'ubuntu-desktop-vulnerable' in line:
                    parts = line.split()
                    self.vm_process = {
                        'pid': int(parts[1]),
                        'user': parts[0]
                    }
                    return True
            return False
        except Exception as e:
            print(f"❌ Error finding VM process: {e}")
            return False
    
    def scan_for_metamask_strings(self):
        """Scan VM memory for MetaMask-related strings"""
        if not self.vm_process:
            return False
            
        pid = self.vm_process['pid']
        print(f"🔍 Scanning VM memory for MetaMask strings...")
        
        # MetaMask keywords to search for
        search_terms = [
            'MetaMask', 'metamask', 'METAMASK',
            'Welcome', 'welcome', 'WELCOME',
            'Wallet', 'wallet', 'WALLET',
            'Extension', 'extension',
            'Ethereum', 'ethereum', 'ETH',
            'Connect', 'connect', 'CONNECT',
            'Account', 'account', 'ACCOUNT',
            'Transaction', 'transaction',
            'Password', 'password', 'PASSWORD',
            'Unlock', 'unlock', 'UNLOCK',
            'Security', 'security', 'SECURITY'
        ]
        
        try:
            # Read memory maps
            with open(f'/proc/{pid}/maps', 'r') as f:
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
            
            # Search for MetaMask strings
            found_strings = {}
            with open(f'/proc/{pid}/mem', 'rb') as mem_file:
                for start_addr, end_addr, size, perms in memory_regions[:30]:
                    try:
                        mem_file.seek(start_addr)
                        data = mem_file.read(size)
                        
                        # Search for each term
                        for term in search_terms:
                            pattern = term.encode('utf-8')
                            offset = 0
                            while True:
                                pos = data.find(pattern, offset)
                                if pos == -1:
                                    break
                                actual_addr = start_addr + pos
                                
                                # Extract context around the found string
                                context_start = max(0, pos - 50)
                                context_end = min(len(data), pos + len(pattern) + 50)
                                context = data[context_start:context_end]
                                
                                found_strings[actual_addr] = {
                                    'term': term,
                                    'address': actual_addr,
                                    'perms': perms,
                                    'context': context.decode('utf-8', errors='ignore')
                                }
                                
                                offset = pos + 1
                                
                    except (OSError, PermissionError):
                        continue
                        
            self.metamask_strings = list(found_strings.values())
            return len(self.metamask_strings) > 0
            
        except Exception as e:
            print(f"❌ Error scanning memory: {e}")
            return False
    
    def display_findings(self):
        """Display all found MetaMask-related strings"""
        if not self.metamask_strings:
            print("❌ No MetaMask strings found")
            return
            
        print(f"\n🎯 Found {len(self.metamask_strings)} MetaMask-related strings:")
        print("=" * 80)
        
        # Group by search term
        by_term = {}
        for finding in self.metamask_strings:
            term = finding['term']
            if term not in by_term:
                by_term[term] = []
            by_term[term].append(finding)
            
        for term, findings in by_term.items():
            print(f"\n🔍 '{term}' ({len(findings)} instances):")
            for finding in findings[:5]:  # Show first 5 of each
                addr = finding['address']
                perms = finding['perms']
                context = finding['context'].replace('\n', '\\n')[:100]
                print(f"  📍 0x{addr:x} ({perms}): ...{context}...")
            if len(findings) > 5:
                print(f"  ... and {len(findings) - 5} more instances")
    
    def suggest_targets(self):
        """Suggest good targets for memory modification"""
        if not self.metamask_strings:
            return
            
        print(f"\n🎯 SUGGESTED ATTACK TARGETS:")
        print("=" * 50)
        
        # Look for writable strings
        writable = [s for s in self.metamask_strings if 'w' in s['perms']]
        if writable:
            print(f"✅ WRITABLE TARGETS ({len(writable)} found):")
            for target in writable[:10]:
                print(f"  🎯 0x{target['address']:x}: '{target['term']}' → Can modify!")
        
        # Look for specific UI strings
        ui_terms = ['Welcome', 'Unlock', 'Connect', 'Account', 'Security']
        ui_targets = [s for s in self.metamask_strings if s['term'] in ui_terms]
        if ui_targets:
            print(f"\n🖥️  UI TEXT TARGETS ({len(ui_targets)} found):")
            for target in ui_targets[:10]:
                print(f"  🎯 0x{target['address']:x} ({target['perms']}): '{target['term']}'")
    
    def run_scan(self):
        """Execute the complete MetaMask memory scan"""
        print("🦊 PASIV MetaMask Live Memory Scanner")
        print("=" * 50)
        
        # Find VM process
        print("🔍 Finding VM process...")
        if not self.find_vm_process():
            print("❌ No running VM found")
            return False
            
        print(f"✅ Found VM: PID {self.vm_process['pid']}")
        
        # Scan for MetaMask strings
        if not self.scan_for_metamask_strings():
            print("❌ No MetaMask strings found")
            return False
            
        # Display results
        self.display_findings()
        self.suggest_targets()
        
        return True

def main():
    if os.geteuid() != 0:
        print("❌ Root privileges required for memory access")
        return 1
        
    scanner = MetaMaskLiveScanner()
    scanner.run_scan()
    return 0

if __name__ == "__main__":
    sys.exit(main()) 