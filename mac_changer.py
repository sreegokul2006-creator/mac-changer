#!/usr/bin/env python3
"""
MAC Changer & Security Analyzer v2.0
Stealth Layer-2 Suite & Security Auditor for Kali Linux.

Designed for educational security research, lab environments, and privacy testing.
Changes are temporary and apply only to local network interfaces.
"""

import argparse
import datetime as dt
import json
import os
import random
import re
import shutil
import subprocess
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# CONFIGURATION & CONSTANTS
# ──────────────────────────────────────────────────────────────────────────────

VERSION = "2.0.0"
BASE_DIR = Path(__file__).resolve().parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "operations.log"
MAC_RE = re.compile(r"^(?:[0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}$")

# Prominent Hardware Vendors and their known OUIs
VENDOR_DATABASE = {
    # Apple
    "00:1c:b3": "Apple Inc.",
    "a4:83:e7": "Apple Inc.",
    "f0:18:98": "Apple Inc.",
    "3c:06:30": "Apple Inc.",
    "ac:bc:32": "Apple Inc.",
    "e0:b9:ba": "Apple Inc.",
    # Intel
    "00:1b:21": "Intel Corporate",
    "a4:4e:31": "Intel Corporate",
    "48:51:b7": "Intel Corporate",
    "80:86:f2": "Intel Corporate",
    "00:21:6a": "Intel Corporate",
    # Cisco
    "00:00:0c": "Cisco Systems",
    "00:01:42": "Cisco Systems",
    "00:1a:a1": "Cisco Systems",
    "00:26:0b": "Cisco Systems",
    # Samsung
    "00:12:fb": "Samsung Electronics",
    "50:01:d9": "Samsung Electronics",
    "e4:7c:f9": "Samsung Electronics",
    "78:40:e4": "Samsung Electronics",
    # Google
    "54:60:09": "Google Inc.",
    "f4:f5:d8": "Google Inc.",
    "3c:5a:37": "Google Inc.",
    "d8:3c:69": "Google Inc.",
    # Raspberry Pi
    "b8:27:eb": "Raspberry Pi Foundation",
    "dc:a6:32": "Raspberry Pi Foundation",
    "e4:5f:01": "Raspberry Pi Foundation",
    "28:cd:c1": "Raspberry Pi Foundation",
    # TP-Link
    "50:c7:bf": "TP-Link Technologies",
    "14:cc:20": "TP-Link Technologies",
    "e8:48:b8": "TP-Link Technologies",
    "ec:08:6b": "TP-Link Technologies",
    # Huawei
    "00:e0:fc": "Huawei Technologies",
    "20:08:89": "Huawei Technologies",
    "70:54:f5": "Huawei Technologies",
    # Realtek
    "00:e0:4c": "Realtek Semiconductor",
    "52:54:4c": "Realtek Semiconductor",
    "00:1c:df": "Realtek Semiconductor",
    # Microsoft
    "00:15:5d": "Microsoft Corporation",
    "7c:1e:52": "Microsoft Corporation",
    "28:18:78": "Microsoft Corporation",
    # Sony
    "00:01:4a": "Sony Corporation",
    "70:9e:29": "Sony Corporation",
    # Dell
    "00:14:22": "Dell Inc.",
    "18:66:da": "Dell Inc.",
    "98:90:96": "Dell Inc.",
}

# ──────────────────────────────────────────────────────────────────────────────
# ANSI / TUI ENGINE (Zero Dependencies)
# ──────────────────────────────────────────────────────────────────────────────

class Theme:
    """Cyberpunk / Kali Linux Terminal Color Theme."""
    ENABLED = sys.stdout.isatty() and os.environ.get("NO_COLOR") is None

    RESET = "\033[0m" if ENABLED else ""
    BOLD = "\033[1m" if ENABLED else ""
    DIM = "\033[2m" if ENABLED else ""
    ITALIC = "\033[3m" if ENABLED else ""
    UNDERLINE = "\033[4m" if ENABLED else ""

    # Neon / Kali Palette
    CYAN = "\033[38;5;51m" if ENABLED else ""        # Vibrant Kali Cyan
    GREEN = "\033[38;5;48m" if ENABLED else ""       # Emerald Neon Green
    RED = "\033[38;5;196m" if ENABLED else ""        # Crimson Alert
    YELLOW = "\033[38;5;220m" if ENABLED else ""     # Amber Warning
    BLUE = "\033[38;5;39m" if ENABLED else ""        # Electric Blue
    MAGENTA = "\033[38;5;201m" if ENABLED else ""    # Cyberpunk Purple/Pink
    ORANGE = "\033[38;5;208m" if ENABLED else ""     # Vibrant Orange
    WHITE = "\033[97m" if ENABLED else ""
    GRAY = "\033[38;5;244m" if ENABLED else ""       # Subtle text
    DARK_GRAY = "\033[38;5;238m" if ENABLED else ""  # Frame / Border
    BG_DARK = "\033[48;5;235m" if ENABLED else ""


def c(text: str, *styles) -> str:
    """Format text with ANSI styles."""
    if not Theme.ENABLED:
        return str(text)
    return "".join(styles) + str(text) + Theme.RESET


def strip_ansi(text: str) -> str:
    """Remove ANSI escape sequences to compute visible string length."""
    return re.sub(r"\x1B\[[0-?]*[ -/]*[@-~]", "", str(text))


def visible_len(text: str) -> int:
    """Return the length of the string without ANSI codes."""
    return len(strip_ansi(text))


def pad(text: str, width: int, align: str = "left") -> str:
    """Pad a string to exact visual width considering ANSI formatting."""
    vlen = visible_len(text)
    diff = max(0, width - vlen)
    if align == "right":
        return (" " * diff) + text
    if align == "center":
        left = diff // 2
        right = diff - left
        return (" " * left) + text + (" " * right)
    return text + (" " * diff)


def badge(label: str, style_type: str = "cyan") -> str:
    """Render a styled pill badge."""
    color_map = {
        "cyan": (Theme.CYAN, Theme.BOLD),
        "green": (Theme.GREEN, Theme.BOLD),
        "red": (Theme.RED, Theme.BOLD),
        "yellow": (Theme.YELLOW, Theme.BOLD),
        "blue": (Theme.BLUE, Theme.BOLD),
        "magenta": (Theme.MAGENTA, Theme.BOLD),
        "gray": (Theme.GRAY, Theme.BOLD),
    }
    fg, weight = color_map.get(style_type, (Theme.CYAN, Theme.BOLD))
    return f"{c('[', Theme.DARK_GRAY)}{c(label, fg, weight)}{c(']', Theme.DARK_GRAY)}"


def print_banner():
    """Display the Kali Cyber banner and system telemetry bar."""
    banner_text = f"""{c('  ███████╗████████╗███████╗ █████╗ ██╗  ████████╗██╗  ██╗', Theme.CYAN, Theme.BOLD)}
{c('  ██╔════╝╚══██╔══╝██╔════╝██╔══██╗██║  ╚══██╔══╝██║  ██║', Theme.CYAN, Theme.BOLD)}
{c('  ███████╗   ██║   █████╗  ███████║██║     ██║   ███████║', Theme.BLUE, Theme.BOLD)}
{c('  ╚════██║   ██║   ██╔══╝  ██╔══██║██║     ██║   ██╔══██║', Theme.BLUE, Theme.BOLD)}
{c('  ███████║   ██║   ███████╗██║  ██║███████╗██║   ██║  ██║', Theme.MAGENTA, Theme.BOLD)}
{c('  ╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚══════╝╚═╝   ╚═╝  ╚═╝', Theme.MAGENTA, Theme.BOLD)}
{c('     [ KALI LINUX MAC CHANGER & SECURITY AUDITOR v' + VERSION + ' ]', Theme.GREEN, Theme.BOLD)}"""

    # Telemetry bar
    is_root = os.geteuid() == 0 if hasattr(os, "geteuid") else False
    root_badge = badge("ROOT PRIVILEGES", "red") if is_root else badge("UNPRIVILEGED (sudo needed)", "yellow")
    
    try:
        iface_count = len(get_interfaces())
        iface_badge = badge(f"{iface_count} INTERFACES", "green" if iface_count > 0 else "yellow")
    except Exception:
        iface_badge = badge("NO INTERFACES", "red")

    line = c("─" * 68, Theme.DARK_GRAY)
    print("\n" + line)
    print(banner_text)
    print(line)
    telemetry = f" {badge('KALI', 'cyan')}  {root_badge}  {iface_badge}"
    print(telemetry)
    print(line + "\n")


def clear_screen():
    """Clear terminal screen gracefully."""
    if sys.stdout.isatty():
        os.system("clear" if os.name != "nt" else "cls")


def draw_box(title: str, content_lines: list, border_color=Theme.CYAN, width=68):
    """Draw a clean Unicode framed card."""
    b = border_color
    rst = Theme.RESET

    t_str = f" {title} " if title else ""
    t_vlen = visible_len(t_str)
    top_fill = max(0, width - 2 - t_vlen)
    
    top = f"{b}┌─{rst}{c(t_str, Theme.BOLD, Theme.WHITE)}{b}{'─' * max(0, top_fill - 1)}┐{rst}"
    bottom = f"{b}└{'─' * (width - 2)}┘{rst}"
    
    print(top)
    for line in content_lines:
        v_len = visible_len(line)
        spacing = max(0, width - 4 - v_len)
        print(f"{b}│{rst} {line}{' ' * spacing} {b}│{rst}")
    print(bottom)


def draw_table(headers: list, rows: list, col_widths: list, border_color=Theme.DARK_GRAY):
    """Render a structured terminal data table with Unicode box-drawing."""
    b = border_color
    rst = Theme.RESET
    
    # Top border
    top = b + "┌" + "┬".join("─" * (w + 2) for w in col_widths) + "┐" + rst
    # Header row
    hdr_cells = []
    for h, w in zip(headers, col_widths):
        hdr_cells.append(" " + pad(c(h, Theme.BOLD, Theme.CYAN), w) + " ")
    header_line = b + "│" + (b + "│").join(hdr_cells) + b + "│" + rst
    # Header separator
    sep = b + "├" + "┼".join("─" * (w + 2) for w in col_widths) + "┤" + rst
    # Bottom border
    bot = b + "└" + "┴".join("─" * (w + 2) for w in col_widths) + "┘" + rst

    print(top)
    print(header_line)
    print(sep)
    for row in rows:
        row_cells = []
        for cell, w in zip(row, col_widths):
            row_cells.append(" " + pad(str(cell), w) + " ")
        print(b + "│" + (b + "│").join(row_cells) + b + "│" + rst)
    print(bot)


# ──────────────────────────────────────────────────────────────────────────────
# SYSTEM & LOGGING HELPERS
# ──────────────────────────────────────────────────────────────────────────────

def log_operation(action: str, interface: str, old_mac: str, new_mac: str, status: str = "SUCCESS"):
    """Append structured log entry to operations.log."""
    try:
        LOG_DIR.mkdir(exist_ok=True)
        stamp = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        with LOG_FILE.open("a", encoding="utf-8") as f:
            f.write(f"[{stamp}] [{status}] ACTION={action} IFACE={interface} OLD={old_mac} NEW={new_mac}\n")
    except Exception as e:
        sys.stderr.write(f"Failed to write log: {e}\n")


def run_cmd(args, check=True):
    """Execute shell command safely with captured output."""
    try:
        return subprocess.run(
            args, text=True, capture_output=True, check=check
        )
    except FileNotFoundError:
        raise RuntimeError(f"Required binary not found in PATH: {args[0]}")
    except subprocess.CalledProcessError as e:
        msg = (e.stderr or e.stdout or "").strip()
        raise RuntimeError(msg or f"Command failed with code {e.returncode}: {' '.join(args)}")


def require_tools():
    """Verify system prerequisites."""
    missing = [x for x in ("ip", "macchanger") if shutil.which(x) is None]
    if missing:
        raise RuntimeError(
            f"Missing required utilities: {', '.join(missing)}. "
            "Please run './install.sh' to install system dependencies."
        )


# ──────────────────────────────────────────────────────────────────────────────
# NETWORK INTELLIGENCE & INTERFACE INSPECTION
# ──────────────────────────────────────────────────────────────────────────────

def get_interfaces():
    """Return a list of non-loopback network interface names."""
    result = run_cmd(["ip", "-o", "link", "show"])
    names = []
    for line in result.stdout.splitlines():
        parts = line.split(": ", 2)
        if len(parts) >= 2:
            name = parts[1].split("@", 1)[0]
            if name != "lo":
                names.append(name)
    return names


def get_current_mac(iface: str) -> str:
    """Retrieve the currently active MAC address for an interface."""
    result = run_cmd(["ip", "link", "show", "dev", iface])
    m = re.search(r"link/ether\s+([0-9a-fA-F:]{17})", result.stdout)
    if not m:
        raise RuntimeError(f"Could not read MAC address for interface '{iface}'.")
    return m.group(1).lower()


def get_interface_details(iface: str) -> dict:
    """Gather deep metadata for an interface (state, IP, permanent MAC, type)."""
    details = {
        "name": iface,
        "current_mac": "unavailable",
        "permanent_mac": "unavailable",
        "ipv4": "unassigned",
        "state": "DOWN",
        "type": "Ethernet",
        "is_spoofed": False,
        "vendor": "Unknown",
    }

    # Query link status and current MAC
    try:
        details["current_mac"] = get_current_mac(iface)
        details["vendor"] = lookup_vendor(details["current_mac"])
    except Exception:
        pass

    # Read ip link status
    try:
        res = run_cmd(["ip", "-o", "link", "show", "dev", iface])
        if "state UP" in res.stdout:
            details["state"] = "UP"
        elif "state DOWN" in res.stdout:
            details["state"] = "DOWN"
        else:
            details["state"] = "UNKNOWN"
    except Exception:
        pass

    # Detect interface type
    if iface.startswith(("wl", "ath", "wlan")):
        details["type"] = "Wireless (Wi-Fi)"
    elif iface.startswith(("tun", "tap", "wg")):
        details["type"] = "VPN / Tunnel"
    elif iface.startswith(("br", "docker", "virbr")):
        details["type"] = "Bridge / Virtual"
    else:
        details["type"] = "Ethernet"

    # Query IPv4 address
    try:
        ip_res = run_cmd(["ip", "-4", "-o", "addr", "show", "dev", iface])
        match = re.search(r"inet\s+([0-9.]+/\d+)", ip_res.stdout)
        if match:
            details["ipv4"] = match.group(1)
    except Exception:
        pass

    # Query permanent hardware MAC via macchanger -s
    try:
        mc_res = run_cmd(["macchanger", "-s", iface], check=False)
        for line in mc_res.stdout.splitlines():
            if "Permanent MAC:" in line:
                m = re.search(r"([0-9a-fA-F:]{17})", line)
                if m:
                    details["permanent_mac"] = m.group(1).lower()
                    break
    except Exception:
        pass

    if details["permanent_mac"] == "unavailable":
        # Fallback to current if permanent could not be read
        details["permanent_mac"] = details["current_mac"]

    if details["current_mac"] != "unavailable" and details["permanent_mac"] != "unavailable":
        details["is_spoofed"] = (details["current_mac"] != details["permanent_mac"])

    return details


# ──────────────────────────────────────────────────────────────────────────────
# MAC ANALYSIS & OUI RESOLUTION
# ──────────────────────────────────────────────────────────────────────────────

def lookup_vendor(mac: str) -> str:
    """Resolve vendor from OUI database and analyze address nature."""
    if not mac or mac == "unavailable":
        return "N/A"
    clean_mac = mac.lower().replace("-", ":")
    octets = clean_mac.split(":")
    if len(octets) != 6:
        return "Invalid MAC"

    first_byte = int(octets[0], 16)
    is_laa = bool(first_byte & 0x02)

    oui = ":".join(octets[:3])
    known = VENDOR_DATABASE.get(oui)
    if known:
        return known
    if is_laa:
        return "Locally Administered (Randomized/Private)"
    return "Unknown / Unregistered OUI"


def analyze_mac_security(mac: str) -> dict:
    """Perform a deep security and privacy analysis on a MAC address."""
    if not mac or mac == "unavailable" or not MAC_RE.fullmatch(mac.strip().lower().replace("-", ":")):
        return {
            "mac": mac or "unavailable",
            "multicast": False,
            "type": "Unavailable",
            "laa": False,
            "admin_scope": "Unavailable",
            "vendor": "Unavailable",
            "privacy": "N/A",
            "tracking_risk": "Cannot determine (interface inactive or MAC unreadable)",
        }

    clean_mac = mac.lower().replace("-", ":")
    octets = [int(x, 16) for x in clean_mac.split(":")]
    first_byte = octets[0]

    # I/G bit: Individual (0) vs Group/Multicast (1)
    is_multicast = bool(first_byte & 0x01)
    # U/L bit: Universal (0) vs Locally Administered (1)
    is_laa = bool(first_byte & 0x02)
    vendor = lookup_vendor(clean_mac)

    if is_laa:
        privacy_status = "HIGH (Hardware identity masked)"
        tracking_risk = "LOW — Does not expose factory vendor OUI"
    else:
        privacy_status = "LOW (Factory hardware OUI visible)"
        tracking_risk = "HIGH — Persistent hardware identifier broadcasted to all APs/switches"

    return {
        "mac": clean_mac,
        "multicast": is_multicast,
        "type": "Multicast / Group" if is_multicast else "Unicast / Individual",
        "laa": is_laa,
        "admin_scope": "Locally Administered (LAA)" if is_laa else "Universally Administered (OUI / Factory)",
        "vendor": vendor,
        "privacy": privacy_status,
        "tracking_risk": tracking_risk,
    }


def validate_mac(value: str) -> str:
    """Validate MAC address format and ensure it is not multicast."""
    cleaned = value.strip().lower().replace("-", ":")
    if not MAC_RE.fullmatch(cleaned):
        raise ValueError("MAC address must be in format XX:XX:XX:XX:XX:XX (e.g. 02:4a:5b:6c:7d:8e)")
    octets = [int(x, 16) for x in cleaned.split(":")]
    if octets[0] & 1:
        raise ValueError("Multicast MAC addresses are not permitted (bit 0 of octet 1 is 1).")
    return cleaned


def generate_random_mac() -> str:
    """Generate a valid, locally administered, unicast random MAC."""
    first = random.randrange(0, 256)
    # Bit 1 = 1 (Locally administered), Bit 0 = 0 (Unicast)
    first = (first | 0x02) & 0xFE
    rest = [random.randrange(0, 256) for _ in range(5)]
    return ":".join(f"{x:02x}" for x in [first] + rest)


def generate_vendor_mac(vendor_prefix: str) -> str:
    """Generate a MAC masquerading under a specific vendor's registered OUI."""
    prefix_octets = vendor_prefix.lower().split(":")
    if len(prefix_octets) != 3:
        raise ValueError("Vendor prefix must contain 3 octets (e.g. 00:1c:b3)")
    rest = [random.randrange(0, 256) for _ in range(3)]
    return ":".join(prefix_octets + [f"{x:02x}" for x in rest])


# ──────────────────────────────────────────────────────────────────────────────
# CORE OPERATIONS (CHANGE, RESTORE, TOGGLE)
# ──────────────────────────────────────────────────────────────────────────────

def change_mac(iface: str, new_mac: str):
    """Apply new MAC address using macchanger with automatic fallback."""
    new_mac = validate_mac(new_mac)
    old = get_current_mac(iface)

    # Check if interface is busy / if down/up is required
    cmd = ["sudo", "macchanger", "--mac", new_mac, iface]
    res = subprocess.run(cmd, text=True, capture_output=True)

    # If macchanger fails because device is busy, attempt safe link down/up cycle
    if res.returncode != 0 and ("Device or resource busy" in res.stderr or "Device or resource busy" in res.stdout):
        try:
            run_cmd(["sudo", "ip", "link", "set", "dev", iface, "down"])
            run_cmd(["sudo", "macchanger", "--mac", new_mac, iface])
            run_cmd(["sudo", "ip", "link", "set", "dev", iface, "up"])
        except Exception as e:
            # Ensure interface is brought back up
            subprocess.run(["sudo", "ip", "link", "set", "dev", iface, "up"], capture_output=True)
            raise RuntimeError(f"Failed to change MAC (device busy): {e}")
    elif res.returncode != 0:
        err = (res.stderr or res.stdout).strip()
        raise RuntimeError(err or f"macchanger failed with code {res.returncode}")

    new = get_current_mac(iface)
    log_operation("CHANGE", iface, old, new, "SUCCESS")
    return old, new


def restore_mac(iface: str):
    """Restore the factory/permanent hardware MAC."""
    old = get_current_mac(iface)
    cmd = ["sudo", "macchanger", "--permanent", iface]
    res = subprocess.run(cmd, text=True, capture_output=True)

    if res.returncode != 0 and ("Device or resource busy" in res.stderr or "Device or resource busy" in res.stdout):
        try:
            run_cmd(["sudo", "ip", "link", "set", "dev", iface, "down"])
            run_cmd(["sudo", "macchanger", "--permanent", iface])
            run_cmd(["sudo", "ip", "link", "set", "dev", iface, "up"])
        except Exception as e:
            subprocess.run(["sudo", "ip", "link", "set", "dev", iface, "up"], capture_output=True)
            raise RuntimeError(f"Failed to restore MAC: {e}")
    elif res.returncode != 0:
        err = (res.stderr or res.stdout).strip()
        raise RuntimeError(err or f"macchanger failed with code {res.returncode}")

    new = get_current_mac(iface)
    log_operation("RESTORE", iface, old, new, "SUCCESS")
    return old, new


def toggle_interface(iface: str, state: str):
    """Bring interface UP or DOWN."""
    state = state.lower()
    if state not in ("up", "down"):
        raise ValueError("State must be 'up' or 'down'.")
    run_cmd(["sudo", "ip", "link", "set", "dev", iface, state])
    log_operation("TOGGLE_STATE", iface, state, state, "SUCCESS")


# ──────────────────────────────────────────────────────────────────────────────
# TUI PRESENTERS & VIEWS
# ──────────────────────────────────────────────────────────────────────────────

def render_interfaces_dashboard():
    """Display an overview table of all interfaces, MACs, status, and IP."""
    names = get_interfaces()
    if not names:
        print(c("[-] No non-loopback network interfaces detected.", Theme.RED, Theme.BOLD))
        return

    headers = ["#", "Interface", "State", "Type", "Current MAC", "Status", "IPv4 Address"]
    col_widths = [3, 11, 8, 16, 19, 11, 17]
    rows = []

    for i, name in enumerate(names, 1):
        info = get_interface_details(name)
        state_badge = badge("UP", "green") if info["state"] == "UP" else badge("DOWN", "gray")
        status_badge = badge("SPOOFED", "magenta") if info["is_spoofed"] else badge("FACTORY", "cyan")
        
        rows.append([
            c(str(i), Theme.BOLD, Theme.YELLOW),
            c(info["name"], Theme.BOLD, Theme.WHITE),
            state_badge,
            c(info["type"], Theme.GRAY),
            c(info["current_mac"], Theme.CYAN),
            status_badge,
            c(info["ipv4"], Theme.BLUE if info["ipv4"] != "unassigned" else Theme.GRAY)
        ])

    print(f"\n{c('=== ACTIVE NETWORK INTERFACES ===', Theme.BOLD, Theme.CYAN)}")
    draw_table(headers, rows, col_widths)


def render_security_audit(iface: str):
    """Display deep security and privacy analysis card for an interface."""
    details = get_interface_details(iface)
    mac = details["current_mac"]
    audit = analyze_mac_security(mac)

    status_tag = badge("SPOOFED", "magenta") if details["is_spoofed"] else badge("FACTORY HARDWARE", "yellow")
    
    lines = [
        f"{c('Target Interface:', Theme.GRAY)}  {c(iface, Theme.BOLD, Theme.WHITE)} {status_tag}",
        f"{c('Current MAC:     ', Theme.GRAY)}  {c(mac, Theme.BOLD, Theme.CYAN)}",
        f"{c('Permanent MAC:   ', Theme.GRAY)}  {c(details['permanent_mac'], Theme.GRAY)}",
        f"{c('Identified Vendor:', Theme.GRAY)} {c(audit['vendor'], Theme.BOLD, Theme.GREEN)}",
        f"{c('─' * 64, Theme.DARK_GRAY)}",
        f"{c('Layer-2 Frame Bit Analysis:', Theme.BOLD, Theme.YELLOW)}",
        f"  • Transmission : {c(audit['type'], Theme.WHITE)} {badge('OK' if not audit['multicast'] else 'MULTICAST', 'green' if not audit['multicast'] else 'red')}",
        f"  • Admin Scope  : {c(audit['admin_scope'], Theme.WHITE)}",
        f"{c('─' * 64, Theme.DARK_GRAY)}",
        f"{c('Privacy & Anonymity Rating:', Theme.BOLD, Theme.YELLOW)}",
        f"  • Score        : {c(audit['privacy'], Theme.BOLD, Theme.GREEN if audit['laa'] else Theme.RED)}",
        f"  • Threat Vector: {c(audit['tracking_risk'], Theme.GRAY)}",
    ]

    print()
    draw_box(f"SECURITY & PRIVACY AUDIT // {iface.upper()}", lines, border_color=Theme.MAGENTA)
    print()


def render_diff_card(iface: str, old_mac: str, new_mac: str, action: str):
    """Display visual before-and-after diff card when MAC is modified."""
    # Compare octets to highlight changes
    old_parts = old_mac.split(":")
    new_parts = new_mac.split(":")
    
    diff_new = []
    for o, n in zip(old_parts, new_parts):
        if o != n:
            diff_new.append(c(n, Theme.BOLD, Theme.GREEN))
        else:
            diff_new.append(c(n, Theme.GRAY))
    highlighted_new = ":".join(diff_new)

    lines = [
        f"{c('Operation:    ', Theme.GRAY)} {badge(action, 'cyan')} on interface {c(iface, Theme.BOLD, Theme.WHITE)}",
        f"{c('Previous MAC: ', Theme.GRAY)} {c(old_mac, Theme.RED)} ({lookup_vendor(old_mac)})",
        f"{c('Applied MAC:  ', Theme.GRAY)} {highlighted_new} ({lookup_vendor(new_mac)})",
        f"{c('Verification: ', Theme.GRAY)} {badge('VERIFIED VIA KERNEL', 'green')}",
    ]
    print()
    draw_box("OPERATION COMPLETED // VISUAL DIFF", lines, border_color=Theme.GREEN)
    print()


def render_operations_log():
    """Display audit trail from operations.log."""
    if not LOG_FILE.exists() or LOG_FILE.stat().st_size == 0:
        print(f"\n{badge('INFO', 'cyan')} No operations logged yet in {LOG_FILE}.\n")
        return

    content = LOG_FILE.read_text(encoding="utf-8").strip().splitlines()
    recent = content[-15:]  # show last 15 events

    headers = ["Timestamp", "Status", "Action", "Iface", "Target MAC"]
    col_widths = [22, 10, 14, 10, 19]
    rows = []

    for line in recent:
        m = re.search(r"\[(.*?)\]\s+\[(.*?)\]\s+ACTION=(\S+)\s+IFACE=(\S+)\s+(?:OLD=(\S+)\s+)?NEW=(\S+)", line)
        if m:
            stamp, status, act, ifc, _, new_m = m.groups()
            st_badge = badge(status, "green" if status == "SUCCESS" else "red")
            rows.append([
                c(stamp[:19], Theme.GRAY),
                st_badge,
                c(act, Theme.BOLD, Theme.CYAN),
                c(ifc, Theme.WHITE),
                c(new_m, Theme.YELLOW)
            ])
        else:
            # Raw log fallback
            rows.append([c(line[:22], Theme.GRAY), badge("LOG", "gray"), "RAW", "-", line[25:44]])

    print(f"\n{c('=== AUDIT TRAIL // RECENT OPERATIONS ===', Theme.BOLD, Theme.CYAN)}")
    draw_table(headers, rows, col_widths)
    print()


def prompt_select_interface() -> str:
    """Interactive selector for network interfaces."""
    names = get_interfaces()
    if not names:
        raise RuntimeError("No non-loopback network interfaces detected.")

    if len(names) == 1:
        return names[0]

    print(f"\n{c('Available Interfaces:', Theme.BOLD, Theme.CYAN)}")
    for i, name in enumerate(names, 1):
        details = get_interface_details(name)
        spoof_tag = badge("SPOOFED", "magenta") if details["is_spoofed"] else badge("FACTORY", "cyan")
        print(f"  {c(str(i), Theme.BOLD, Theme.YELLOW)}. {c(name, Theme.BOLD, Theme.WHITE):<12} {details['current_mac']} {spoof_tag}")

    choice = input(f"\n{c('Select interface [1-' + str(len(names)) + ']: ', Theme.BOLD, Theme.WHITE)}").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(names):
        raise ValueError("Invalid interface selection index.")
    return names[int(choice) - 1]


def prompt_vendor_menu() -> str:
    """Interactive vendor masquerading preset menu."""
    presets = [
        ("Apple Inc.", "a4:83:e7"),
        ("Intel Corporate (Wi-Fi)", "48:51:b7"),
        ("Cisco Systems", "00:1a:a1"),
        ("Samsung Electronics", "50:01:d9"),
        ("Google Inc.", "3c:5a:37"),
        ("Raspberry Pi Foundation", "dc:a6:32"),
        ("TP-Link Technologies", "50:c7:bf"),
        ("Microsoft Corporation", "00:15:5d"),
    ]

    print(f"\n{c('Select Hardware Vendor Spoofing Profile:', Theme.BOLD, Theme.CYAN)}")
    for i, (vname, prefix) in enumerate(presets, 1):
        print(f"  {c(str(i), Theme.BOLD, Theme.YELLOW)}. {c(vname, Theme.BOLD, Theme.WHITE):<26} {c('(OUI: ' + prefix + ')', Theme.GRAY)}")

    choice = input(f"\n{c('Select vendor profile [1-' + str(len(presets)) + ']: ', Theme.BOLD, Theme.WHITE)}").strip()
    if not choice.isdigit() or not 1 <= int(choice) <= len(presets):
        raise ValueError("Invalid vendor choice.")
    selected_name, prefix = presets[int(choice) - 1]
    return generate_vendor_mac(prefix), selected_name


# ──────────────────────────────────────────────────────────────────────────────
# MAIN INTERACTIVE TUI LOOP
# ──────────────────────────────────────────────────────────────────────────────

def interactive_menu():
    """Main interactive TUI loop with styled options."""
    require_tools()
    clear_screen()
    print_banner()

    menu_items = [
        ("1", "🌐", "Interfaces Dashboard", "Inspect all network adapters, IPs, and MAC states"),
        ("2", "🔍", "Deep Security Audit", "Analyze MAC privacy, OUI exposure, and LAA bit status"),
        ("3", "🎲", "Quick Random Spoof", "Apply a valid locally administered unicast random MAC"),
        ("4", "🎭", "Vendor Masquerade", "Spoof as Apple, Cisco, Intel, Samsung, Google, etc."),
        ("5", "✍️ ", "Custom MAC Address", "Specify a targeted MAC with real-time format validation"),
        ("6", "🔄", "Restore Factory MAC", "Reset adapter to original permanent hardware address"),
        ("7", "⚡", "Toggle Interface", "Safely bring interface UP or DOWN (cycling links)"),
        ("8", "📜", "View Operations Log", "Display chronological audit history and logged changes"),
        ("9", "🚪", "Exit", "Close MAC Changer"),
    ]

    while True:
        print(f"{c('MAIN OPERATIONS MENU:', Theme.BOLD, Theme.CYAN)}")
        for num, icon, title, desc in menu_items:
            print(f"  {c(num + '.', Theme.BOLD, Theme.YELLOW)} {icon} {c(title, Theme.BOLD, Theme.WHITE):<22} {c(desc, Theme.GRAY)}")
        print()

        try:
            choice = input(f"{c('kali@sec', Theme.GREEN)}{c(':', Theme.WHITE)}{c('~/mac-changer', Theme.BLUE)}{c('$ ', Theme.YELLOW)}").strip()

            if choice == "1":
                render_interfaces_dashboard()
                print()

            elif choice == "2":
                iface = prompt_select_interface()
                render_security_audit(iface)

            elif choice == "3":
                iface = prompt_select_interface()
                new_mac = generate_random_mac()
                confirm = input(f"Apply random MAC {c(new_mac, Theme.CYAN)} to {iface}? [y/N]: ").strip().lower()
                if confirm == "y":
                    before, after = change_mac(iface, new_mac)
                    render_diff_card(iface, before, after, "RANDOM_SPOOF")
                else:
                    print(c("Action cancelled.", Theme.YELLOW))

            elif choice == "4":
                iface = prompt_select_interface()
                new_mac, vendor_name = prompt_vendor_menu()
                confirm = input(f"Masquerade as {c(vendor_name, Theme.BOLD, Theme.GREEN)} ({c(new_mac, Theme.CYAN)}) on {iface}? [y/N]: ").strip().lower()
                if confirm == "y":
                    before, after = change_mac(iface, new_mac)
                    render_diff_card(iface, before, after, f"VENDOR_SPOOF ({vendor_name})")
                else:
                    print(c("Action cancelled.", Theme.YELLOW))

            elif choice == "5":
                iface = prompt_select_interface()
                details = get_interface_details(iface)
                print(f"Current MAC: {c(details['current_mac'], Theme.CYAN)}")
                raw_mac = input("Enter target MAC (or press Enter for random): ").strip()
                new_mac = generate_random_mac() if not raw_mac else validate_mac(raw_mac)
                confirm = input(f"Apply MAC {c(new_mac, Theme.CYAN)} to {iface}? [y/N]: ").strip().lower()
                if confirm == "y":
                    before, after = change_mac(iface, new_mac)
                    render_diff_card(iface, before, after, "CUSTOM_SPOOF")
                else:
                    print(c("Action cancelled.", Theme.YELLOW))

            elif choice == "6":
                iface = prompt_select_interface()
                confirm = input(f"{c('Restore permanent factory MAC for ' + iface + '? [y/N]: ', Theme.YELLOW)}").strip().lower()
                if confirm == "y":
                    before, after = restore_mac(iface)
                    render_diff_card(iface, before, after, "FACTORY_RESTORE")
                else:
                    print(c("Action cancelled.", Theme.YELLOW))

            elif choice == "7":
                iface = prompt_select_interface()
                details = get_interface_details(iface)
                print(f"Current state of {iface}: {badge(details['state'], 'green' if details['state'] == 'UP' else 'gray')}")
                target_state = "down" if details["state"] == "UP" else "up"
                confirm = input(f"Set {iface} to {target_state.upper()}? [y/N]: ").strip().lower()
                if confirm == "y":
                    toggle_interface(iface, target_state)
                    print(f"\n{badge('SUCCESS', 'green')} Interface {iface} set to {target_state.upper()}.\n")
                else:
                    print(c("Action cancelled.", Theme.YELLOW))

            elif choice == "8":
                render_operations_log()

            elif choice == "9" or choice.lower() in ("exit", "quit", "q"):
                print(c("\n[+] Exiting MAC Changer. Happy hunting!", Theme.GREEN, Theme.BOLD))
                return

            else:
                print(c(f"[-] Invalid option '{choice}'. Please choose 1-9.", Theme.RED))

        except (ValueError, RuntimeError, OSError) as err:
            print(f"\n{badge('ERROR', 'red')} {err}\n")
            log_operation("ERROR", "-", "-", "-", str(err))
        except KeyboardInterrupt:
            print(c("\n\n[!] Session interrupted by user. Exiting.\n", Theme.YELLOW))
            return


# ──────────────────────────────────────────────────────────────────────────────
# CLI ENTRYPOINT
# ──────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Stealth Layer-2 Suite & Security Auditor for Kali Linux",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python3 mac_changer.py                      # Launch interactive TUI\n"
               "  python3 mac_changer.py --list               # Display interfaces dashboard\n"
               "  sudo python3 mac_changer.py -i eth0 -r      # Apply random MAC to eth0\n"
               "  sudo python3 mac_changer.py -i eth0 --vendor apple  # Masquerade as Apple device\n"
               "  sudo python3 mac_changer.py -i eth0 --restore       # Restore factory hardware MAC\n"
    )
    parser.add_argument("--list", "-l", action="store_true", help="Display interactive interfaces dashboard")
    parser.add_argument("--interface", "-i", help="Target network interface")
    parser.add_argument("--random", "-r", action="store_true", help="Apply a random locally administered MAC")
    parser.add_argument("--mac", "-m", help="Apply a specific MAC address (XX:XX:XX:XX:XX:XX)")
    parser.add_argument("--vendor", help="Masquerade as vendor (apple, cisco, intel, samsung, google, rpi)")
    parser.add_argument("--restore", action="store_true", help="Restore permanent factory MAC")
    parser.add_argument("--audit", action="store_true", help="Perform deep security and privacy audit on interface")
    parser.add_argument("--json", action="store_true", help="Output interface and MAC details in JSON format")

    args = parser.parse_args()

    try:
        require_tools()

        # JSON mode
        if args.json:
            iface = args.interface or (get_interfaces()[0] if get_interfaces() else None)
            if not iface:
                print(json.dumps({"error": "No interfaces found"}))
                return 1
            details = get_interface_details(iface)
            details["audit"] = analyze_mac_security(details["current_mac"])
            print(json.dumps(details, indent=2))
            return 0

        # List mode
        if args.list:
            render_interfaces_dashboard()
            return 0

        # Non-interactive interface operations
        if args.interface:
            iface = args.interface
            if iface not in get_interfaces():
                raise ValueError(f"Interface '{iface}' not found.")

            if args.audit:
                render_security_audit(iface)
                return 0

            if args.restore:
                before, after = restore_mac(iface)
                render_diff_card(iface, before, after, "FACTORY_RESTORE")
                return 0

            if args.vendor:
                vendor_map = {
                    "apple": "a4:83:e7",
                    "cisco": "00:1a:a1",
                    "intel": "48:51:b7",
                    "samsung": "50:01:d9",
                    "google": "3c:5a:37",
                    "rpi": "dc:a6:32",
                }
                prefix = vendor_map.get(args.vendor.lower())
                if not prefix:
                    raise ValueError(f"Unknown vendor preset '{args.vendor}'. Available: {', '.join(vendor_map.keys())}")
                new_mac = generate_vendor_mac(prefix)
                before, after = change_mac(iface, new_mac)
                render_diff_card(iface, before, after, f"VENDOR_SPOOF ({args.vendor.upper()})")
                return 0

            if args.random:
                new_mac = generate_random_mac()
                before, after = change_mac(iface, new_mac)
                render_diff_card(iface, before, after, "RANDOM_SPOOF")
                return 0

            if args.mac:
                new_mac = validate_mac(args.mac)
                before, after = change_mac(iface, new_mac)
                render_diff_card(iface, before, after, "CUSTOM_SPOOF")
                return 0

            # Default: show audit and current MAC
            render_security_audit(iface)
            return 0

        # No arguments: launch full interactive TUI
        interactive_menu()
        return 0

    except (ValueError, RuntimeError, OSError) as e:
        print(f"\n{badge('ERROR', 'red')} {e}\n", file=sys.stderr)
        log_operation("ERROR", "-", "-", "-", str(e))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
