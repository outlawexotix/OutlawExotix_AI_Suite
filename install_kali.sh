#!/bin/bash
echo -e "\e[31m>> OUTLAW EXOTIX // KALI DEPLOYMENT PROTOCOL <<\e[0m"

# 1. Install System Dependencies
echo "[*] Installing Dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip nodejs npm git

# 2. Install Python Libraries
echo "[*] Installing Python Assets..."
pip3 install google-generativeai colorama --break-system-packages

# 3. Install Claude Code CLI (if missing)
if ! command -v claude &> /dev/null; then
    echo "[*] Installing Claude Code CLI..."
    sudo npm install -g @anthropic-ai/claude-code
fi

# 4. Setup Directories
echo "[*] Constructing Architecture (~/.claude)..."
mkdir -p ~/.claude/tools
mkdir -p ~/.claude/templates
mkdir -p ~/.local/bin

# 5. Copy Assets
echo "[*] Deploying Tools and Personas..."
# Assuming script is run from repo root
cp tools/*.py ~/.claude/tools/
cp templates/*.md ~/.claude/templates/
cp memory_protocol.md ~/.claude/

# 6. Deploy Agent Launcher
cp bin/agent.sh ~/.local/bin/agent
chmod +x ~/.local/bin/agent

# 7. Create 'battlecry' Alias
echo "[*] Injecting Battle Cry Alias..."
SHELL_CONFIG="$HOME/.zshrc"
if [ ! -f "$SHELL_CONFIG" ]; then
    SHELL_CONFIG="$HOME/.bashrc"
fi

if ! grep -q "battlecry" "$SHELL_CONFIG"; then
    echo "alias battlecry='python3 ~/.claude/tools/war_room.py'" >> "$SHELL_CONFIG"
    echo "Alias injected into $SHELL_CONFIG"
else
    echo "Alias already exists."
fi

echo -e "\e[32m[+] DEPLOYMENT COMPLETE. RELOAD YOUR SHELL AND TYPE 'battlecry'.\e[0m"
