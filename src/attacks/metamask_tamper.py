#!/usr/bin/env python3
"""
PASIV MetaMask Extension Tampering Tool
Demonstrates browser extension modification attacks for security research
WARNING: For authorized security research only!
"""

import os
import re
import json
import shutil
import glob
from pathlib import Path
import subprocess
import sys

class MetaMaskTamper:
    def __init__(self):
        self.browser_paths = {
            'chrome': [
                '~/.config/google-chrome/Default/Extensions',
                '~/.config/google-chrome-unstable/Default/Extensions',
                '~/.config/chromium/Default/Extensions'
            ],
            'firefox': [
                '~/.mozilla/firefox/*/extensions'
            ]
        }
        self.metamask_id = 'nkbihfbeogaeaoehlefnkodbefgpgknn'  # Official MetaMask extension ID
        self.backup_dir = Path('metamask_backups')
        self.tamper_log = []
        
    def find_metamask_installations(self):
        """Find all MetaMask extension installations"""
        installations = []
        
        for browser, paths in self.browser_paths.items():
            for path_pattern in paths:
                expanded_path = Path(path_pattern).expanduser()
                
                if browser == 'chrome':
                    # Chrome/Chromium extensions
                    metamask_path = expanded_path / self.metamask_id
                    if metamask_path.exists():
                        # Find the version directory
                        version_dirs = list(metamask_path.glob('*'))
                        for version_dir in version_dirs:
                            if version_dir.is_dir():
                                installations.append({
                                    'browser': browser,
                                    'path': version_dir,
                                    'manifest': version_dir / 'manifest.json'
                                })
                                
                elif browser == 'firefox':
                    # Firefox extensions (different structure)
                    for profile_path in glob.glob(str(expanded_path)):
                        profile_path = Path(profile_path)
                        if profile_path.exists():
                            for ext_file in profile_path.glob('*metamask*'):
                                installations.append({
                                    'browser': browser,
                                    'path': ext_file,
                                    'manifest': None
                                })
        
        return installations
    
    def backup_extension(self, install_path):
        """Create backup of original extension"""
        self.backup_dir.mkdir(exist_ok=True)
        backup_name = f"metamask_backup_{install_path.name}_{int(os.path.getmtime(install_path))}"
        backup_path = self.backup_dir / backup_name
        
        print(f"📁 Creating backup: {backup_path}")
        shutil.copytree(install_path, backup_path)
        return backup_path
    
    def find_text_files(self, extension_path):
        """Find files that might contain UI text"""
        text_files = []
        
        # Common file patterns that contain UI text
        patterns = [
            '**/*.js',
            '**/*.html',
            '**/*.json',
            '**/*.css'
        ]
        
        for pattern in patterns:
            for file_path in extension_path.glob(pattern):
                if file_path.is_file():
                    text_files.append(file_path)
                    
        return text_files
    
    def tamper_welcome_text(self, file_path):
        """Replace welcome text with hacked version"""
        try:
            # Read file content
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            original_content = content
            
            # Tampering patterns
            tampering_rules = [
                # Welcome messages
                (r'Welcome back', 'Welcome HACK'),
                (r'Welcome Back', 'Welcome HACK'),
                (r'welcome back', 'welcome HACK'),
                (r'Welcome to MetaMask', 'Welcome to HACKED MetaMask'),
                (r'Welcome to your wallet', 'Welcome to your HACKED wallet'),
                
                # Security messages for demonstration
                (r'Your wallet is secure', 'Your wallet is COMPROMISED'),
                (r'Secure your wallet', 'HACKED: Secure your wallet'),
                (r'MetaMask is locked', 'MetaMask is HACKED'),
                
                # Unlock messages
                (r'Unlock your wallet', 'UNLOCK YOUR HACKED WALLET'),
                (r'Enter password', 'Enter password (INTERCEPTED)'),
                
                # Transaction messages
                (r'Confirm transaction', 'CONFIRM INTERCEPTED TRANSACTION'),
                (r'Transaction confirmed', 'Transaction HIJACKED'),
            ]
            
            changes_made = []
            for pattern, replacement in tampering_rules:
                if re.search(pattern, content, re.IGNORECASE):
                    new_content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                    if new_content != content:
                        changes_made.append(f"{pattern} → {replacement}")
                        content = new_content
            
            # Write modified content back
            if changes_made:
                file_path.write_text(content, encoding='utf-8')
                return changes_made
            
        except Exception as e:
            print(f"⚠️  Error tampering {file_path}: {e}")
            
        return []
    
    def inject_warning_banner(self, extension_path):
        """Inject a visible warning banner in HTML files"""
        banner_css = """
        <style>
        .pasiv-hack-banner {
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            width: 100% !important;
            background: linear-gradient(45deg, #ff0000, #ff6600) !important;
            color: white !important;
            text-align: center !important;
            padding: 10px !important;
            font-weight: bold !important;
            font-size: 14px !important;
            z-index: 999999 !important;
            border-bottom: 3px solid #000 !important;
            font-family: monospace !important;
        }
        .pasiv-hack-banner::before {
            content: "⚠️ SECURITY RESEARCH: EXTENSION MODIFIED BY PASIV ⚠️" !important;
        }
        </style>
        <div class="pasiv-hack-banner"></div>
        """
        
        html_files = list(extension_path.glob('**/*.html'))
        for html_file in html_files:
            try:
                content = html_file.read_text(encoding='utf-8')
                if '<head>' in content:
                    content = content.replace('<head>', f'<head>{banner_css}')
                    html_file.write_text(content, encoding='utf-8')
                    print(f"💉 Injected warning banner into {html_file.name}")
            except Exception as e:
                print(f"⚠️  Error injecting banner into {html_file}: {e}")
    
    def tamper_extension(self, installation):
        """Perform tampering on a MetaMask installation"""
        extension_path = installation['path']
        print(f"\n🎯 Tampering with MetaMask at: {extension_path}")
        
        # Create backup
        backup_path = self.backup_extension(extension_path)
        
        # Find text files to modify
        text_files = self.find_text_files(extension_path)
        print(f"📝 Found {len(text_files)} files to analyze")
        
        total_changes = 0
        modified_files = []
        
        # Tamper with text content
        for file_path in text_files:
            changes = self.tamper_welcome_text(file_path)
            if changes:
                modified_files.append({
                    'file': str(file_path.relative_to(extension_path)),
                    'changes': changes
                })
                total_changes += len(changes)
                print(f"✏️  Modified {file_path.name}: {len(changes)} changes")
        
        # Inject visible warning banner
        self.inject_warning_banner(extension_path)
        
        # Log tampering activity
        tamper_record = {
            'installation': str(extension_path),
            'backup': str(backup_path),
            'browser': installation['browser'],
            'files_modified': len(modified_files),
            'total_changes': total_changes,
            'modifications': modified_files
        }
        
        self.tamper_log.append(tamper_record)
        return tamper_record
    
    def restore_from_backup(self, backup_path, installation_path):
        """Restore extension from backup"""
        print(f"🔄 Restoring from backup: {backup_path}")
        if Path(backup_path).exists():
            shutil.rmtree(installation_path)
            shutil.copytree(backup_path, installation_path)
            print(f"✅ Restored to: {installation_path}")
        else:
            print(f"❌ Backup not found: {backup_path}")
    
    def generate_report(self):
        """Generate tampering report"""
        report = {
            'framework': 'PASIV MetaMask Tamper Tool',
            'timestamp': __import__('time').time(),
            'installations_tampered': len(self.tamper_log),
            'details': self.tamper_log
        }
        
        report_file = f"metamask_tamper_report_{int(report['timestamp'])}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📊 TAMPERING REPORT")
        print("=" * 50)
        print(f"Installations found: {len(self.tamper_log)}")
        
        for i, record in enumerate(self.tamper_log, 1):
            print(f"\n{i}. {record['browser'].upper()} Installation")
            print(f"   Path: {record['installation']}")
            print(f"   Files modified: {record['files_modified']}")
            print(f"   Total changes: {record['total_changes']}")
            print(f"   Backup: {record['backup']}")
        
        print(f"\n💾 Full report saved: {report_file}")
        return report_file

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '--restore':
        print("🔄 Restoration mode not implemented yet")
        print("   Manually restore from backups in metamask_backups/")
        return
    
    print("🦊 PASIV MetaMask Extension Tampering Tool")
    print("=" * 50)
    print("⚠️  WARNING: This tool modifies browser extensions!")
    print("⚠️  Only use for authorized security research!")
    print("⚠️  Backups will be created automatically\n")
    
    # Confirm before proceeding
    response = input("Continue with MetaMask tampering? (yes/no): ")
    if response.lower() != 'yes':
        print("Aborted.")
        return
    
    tamper = MetaMaskTamper()
    
    # Find MetaMask installations
    installations = tamper.find_metamask_installations()
    
    if not installations:
        print("❌ No MetaMask installations found!")
        print("   Make sure MetaMask is installed in Chrome/Chromium")
        return
    
    print(f"🔍 Found {len(installations)} MetaMask installation(s)")
    
    # Tamper with each installation
    for installation in installations:
        try:
            tamper.tamper_extension(installation)
        except Exception as e:
            print(f"❌ Error tampering with {installation['path']}: {e}")
    
    # Generate report
    tamper.generate_report()
    
    print(f"\n🎯 TAMPERING COMPLETE!")
    print(f"✅ Modified {len(installations)} MetaMask installation(s)")
    print(f"📁 Backups stored in: metamask_backups/")
    print(f"⚠️  Restart browser to see changes")
    print(f"🔄 To restore: copy files from backups manually")

if __name__ == "__main__":
    main() 