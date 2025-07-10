#!/usr/bin/env python3
"""
PASIV Memory Analysis Tool
Extracts and analyzes process information from VM memory dumps
"""

import re
import subprocess
import sys
from collections import defaultdict, Counter
from pathlib import Path

class MemoryAnalyzer:
    def __init__(self, dump_file):
        self.dump_file = Path(dump_file)
        if not self.dump_file.exists():
            raise FileNotFoundError(f"Memory dump not found: {dump_file}")
        
        self.processes = defaultdict(list)
        self.services = defaultdict(list)
        self.network_info = []
        self.desktop_info = []
        
    def extract_strings(self):
        """Extract strings from memory dump"""
        print(f"📄 Extracting strings from {self.dump_file.name}...")
        try:
            result = subprocess.run(['strings', str(self.dump_file)], 
                                  capture_output=True, text=True, timeout=300)
            return result.stdout.split('\n')
        except subprocess.TimeoutExpired:
            print("⚠️  String extraction timed out - using partial results")
            return []
        except Exception as e:
            print(f"❌ Error extracting strings: {e}")
            return []
    
    def analyze_processes(self, strings_data):
        """Analyze process information from strings"""
        print("🔍 Analyzing process information...")
        
        # Process patterns
        process_patterns = {
            'system_services': [
                r'systemd(?:-\w+)?',
                r'NetworkManager',
                r'gdm',
                r'dbus',
                r'pulseaudio',
                r'chronyd',
                r'rsyslog',
                r'cron',
                r'ssh',
                r'udev'
            ],
            'desktop_environment': [
                r'gnome-\w+',
                r'Xorg',
                r'wayland',
                r'mutter',
                r'gjs',
                r'evolution',
                r'nautilus'
            ],
            'browsers': [
                r'firefox',
                r'chrome',
                r'chromium',
                r'webkit'
            ],
            'shells': [
                r'/bin/bash',
                r'/bin/sh',
                r'/usr/bin/zsh'
            ]
        }
        
        for line in strings_data:
            if not line.strip():
                continue
                
            for category, patterns in process_patterns.items():
                for pattern in patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        self.processes[category].append(line.strip())
    
    def analyze_services(self, strings_data):
        """Analyze systemd and D-Bus services"""
        print("🛠️  Analyzing system services...")
        
        service_patterns = [
            r'org\.freedesktop\.\w+',
            r'systemd-\w+\.service',
            r'\.service$',
            r'org\.gnome\.\w+',
            r'com\.ubuntu\.\w+'
        ]
        
        for line in strings_data:
            for pattern in service_patterns:
                if re.search(pattern, line):
                    self.services['dbus_services'].append(line.strip())
    
    def analyze_network(self, strings_data):
        """Analyze network-related information"""
        print("🌐 Analyzing network information...")
        
        network_patterns = [
            r'NetworkManager',
            r'wifi',
            r'ethernet',
            r'bluetooth',
            r'tcp',
            r'udp',
            r'socket',
            r'ip\s+\d+\.\d+\.\d+\.\d+',
            r'eth\d+',
            r'wlan\d+'
        ]
        
        for line in strings_data:
            for pattern in network_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    self.network_info.append(line.strip())
    
    def analyze_desktop(self, strings_data):
        """Analyze desktop environment information"""
        print("🖥️  Analyzing desktop environment...")
        
        desktop_patterns = [
            r'\.desktop$',
            r'gnome',
            r'gtk',
            r'wayland',
            r'x11',
            r'themes',
            r'icons'
        ]
        
        for line in strings_data:
            for pattern in desktop_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    if len(line.strip()) < 200:  # Avoid very long lines
                        self.desktop_info.append(line.strip())
    
    def generate_report(self):
        """Generate a comprehensive analysis report"""
        print("\n" + "="*60)
        print("🚀 PASIV MEMORY ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n📊 DUMP FILE: {self.dump_file.name}")
        print(f"📏 SIZE: {self.dump_file.stat().st_size / (1024**3):.2f} GB")
        
        # Process Summary
        print("\n🔧 PROCESS ANALYSIS")
        print("-" * 30)
        for category, items in self.processes.items():
            if items:
                unique_items = list(set(items))[:10]  # Top 10 unique
                print(f"\n{category.upper().replace('_', ' ')}:")
                for item in unique_items:
                    print(f"  • {item}")
        
        # Services Summary  
        print("\n🛠️  SYSTEM SERVICES")
        print("-" * 30)
        if self.services['dbus_services']:
            unique_services = list(set(self.services['dbus_services']))[:15]
            for service in unique_services:
                print(f"  • {service}")
        
        # Network Summary
        print("\n🌐 NETWORK INFORMATION")
        print("-" * 30)
        if self.network_info:
            unique_network = list(set(self.network_info))[:10]
            for info in unique_network:
                print(f"  • {info}")
        
        # Desktop Summary
        print("\n🖥️  DESKTOP ENVIRONMENT")
        print("-" * 30)
        if self.desktop_info:
            unique_desktop = list(set(self.desktop_info))[:10]
            for info in unique_desktop:
                print(f"  • {info}")
        
        # Statistics
        total_strings = sum(len(items) for items in self.processes.values())
        total_services = len(self.services.get('dbus_services', []))
        
        print(f"\n📈 STATISTICS")
        print("-" * 30)
        print(f"  • Total Process References: {total_strings}")
        print(f"  • System Services Found: {total_services}")
        print(f"  • Network References: {len(self.network_info)}")
        print(f"  • Desktop Components: {len(self.desktop_info)}")
        
        print("\n✅ Analysis complete!")
        
    def run_analysis(self):
        """Run complete memory analysis"""
        strings_data = self.extract_strings()
        if not strings_data:
            print("❌ No string data extracted - cannot continue analysis")
            return
            
        self.analyze_processes(strings_data)
        self.analyze_services(strings_data)
        self.analyze_network(strings_data)
        self.analyze_desktop(strings_data)
        self.generate_report()

def main():
    if len(sys.argv) != 2:
        print("Usage: python3 memory_analysis.py <memory_dump_file>")
        sys.exit(1)
    
    dump_file = sys.argv[1]
    
    try:
        analyzer = MemoryAnalyzer(dump_file)
        analyzer.run_analysis()
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 