## PASIV DEFCON Demo: Live DMA Hijack of a $1 USDC Transfer to vitalik.eth (Base)

> Educational/Research use only. Perform this demo only on systems and accounts you control, with negligible funds you can afford to lose. This attack operates below the OS and browser security layers.

### Related DEF CON 33 Talk
- Session link: [Hacker Tracker event page](https://hackertracker.app/event/?conf=DEFCON33&event=61038)
- Presenters: Joe and Grace (collaboration support from the PASIV team)
- Quick summary: Live demonstration of DMA-enabled memory tampering to hijack ERC‑20 token transfers from within a running VM. The session walks through configuring a vulnerable target, observing ASCII‑encoded Web3 transaction data in memory (e.g., `0xa9059cbb…`), and performing real‑time recipient address substitution before broadcast, along with discussion of mitigations and research ethics.

### Overview
This demo shows how to:
- Launch an Ubuntu VM with file-backed (DMA-accessible) memory
- Install MetaMask in the VM and add the Base network + USDC token
- Fund the VM wallet with a small amount of USDC on Base
- Initiate a USDC transfer to `vitalik.eth`
- Run `ascii_transfer_monitor.py` from the host to hijack the destination address in real-time

The hijack works by scanning the VM's memory for ASCII-encoded ERC-20 transfer calls (`0xa9059cbb…`) and replacing the 40-hex-character recipient with an attacker-chosen value.

---

### 0) Host Prerequisites
- Ubuntu host with virtualization support (KVM)
- QEMU installed: `sudo apt install -y qemu-system-x86 qemu-kvm`  
- Optional viewers: `sudo apt install -y tigervnc-viewer remote-viewer`  
- Python 3.8+ available on host  
- This repo cloned and you are in the project root: `/home/pierce/projects/PASIV`

Note: The included launcher starts QEMU directly with file-backed RAM for DMA.

---

### 1) Start the VM with DMA-accessible memory (Host)
From the PASIV project root:

```bash
./scripts/launch/launch_dma_qemu_direct.sh
```

What this does:
- Creates `./pasiv_vm_memory.raw` (4 GB) in the repo root and launches a VM with RAM backed by this file
- Also creates/refreshes a symlink `./pasiv_vm_memory.img` -> `./pasiv_vm_memory.raw`
- QEMU GTK window appears (or connect via VNC at `localhost:5901`)
- SSH forwarding available on `localhost:2222` (inside VM once configured)

(If needed) Recreate the link the monitor reads by default:

```bash
ln -sf ./pasiv_vm_memory.raw ./pasiv_vm_memory.img
```

Verification (optional):
```bash
hexdump -C ./pasiv_vm_memory.raw | head -10
# Expect non-zero data once the VM is booted
```

---

### 2) Inside the VM: Install Browser and MetaMask
In the VM desktop:
1. Install a Chromium/Chrome or Firefox browser
2. Install the MetaMask extension from the official store
3. Create a new wallet (record the seed phrase securely and offline)

---

### 3) Add the Base Network to MetaMask (Mainnet)
In MetaMask -> Networks -> Add network manually:
- Network Name: `Base`
- RPC URL: `https://mainnet.base.org`
- Chain ID: `8453`
- Currency Symbol: `ETH`
- Block Explorer: `https://basescan.org`

Save.

---

### 4) Add USDC Token on Base
USDC (Base) contract:
```
0x833589fCD6EDB6E08f4c7c32D4f71B54Bda02913
```
In MetaMask -> Assets -> Import Tokens:
- Token contract address: paste the above
- Name/Symbol should auto-fill as USDC

---

### 5) Fund the VM Wallet with Small USDC on Base
Transfer ~$2 USDC (or less) to the VM wallet address on Base.  
Options: send from another wallet you control, a centralized exchange with Base withdrawals, or bridge from another chain.  
Wait for the balance to appear in MetaMask (Base).

---

### 6) Prepare the Demo Transaction to vitalik.eth
In MetaMask (VM):
1. Select USDC asset
2. Click Send
3. In the Recipient field, enter `vitalik.eth` (ENS resolves to `0xd8dA6BF26964aF9D7eEd9e03E53415D37aA96045`)
4. Enter Amount: `1` USDC
5. Proceed to the confirmation screen but do not confirm yet

Leave the confirmation dialog open so that the transfer data is resident in memory.

---

### 7) Run the ASCII Transfer Monitor (Host)
From the host, in the PASIV project root:

```bash
# (Optional) activate venv if you use one
# source venv/bin/activate

python3 ascii_transfer_monitor.py
```

Notes:
- No arguments = universal mode (hijacks ANY ERC-20 `transfer()` found)
- The tool scans `./pasiv_vm_memory.img` which links to the VM’s RAM file
- You should see logs like:
  - `Target: ANY ERC-20 transfer (universal attack mode)`
  - `🎯 NEW ERC-20 TRANSFER(S) DETECTED! ...`
  - `🔥 DMA ATTACK SUCCESSFUL!`

---

### 8) Execute the Transfer in MetaMask (VM)
Back in the VM:
- Click Confirm in MetaMask for the 1 USDC transfer to `vitalik.eth`
- The host monitor should immediately log detections and successful replacements

By default, the tool replaces the 40-hex recipient with an easily-visible pattern (counter + `66` filler).  
If you want to redirect to a specific attacker address, edit `generate_evil_address()` in `ascii_transfer_monitor.py` to return your ASCII-hex address (40 lowercase hex chars, no `0x`).

---

### 9) Verify on BaseScan
After MetaMask broadcasts the transaction:
1. Copy the Tx hash from MetaMask
2. Open `https://basescan.org/tx/<TX_HASH>` in the VM browser
3. Verify the `To` (token recipient) is NOT Vitalik’s address. It should match the replaced value printed by the tool.

If you changed the evil address to your own, you should receive the USDC.

---

### 10) Troubleshooting
- Memory file shows only zeros:
  - Ensure the VM was started with `launch_dma_qemu_direct.sh` and that `-object memory-backend-file,...,mem-path=<project_path>/pasiv_vm_memory.raw` is present in the QEMU command line
  - Recreate the link: `ln -sf ./pasiv_vm_memory.raw ./pasiv_vm_memory.img`
- No detections:
  - Confirm you’re sending USDC on Base and are on the final confirmation screen
  - Ensure the selector printed in the monitor includes `0xa9059cbb...`
  - Let the monitor run while you press Confirm
- Permission denied on the VM disk:
  - Stop any libvirt VMs using the same image (`sudo virsh list --all`) and ensure only the direct QEMU process has the disk open
- Viewer access:
  - QEMU GTK opens a window on the host desktop.  
  - Or connect via VNC: `vncviewer localhost:1` (port 5901)

---

### 11) Cleanup
- Close the VM window or send `System -> Power Off` inside the VM
- Remove the RAM file and link if desired:
```bash
rm -f ./pasiv_vm_memory.raw ./pasiv_vm_memory.img
```

---

### Legal / Ethics
This demo is for research and education. Do not perform unauthorized interception or redirection of funds. Always use your own systems and accounts and keep amounts trivial.
