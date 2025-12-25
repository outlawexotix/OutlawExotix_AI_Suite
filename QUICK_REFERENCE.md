# Quick Reference Guide

## GitHub Commands

### OAuth Authorization
```bash
gh auth login
```
**Purpose:** Authenticates with GitHub using OAuth 2.0 flow. This is the primary command for authorizing the GitHub CLI to access your GitHub account.

**What it does:**
- Initiates OAuth 2.0 authorization flow
- Opens your browser for authentication
- Creates secure access tokens
- Stores credentials for future use

**When to use:**
- First time setup
- After credentials expire
- When switching GitHub accounts
- When setting up on a new machine

### Check Authentication Status
```bash
gh auth status
```
Shows current authentication status for all configured GitHub hosts.

### Logout
```bash
gh auth logout
```
Removes stored credentials and logs out from GitHub.

### Refresh Authentication
```bash
gh auth refresh
```
Refreshes your authentication credentials without re-logging in.

---

## War Room Commands

### Launch War Room
```bash
python tools/war_room.py
# OR with alias
battlecry
```

### Query Gemini Directly
```bash
python tools/gemini_bridge.py "Your question here"
```

### Query Codex/OpenAI
```bash
python tools/codex_bridge.py "Your question here"
```

### Launch an Agent (Windows)
```powershell
pwsh ./bin/agent.ps1 -Name overwatch -p "Scan this repo"
```

### Launch an Agent (Linux/Mac)
```bash
./bin/agent.sh overwatch "Scan this repo"
```

---

## Available Agents

- **COMMANDER** - Chief of Staff (delegator)
- **OVERWATCH** - Strategist (checks Gemini before acting)
- **APEX ANALYST** - Researcher (autonomous installs)
- **ETHICAL HACKER** - Red Team security auditor
- **CODE AUDITOR** - Blue Team quality control
- **FILE ORGANIZER** - File system management
- **SECURITY ARCHITECT** - Security design and review

---

## Testing Commands

### Run All Tests
```bash
# Windows
.\run_tests.ps1

# Linux/Mac
./run_tests.sh
```

### Run Tests with Coverage
```bash
# Windows
.\run_tests.ps1 -Coverage

# Linux/Mac
./run_tests.sh --coverage
```

### Run Specific Test Module
```bash
pytest tests/unit/test_war_room.py -v
```

---

## Environment Setup

### Required Environment Variables
```bash
# Google Gemini API Key (required)
export GOOGLE_API_KEY="your-gemini-api-key"

# OpenAI API Key (optional, for Codex bridge)
export OPENAI_API_KEY="your-openai-api-key"
```

### Python Dependencies
```bash
# Core dependencies
pip install google-generativeai colorama

# Development dependencies (for testing)
pip install -r requirements-dev.txt
```

---

## Repository Management

### Create Repository on GitHub
```bash
# Replace 'YOUR_REPO_NAME' with your desired repository name
gh repo create YOUR_REPO_NAME --public --source=. --remote=origin --push
```

### Push Changes
```bash
git push -u origin branch-name
```

### Create Pull Request
```bash
gh pr create --title "Your PR Title" --body "PR description"
```

### View Repository in Browser
```bash
gh browse
```

---

## Troubleshooting

### "Not authenticated" Error
**Solution:** Run `gh auth login` to authenticate with GitHub

### "GOOGLE_API_KEY not found" Error
**Solution:** Set environment variable or use `--api-key` flag:
```bash
python tools/gemini_bridge.py "query" --api-key YOUR_KEY
```

### "CLAUDE_EXE not found" Error
**Solution:** Edit `tools/war_room.py` and update the `CLAUDE_EXE` path to your Claude installation

### Tests Failing
**Solution:** Install development dependencies:
```bash
pip install -r requirements-dev.txt
```

---

## Quick Start Checklist

- [ ] Install Python 3.10+
- [ ] Install GitHub CLI (`gh`) - See https://cli.github.com/manual/installation
- [ ] Authenticate with GitHub: `gh auth login`
- [ ] Install Claude Code CLI - See https://docs.anthropic.com/
- [ ] Set `GOOGLE_API_KEY` environment variable
- [ ] Install Python dependencies: `pip install google-generativeai colorama`
- [ ] Copy templates to `~/.claude/templates`
- [ ] Update `CLAUDE_EXE` path in `tools/war_room.py`
- [ ] Test War Room: `python tools/war_room.py`
- [ ] Run tests: `./run_tests.sh` or `.\run_tests.ps1`

---

## Additional Resources

- [GITHUB_SETUP.md](GITHUB_SETUP.md) - Detailed GitHub setup instructions
- [README.md](README.md) - Full project documentation
- [AGENTS.md](AGENTS.md) - Repository guidelines
- [memory_protocol.md](memory_protocol.md) - Shared memory system
- [tests/README.md](tests/README.md) - Testing documentation
