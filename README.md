# 🐉 MAC Changer & Security Analyzer — Kali Linux Edition v2.0

> **Stealth Layer-2 Suite & Security Auditor for Kali Linux.**
> Educational cybersecurity project for demonstrating MAC-address management, privacy concepts, hardware vendor masquerading, and the limitations of Layer-2 access control.

---

## 🎨 New Kali Terminal User Interface (TUI)

The tool now features a custom **Kali Cyberpunk TUI** powered by a zero-dependency pure-Python ANSI/Unicode engine. It runs natively across any terminal emulator (QTerminal, Alacritty, GNOME Terminal, Tilix, tmux):

```text
 ────────────────────────────────────────────────────────────────────
  ███████╗████████╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗
  ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║
  ███████╗   ██║   █████╗  ███████║██║     ██║   ███████║
  ╚════██║   ██║   ██╔══╝  ██╔══██║██║     ██║   ██╔══██║
  ███████║   ██║   ███████╗██║  ██║███████╗██║   ██║  ██║
  ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝
     [ KALI LINUX MAC CHANGER & SECURITY AUDITOR v2.0.0 ]
 ────────────────────────────────────────────────────────────────────
 [KALI]  [ROOT PRIVILEGES]  [3 INTERFACES]
 ────────────────────────────────────────────────────────────────────
```

### ✨ Key Features

- **🌐 Live Interfaces Dashboard**: Displays adapters, link state (`UP`/`DOWN`), IPv4 address, interface type (Ethernet, Wi-Fi, Virtual), current MAC, permanent hardware MAC, and `[FACTORY]` vs `[SPOOFED]` badges.
- **🔍 Deep Security & Privacy Audit**:
  - Unicast vs Multicast bit inspection (I/G bit).
  - Universal (Factory OUI) vs Locally Administered (LAA / Randomized) bit analysis.
  - Manufacturer identification via built-in OUI resolution.
  - Privacy rating & wireless tracking risk assessment.
- **🎭 Hardware Vendor Masquerading**:
  - One-click presets to spoof as **Apple Inc.** (iPhone/MacBook), **Cisco Systems**, **Intel Corporate**, **Samsung Electronics**, **Google**, **Raspberry Pi**, and **TP-Link**.
- **🎲 Clean Random MAC Generator**:
  - Generates valid, unicast, locally administered MAC addresses.
- **⚡ Visual Diff Cards**:
  - Live side-by-side before/after comparison highlighting changed octets.
- **🔄 Safe Factory Restore**:
  - One-touch restoration of permanent hardware MAC using kernel verification.
- **📜 Operations Audit Trail**:
  - Structured chronological table of all modifications and restorations saved to `logs/operations.log`.
- **🚀 Zero External Dependencies**:
  - 100% standard library Python 3. No pip packages or network downloads required at runtime.

---

## ⚡ Installation on Kali Linux

Run the enhanced installer:

```bash
cd mac-changer-project
chmod +x install.sh
./install.sh
```

The installer will:
1. Verify Kali/Debian Linux environment.
2. Install `python3`, `iproute2`, and `macchanger`.
3. Create a global command shortcut `/usr/local/bin/mac-changer`.

---

## 💻 Usage

### 1. Interactive Cyber TUI (Recommended)

Launch the full interactive suite:

```bash
sudo mac-changer
# or
sudo python3 mac_changer.py
```

You will be greeted by the Kali banner and interactive operations menu:
1. `🌐 Interfaces Dashboard`
2. `🔍 Deep Security Audit`
3. `🎲 Quick Random Spoof`
4. `🎭 Vendor Masquerade`
5. `✍️  Custom MAC Address`
6. `🔄 Restore Factory MAC`
7. `⚡ Toggle Interface (UP/DOWN)`
8. `📜 View Operations Log`
9. `🚪 Exit`

---

### 2. Command-Line (CLI) Shortcuts

You can also run automated or one-liner operations:

#### 📊 List Interface Dashboard
```bash
mac-changer --list
```

#### 🔍 Perform Deep Security Audit
```bash
mac-changer -i eth0 --audit
```

#### 🎲 Apply Random Locally Administered MAC
```bash
sudo mac-changer -i eth0 --random
```

#### 🎭 Masquerade as a Vendor (Apple, Cisco, Intel, Samsung, Google, RPi)
```bash
sudo mac-changer -i eth0 --vendor apple
sudo mac-changer -i eth0 --vendor cisco
sudo mac-changer -i eth0 --vendor intel
```

#### ✍️ Apply a Specific MAC Address
```bash
sudo mac-changer -i eth0 --mac 02:11:22:33:44:55
```

#### 🔄 Restore Permanent Factory Hardware MAC
```bash
sudo mac-changer -i eth0 --restore
```

#### 📋 Export Interface & Audit Metadata to JSON (Scripting)
```bash
mac-changer -i eth0 --json
```

---

## 🛡️ Security Discussion & Educational Context

A MAC address is a Layer-2 physical identifier. In modern wireless and wired networks:
1. **Privacy & Tracking**: Permanent hardware MACs broadcast the device manufacturer OUI to all nearby Wi-Fi access points and packet sniffers, enabling physical location tracking across networks.
2. **Access Control Limitations**: MAC filtering is not a security boundary; unauthorized actors can observe legitimate frames over the air and spoof authorized MAC addresses.
3. **Enterprise Defense**: Strong network security relies on cryptographic authentication (802.1X, WPA3-Enterprise, certificates) rather than Layer-2 identifiers alone.

---

## 📜 License

For educational, lab security testing, and privacy research purposes only.
