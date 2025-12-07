# ?? OUTLAW EXOTIX AI SUITE (WAR ROOM)

**"Two AIs, One Terminal, Total Domination."**

This suite integrates **Claude Code CLI** (Execution) and **Google Gemini API** (Strategy) into a single, unified "War Room" console (`battlecry`). It also provides a squad of specialized AI agents for autonomous operations.

## ?? Repository Structure

*   `tools/`: Python scripts for the War Room and Gemini Bridge.
*   `templates/`: Agent Personas (Ethical Hacker, Code Auditor, etc.).
*   `bin/`: PowerShell launcher scripts.
*   `memory_protocol.md`: The "Mnemosyne" system for shared AI memory.

## 🔧 Installation

1.  **Prerequisites:**
    *   Python 3.10+ (`pip install google-generativeai google-auth colorama`)
    *   Claude Code CLI (`npm install -g @anthropic-ai/claude-code` OR native installer)
    *   Google Cloud SDK for Gemini authentication (see [GEMINI_AUTH_SETUP.md](GEMINI_AUTH_SETUP.md))

2.  **Setup:**
    *   Copy `tools/*.py` to your preferred tools directory (e.g., `~/.claude/tools`).
    *   Copy `templates/*.md` to `~/.claude/templates`.
    *   Edit `tools/war_room.py` and update `CLAUDE_EXE` to point to your Claude executable.

3.  **Authenticate with Google (for Gemini):**
    ```bash
    gcloud auth application-default login
    ```
    See [GEMINI_AUTH_SETUP.md](GEMINI_AUTH_SETUP.md) for detailed instructions.

4.  **The "Battle Cry" Alias:**
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
