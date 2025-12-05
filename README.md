# ?? OUTLAW EXOTIX AI SUITE (WAR ROOM)

**"Two AIs, One Terminal, Total Domination."**

This suite integrates **Claude Code CLI** (Execution) and **Google Gemini API** (Strategy) into a single, unified "War Room" console (`battlecry`). It also provides a squad of specialized AI agents for autonomous operations.

## ?? Repository Structure

*   `tools/`: Python scripts for the War Room and Gemini Bridge.
*   `templates/`: Agent Personas (Ethical Hacker, Code Auditor, etc.).
*   `bin/`: PowerShell launcher scripts.
*   `memory_protocol.md`: The "Mnemosyne" system for shared AI memory.

## ?? Installation

1.  **Prerequisites:**
    *   Python 3.10+ (`pip install google-generativeai colorama`)
    *   Claude Code CLI (`npm install -g @anthropic-ai/claude-code` OR native installer)
    *   Google Gemini API Key (`GOOGLE_API_KEY` env var)

2.  **Setup:**
    *   Copy `tools/*.py` to your preferred tools directory (e.g., `~/.claude/tools`).
    *   Copy `templates/*.md` to `~/.claude/templates`.
    *   Edit `tools/war_room.py` and update `CLAUDE_EXE` to point to your Claude executable.

3.  **The "Battle Cry" Alias:**
    Add this to your PowerShell profile:
    ```powershell
    Set-Alias -Name battlecry -Value 'python Path\To\tools\war_room.py'
    ```

## ?? The Agents

*   **COMMANDER (Chief of Staff):** Delegator. Runs other agents.
*   **OVERWATCH:** Strategist. Checks Gemini before acting.
*   **APEX ANALYST:** Researcher. Installs apps/dependencies autonomously.
*   **ETHICAL HACKER:** Red Team security auditor.
*   **CODE AUDITOR:** Blue Team quality control.

## ?? Usage

**Enter the War Room:**
```powershell
battlecry
```

**Summon an Agent:**
```powershell
agent overwatch -p "Scan this directory."
```

## ?? License
Outlaw Exotix Internal / MIT
