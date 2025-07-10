# PASIV MetaMask Extension Tampering Tool

## Overview
This tool demonstrates how browser extensions can be modified by attackers to manipulate user interfaces and potentially deceive users. It's designed for security research to understand extension-based attack vectors.

## Features

### 🎯 **Text Replacement**
The script will find and replace various MetaMask UI text elements:

- `"Welcome back"` → `"Welcome HACK"`
- `"Welcome to MetaMask"` → `"Welcome to HACKED MetaMask"`
- `"Your wallet is secure"` → `"Your wallet is COMPROMISED"`
- `"Unlock your wallet"` → `"UNLOCK YOUR HACKED WALLET"`
- `"Confirm transaction"` → `"CONFIRM INTERCEPTED TRANSACTION"`

### 🚨 **Visual Indicators**
- Injects a bright red warning banner at the top of MetaMask pages
- Banner displays: "⚠️ SECURITY RESEARCH: EXTENSION MODIFIED BY PASIV ⚠️"
- Helps identify tampered extensions during research

### 💾 **Safety Features**
- **Automatic Backups**: Creates complete backups before any modifications
- **Detailed Logging**: Records all changes made to extension files
- **Report Generation**: Creates JSON reports of tampering activities

## Usage

### Basic Tampering
```bash
python3 src/attacks/metamask_tamper.py
```

### Restoration (Manual)
```bash
# Backups are stored in metamask_backups/
# Manually copy files back to restore original extension
cp -r metamask_backups/metamask_backup_* ~/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/
```

## Technical Details

### Supported Browsers
- **Chrome/Chromium**: `~/.config/google-chrome/Default/Extensions`
- **Firefox**: `~/.mozilla/firefox/*/extensions` (limited support)

### File Types Modified
- **JavaScript files** (`.js`) - Main UI logic and text
- **HTML files** (`.html`) - Page structure and content  
- **JSON files** (`.json`) - Configuration and localization
- **CSS files** (`.css`) - Styling and appearance

### Extension Detection
- Searches for MetaMask extension ID: `nkbihfbeogaeaoehlefnkodbefgpgknn`
- Automatically finds all version directories
- Handles multiple browser profiles

## Security Research Applications

### 1. **Social Engineering Demos**
- Show how UI manipulation can deceive users
- Demonstrate fake security messages
- Illustrate transaction hijacking interfaces

### 2. **Extension Security Testing**
- Test if browsers detect modified extensions
- Verify code signing and integrity checks
- Analyze extension update mechanisms

### 3. **User Awareness Training**
- Create realistic phishing scenarios
- Train users to spot suspicious interfaces
- Demonstrate attack vectors

## Example Output

```
🦊 PASIV MetaMask Extension Tampering Tool
==================================================
⚠️  WARNING: This tool modifies browser extensions!
⚠️  Only use for authorized security research!
⚠️  Backups will be created automatically

🔍 Found 1 MetaMask installation(s)

🎯 Tampering with MetaMask at: ~/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/12.2.3_0
📁 Creating backup: metamask_backups/metamask_backup_12.2.3_0_1704844800
📝 Found 247 files to analyze
✏️  Modified app.js: 3 changes
✏️  Modified popup.html: 1 changes
✏️  Modified content-script.js: 2 changes
💉 Injected warning banner into popup.html
💉 Injected warning banner into notification.html

📊 TAMPERING REPORT
==================================================
Installations found: 1

1. CHROME Installation
   Path: ~/.config/google-chrome/Default/Extensions/nkbihfbeogaeaoehlefnkodbefgpgknn/12.2.3_0
   Files modified: 3
   Total changes: 6
   Backup: metamask_backups/metamask_backup_12.2.3_0_1704844800

💾 Full report saved: metamask_tamper_report_1704844800.json
```

## Security Warnings

⚠️ **IMPORTANT DISCLAIMERS**:

1. **Authorized Use Only**: Only use on systems you own or have explicit permission to test
2. **Educational Purpose**: Designed for security research and user awareness training
3. **Browser Restart Required**: Changes only take effect after restarting the browser
4. **Backup Critical**: Always verify backups before proceeding
5. **Detection Risk**: Modified extensions may be flagged by security software

## Attack Vector Analysis

### How This Attack Works in Real Scenarios:

1. **Malware Installation**: Attacker gains system access via malware
2. **Extension Discovery**: Locates browser extension directories
3. **File Modification**: Modifies extension files to inject malicious content
4. **User Deception**: Modified UI tricks users into revealing private keys
5. **Credential Theft**: Captures passwords, seed phrases, or transaction data

### Defense Strategies:

- **Code Signing**: Verify extension signatures regularly
- **File Integrity**: Monitor extension directories for changes
- **Browser Security**: Use browsers with extension integrity checking
- **User Training**: Educate users about suspicious interface changes

## Integration with PASIV

This tool complements other PASIV components:

- **Memory Analysis**: `metamask_extractor.py` - Extract data from memory
- **Key Matching**: `key_address_matcher.py` - Derive addresses from keys  
- **Extension Tampering**: `metamask_tamper.py` - Modify browser interfaces

Together, these tools demonstrate a complete attack chain against cryptocurrency wallets in virtualized environments.

---

**Part of the PASIV (Peripheral Attack Simulation and Introspection Vehicle) Framework**  
For authorized security research and educational purposes only. 