#!/usr/bin/env bash
# ==============================================================================
# MAC Changer & Security Analyzer — Kali Linux Installation Script
# ==============================================================================

set -euo pipefail

# Kali Cyber ANSI Palette
CYAN="\033[38;5;51m"
GREEN="\033[38;5;48m"
YELLOW="\033[38;5;220m"
RED="\033[38;5;196m"
GRAY="\033[38;5;244m"
BOLD="\033[1m"
RESET="\033[0m"

echo -e "\n${CYAN}${BOLD}╔══════════════════════════════════════════════════════════════════╗${RESET}"
echo -e "${CYAN}${BOLD}║     KALI LINUX // MAC CHANGER & SECURITY ANALYZER INSTALLER      ║${RESET}"
echo -e "${CYAN}${BOLD}╚══════════════════════════════════════════════════════════════════╝${RESET}\n"

echo -e "${CYAN}[*]${RESET} Verifying environment..."
if ! command -v apt >/dev/null 2>&1; then
    echo -e "${RED}[-] Error: This installer is intended for Kali / Debian-based distributions.${RESET}"
    exit 1
fi

if ! command -v sudo >/dev/null 2>&1 && [ "$(id -u)" -ne 0 ]; then
    echo -e "${RED}[-] Error: sudo or root privileges are required to install packages.${RESET}"
    exit 1
fi

echo -e "${GREEN}[+]${RESET} Environment verified (Debian/Kali Linux)."

echo -e "${CYAN}[*]${RESET} Updating package repositories..."
sudo apt update -qq

echo -e "${CYAN}[*]${RESET} Installing required system packages (python3, iproute2, macchanger)..."
sudo apt install -y python3 iproute2 macchanger

echo -e "${CYAN}[*]${RESET} Preparing directories and permissions..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
mkdir -p "${SCRIPT_DIR}/logs" "${SCRIPT_DIR}/screenshots"
touch "${SCRIPT_DIR}/logs/operations.log"
chmod +x "${SCRIPT_DIR}/mac_changer.py"
chmod 700 "${SCRIPT_DIR}/logs"

# Offer global symlink installation
echo -e "${CYAN}[*]${RESET} Installing global command shortcut ${GREEN}mac-changer${RESET} to /usr/local/bin..."
if sudo ln -sf "${SCRIPT_DIR}/mac_changer.py" /usr/local/bin/mac-changer; then
    echo -e "${GREEN}[+]${RESET} Shortcut created: You can now type ${CYAN}${BOLD}mac-changer${RESET} from anywhere!"
else
    echo -e "${YELLOW}[!]${RESET} Could not create symlink in /usr/local/bin (non-critical)."
fi

echo -e "\n${GREEN}${BOLD}════════════════════════════════════════════════════════════════════${RESET}"
echo -e "${GREEN}${BOLD} [✓] INSTALLATION COMPLETE! READY FOR KALI TERMINAL USE           ${RESET}"
echo -e "${GREEN}${BOLD}════════════════════════════════════════════════════════════════════${RESET}\n"

echo -e "  ${YELLOW}• Interactive Cyber TUI:${RESET}    ${BOLD}sudo mac-changer${RESET}  (or: python3 mac_changer.py)"
echo -e "  ${YELLOW}• Interfaces Dashboard:${RESET}     ${BOLD}mac-changer --list${RESET}"
echo -e "  ${YELLOW}• Quick Random Spoof:${RESET}       ${BOLD}sudo mac-changer -i eth0 -r${RESET}"
echo -e "  ${YELLOW}• Vendor Masquerade (Apple):${RESET} ${BOLD}sudo mac-changer -i eth0 --vendor apple${RESET}"
echo -e "  ${YELLOW}• Security & Privacy Audit:${RESET}  ${BOLD}mac-changer -i eth0 --audit${RESET}"
echo -e "  ${YELLOW}• Restore Factory MAC:${RESET}       ${BOLD}sudo mac-changer -i eth0 --restore${RESET}\n"
