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
    *   Google Gemini API Key (`GOOGLE_API_KEY` env var) OR a Google Cloud Project for OAuth.

2.  **Setup:**
    *   Copy `tools/*.py` to your preferred tools directory (e.g., `~/.claude/tools`).
    *   Copy `templates/*.md` to `~/.claude/templates`.
    *   Edit `tools/war_room.py` and update `CLAUDE_EXE` to point to your Claude executable.

3.  **The "Battle Cry" Alias:**
    Add this to your PowerShell profile:
    ```powershell
    Sets-Alias -Name battlecry -Value 'python Path\To\tools\war_room.py'
    ```

### Authentication Options
You can authenticate with Gemini in two ways:
1.  **API Key (Simplest):** Set `GOOGLE_API_KEY` environment variable.
2.  **Native OAuth (Recommended):**
    *   Download your OAuth 2.0 Client ID JSON from Google Cloud Console.
    *   Rename it to `client_secret.json` and place it in the project root.
    *   Run any command; a browser window will open for you to sign in.
    *   Authentication is cached in `token.json`.

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

## ?? Testing

This project includes a comprehensive test suite with **56 passing tests** and **37% code coverage**.

### Quick Start
```bash
# Windows
.\run_tests.ps1 -Coverage

# Linux/Mac
./run_tests.sh --coverage
```

### Test Results
- ✓ **56 tests passing** (91.8% pass rate)
- ✓ **5 tests skipped** (OpenAI library not installed)
- ✓ **37% code coverage** baseline established
- ✓ **4 security vulnerabilities patched**

See [FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md) for complete test results and [tests/README.md](tests/README.md) for test documentation.

### Security Fixes
- ✓ Path traversal prevention in agent launchers
- ✓ Shell injection hardening in war_room.py
- ✓ File locking in log_memory.py
- ✓ Removed duplicate code in gemini_bridge.py

## ?? License
Outlaw Exotix Internal / MIT
