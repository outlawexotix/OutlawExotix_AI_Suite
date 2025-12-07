# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

The **Outlaw Exotix AI Suite (War Room)** is a dual-AI orchestration system that integrates Claude Code CLI (execution) with Google Gemini API (strategy). It provides:

1. **War Room Console** - Interactive terminal that combines Gemini strategic analysis with Claude execution
2. **Agent System** - Specialized AI personas with distinct roles and capabilities
3. **Mnemosyne Memory Protocol** - Shared persistent memory across all agents via `PROJECT_MEMORY.md`

## Architecture

### Core Components

**War Room Flow** (`tools/war_room.py`):
```
User Input → Gemini (Strategic Advice) → Claude (Execution with Context) → Output
```

**Agent Invocation** (`bin/agent.sh` or `bin/agent.ps1`):
```
Agent Template + Memory Protocol → Combined System Prompt → Claude Execution
```

**Memory System** (`tools/log_memory.py` + `tools/gemini_bridge.py`):
- Claude writes to `PROJECT_MEMORY.md` after significant actions
- Gemini reads from `PROJECT_MEMORY.md` for context-aware responses
- Creates continuous context across sessions

### Directory Structure

- **`tools/`** - Python scripts for War Room, Gemini bridge, and memory logging
- **`templates/`** - Agent persona markdown files (system prompts)
- **`bin/`** - Shell launchers for agents (PowerShell & Bash)
- **`memory_protocol.md`** - Instructions for agents on using shared memory

## Development Commands

### Testing the War Room Console
```bash
# Windows (PowerShell)
python tools/war_room.py

# Linux/macOS
python3 tools/war_room.py
```

### Testing Individual Agents
```bash
# Windows (PowerShell)
.\bin\agent.ps1 -Name overwatch -p "Analyze this directory"

# Linux/macOS
./bin/agent.sh overwatch -p "Analyze this directory"
```

### Testing Gemini Bridge Standalone
```bash
# Requires GOOGLE_API_KEY environment variable
python tools/gemini_bridge.py "Describe this project's architecture"
```

### Testing Memory Logging
```bash
python tools/log_memory.py "Test entry: Refactored war_room.py for cross-platform support"
```

## Critical Configuration Points

### War Room (`tools/war_room.py`)

**Line 12-16**: Claude executable path detection
```python
if os.name == "nt":
    CLAUDE_EXE = r"C:\Users\penne\.local\bin\claude.exe"
else:
    CLAUDE_EXE = shutil.which("claude") or "claude"
```
- Update `CLAUDE_EXE` path if Claude is installed elsewhere
- Current default: `C:\Users\penne\.local\bin\claude.exe`

### Agent Launchers

**PowerShell** (`bin/agent.ps1` line 7-8):
```powershell
$TemplatePath = "C:\Users\penne\.claude\templates\$Name.md"
$MemoryProtocolPath = "C:\Users\penne\.claude\memory_protocol.md"
```

**Bash** (`bin/agent.sh` line 5-6):
```bash
TEMPLATE_PATH="$HOME/.claude/templates/${AGENT_NAME}.md"
MEMORY_PATH="$HOME/.claude/memory_protocol.md"
```
- These assume standard installation at `~/.claude/`
- Update if deploying to custom location

### Gemini Bridge (`tools/gemini_bridge.py`)

**Line 33**: Model selection
```python
model = genai.GenerativeModel('gemini-1.5-flash')
```
- Uses `gemini-1.5-flash` for speed
- Can upgrade to `gemini-1.5-pro` for complex analysis (slower, more capable)

**Line 21-26**: Context window for shared memory
```python
memory = f.read()[-3000:]  # Last 3000 chars
```
- Adjust character limit based on token budget needs

## Agent System Architecture

### Agent Invocation Chain

1. **User calls agent launcher** with agent name + arguments
2. **Launcher reads two files**:
   - Agent persona template (`templates/{agent-name}.md`)
   - Memory protocol (`memory_protocol.md`)
3. **Files are concatenated** into a single system prompt
4. **Claude is executed** with combined prompt + user arguments
5. **Agent operates** under its persona constraints with memory awareness

### Available Agents

- **`chief-of-staff`** - Delegator, orchestrates other agents
- **`overwatch`** - Strategist, analyzes root causes, consults Gemini before acting
- **`apex-analyst`** - Researcher, installs dependencies, reads docs
- **`ethical-hacker`** - Red team security auditor
- **`code-auditor`** - Blue team code reviewer
- **`file-organizer`** - Cleanup and file management
- **`security-architect`** - System-level security design

### Creating New Agents

1. Create `templates/new-agent-name.md` with:
   - `# IDENTITY:` section defining role
   - `## CORE DIRECTIVE` describing purpose
   - `## CAPABILITIES` listing available tools
   - `## OPERATIONAL PROTOCOLS` defining behavior rules
2. Agent immediately available via `agent new-agent-name -p "..."`

## Memory Protocol (Mnemosyne System)

### When to Log Memory

Agents should log after:
- Installing packages/dependencies
- Creating or significantly modifying files
- Fixing bugs or completing features
- Making architectural decisions
- Discovering important project insights

### How to Log
```bash
python C:\Users\penne\.claude\tools\log_memory.py "Summary of action taken"
```

### Memory File Location
- Default: `./PROJECT_MEMORY.md` (in current working directory)
- Format: Markdown with timestamped entries

### Context Injection Points

1. **Gemini Bridge** reads memory in `get_context()` function (line 15-26)
2. **War Room** does NOT auto-inject memory (manual only)
3. **Agents** are instructed via `memory_protocol.md` to read/write

## Cross-Platform Considerations

### Path Separators
- War Room uses `os.path.join()` for cross-platform paths
- Agent launchers have separate `.sh` (Unix) and `.ps1` (Windows) versions

### Shell Commands
War Room detects OS:
```python
if os.name == "nt":  # Windows
    cmd = ["powershell", "-Command", ...]
else:  # Unix
    cmd = [CLAUDE_EXE, ...]
```

### Installation Scripts
- **Linux/macOS**: `install_kali.sh` (Debian/Ubuntu focused)
- **Windows**: Manual setup via README instructions

## Extending the War Room

### Adding Gemini Context Sources

Edit `gemini_bridge.py` `get_context()` function to include:
- Git status/branch info
- Environment variables
- Active services/processes
- Custom project metadata

### Customizing War Room Behavior

**Pre-processing prompts** (line 37-38):
```python
gemini_prompt = f"Strategic Advice for: {user_input}"
combined_prompt = f"REQUEST: {user_input}\nADVICE: {gemini_process.stdout}"
```

Modify these templates to change how Gemini/Claude receive instructions.

### Changing UI/UX

**Header** (`draw_header()` function) - ASCII art banner
**Prompt** (line 31) - `COMMANDER >` prefix
**Colors** - Uses `colorama` library (RED, GREEN, CYAN)

## Security Considerations

### API Keys
- Gemini requires `GOOGLE_API_KEY` environment variable
- Never commit API keys to repository
- Use environment variables or secrets management

### Dangerous Permissions Flag
War Room uses `--dangerously-skip-permissions` flag on line 45 for Claude.
- **Risk**: Bypasses file access confirmations
- **Reason**: Enables autonomous agent operation
- **Mitigation**: Only use in controlled environments

## Common Development Tasks

### Add a new agent tool capability
1. Edit the agent's template in `templates/`
2. Add new command to `## CAPABILITIES` section
3. Update `## OPERATIONAL PROTOCOLS` with usage rules

### Change default Claude path system-wide
Update BOTH:
- `tools/war_room.py` (lines 12-16)
- `bin/agent.ps1` (line 21) or `bin/agent.sh` (line 16 in claude command)

### Increase Gemini context window
Edit `gemini_bridge.py` line 21:
```python
memory = f.read()[-5000:]  # Increase from 3000 to 5000
```

### Switch Gemini model
Edit `gemini_bridge.py` line 33:
```python
model = genai.GenerativeModel('gemini-1.5-pro')  # More capable, slower
```

### Debug agent invocation
Check combined system prompt being sent to Claude:
```bash
# Temporarily add print statement in agent launcher before claude execution
cat ~/.claude/templates/overwatch.md ~/.claude/memory_protocol.md
```

## Troubleshooting

**War Room fails to launch**:
- Verify `CLAUDE_EXE` path in `war_room.py` points to valid Claude executable
- Check Python dependencies: `pip install google-generativeai colorama`

**Gemini bridge returns errors**:
- Confirm `GOOGLE_API_KEY` environment variable is set
- Test API key: `python -c "import os; print(os.getenv('GOOGLE_API_KEY'))"`

**Agent not found**:
- Verify template exists: `ls ~/.claude/templates/{agent-name}.md`
- Check `memory_protocol.md` exists in `~/.claude/`

**Memory not persisting**:
- Ensure `PROJECT_MEMORY.md` is in current working directory
- Check write permissions on directory
- Verify `log_memory.py` path is correct in agent instructions

**Cross-platform path issues**:
- Use forward slashes in Python code (auto-converts)
- Use `os.path.join()` for constructing paths
- Check line endings (LF vs CRLF) in shell scripts
