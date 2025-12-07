# War Room Extension for Google Antigravity

Integrate your Outlaw Exotix AI agents directly into Google Antigravity IDE.

## Features

### 🤖 Agent Commands

Access all War Room agents via Command Palette (`Ctrl+Shift+P` / `Cmd+Shift+P`):

- **War Room: Summon Overwatch** - Strategic analysis and planning
- **War Room: Summon Ethical Hacker** - Security audits and vulnerability scanning
- **War Room: Summon Code Auditor** - Code quality reviews and best practices
- **War Room: Summon Apex Analyst** - Research and dependency management
- **War Room: Summon Chief of Staff** - Task delegation to other agents

### 🎯 Context-Aware Execution

- Right-click on selected code → Run Code Auditor or Ethical Hacker
- Agents automatically include file context and selected code
- Results streamed to dedicated Output channel

### 💾 Shared Memory Integration

- **War Room: View Shared Memory** - Open PROJECT_MEMORY.md
- Automatic notifications when memory updates
- Agents read and write to shared context

### 🧪 Testing Integration

- **War Room: Run Test Suite** - Execute pytest with coverage
- Results displayed in integrated terminal
- One-click access to test runners

### 🖥️ War Room Console

- **War Room: Open Console** - Launch full War Room terminal interface
- All War Room features available
- Gemini strategy + Claude execution

## Installation

### Option 1: From VSIX (Recommended)

```bash
# Build the extension
cd antigravity-extension
npm install
npx vsce package

# Install in Antigravity
# File → Install Extension from VSIX → select antigravity-warroom-1.0.0.vsix
```

### Option 2: Development Mode

```bash
# Link extension for development
cd antigravity-extension
npm install
npm link

# Open in Antigravity
# Help → Developer → Install Extension from Location
# Select the antigravity-extension directory
```

## Configuration

Open Antigravity Settings (`Ctrl+,` / `Cmd+,`) and search for "War Room":

```json
{
  "warroom.pythonPath": "python",
  "warroom.toolsPath": "./tools",
  "warroom.binPath": "./bin",
  "warroom.memoryFile": "./PROJECT_MEMORY.md",
  "warroom.autoShowMemory": true
}
```

## Usage Examples

### Example 1: Security Audit

1. Open a file with sensitive code
2. Select the authentication function
3. Right-click → **War Room: Summon Ethical Hacker**
4. Enter task: "Audit for SQL injection vulnerabilities"
5. View results in Output panel
6. Check PROJECT_MEMORY.md for recommendations

### Example 2: Code Review

1. Open Command Palette (`Ctrl+Shift+P`)
2. Type "War Room: Summon Code Auditor"
3. Enter task: "Review this module for best practices"
4. Agent analyzes entire file
5. Results appear in Output + Memory

### Example 3: Strategic Planning

1. Command Palette → "War Room: Summon Overwatch"
2. Enter: "Analyze the architecture of this project"
3. Overwatch consults Gemini for strategic advice
4. Recommendations saved to shared memory
5. Other agents can read the context

### Example 4: Full War Room

1. Command Palette → "War Room: Open Console"
2. Full terminal interface opens
3. Access all War Room features
4. Use `/mode`, `/execute`, `/consult` commands

## Keyboard Shortcuts

Add these to your `keybindings.json`:

```json
[
  {
    "key": "ctrl+shift+o",
    "command": "warroom.summonOverwatch",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+h",
    "command": "warroom.summonEthicalHacker",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+a",
    "command": "warroom.summonCodeAuditor",
    "when": "editorTextFocus"
  },
  {
    "key": "ctrl+shift+m",
    "command": "warroom.viewMemory"
  },
  {
    "key": "ctrl+shift+w",
    "command": "warroom.openConsole"
  }
]
```

## Architecture

```
Antigravity IDE
    ↓
War Room Extension (extension.js)
    ↓
Agent Launchers (bin/agent.sh, bin/agent.ps1)
    ↓
Agent Templates (templates/*.md)
    ↓
Claude Code CLI + Gemini API
    ↓
PROJECT_MEMORY.md (Shared Context)
```

## Requirements

- **Google Antigravity** - Download from https://antigravity.google/
- **Python 3.10+** - For War Room scripts
- **Claude Code CLI** - For agent execution
- **Google API Key** - For Gemini integration (set `GOOGLE_API_KEY` env var)

## Troubleshooting

### "Agent not found" Error

Check that `warroom.binPath` in settings points to your `bin/` directory.

### "Python not found" Error

Set `warroom.pythonPath` to the full path of your Python executable:
```json
{
  "warroom.pythonPath": "C:\\Python310\\python.exe"  // Windows
  "warroom.pythonPath": "/usr/bin/python3"          // Linux/Mac
}
```

### Agents Don't Start

1. Verify Claude Code CLI is installed: `claude --version`
2. Check templates exist: `ls templates/`
3. View extension logs: View → Output → War Room

### Memory Not Updating

1. Check `warroom.memoryFile` setting
2. Ensure agents have write permissions
3. View → Output → War Room for error messages

## Development

### Building from Source

```bash
git clone https://github.com/outlawexotix/OutlawExotix_AI_Suite.git
cd OutlawExotix_AI_Suite/antigravity-extension
npm install
npm run lint
npx vsce package
```

### Testing

```bash
npm test
```

### Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/my-feature`
3. Commit changes: `git commit -m "Add feature"`
4. Push: `git push origin feature/my-feature`
5. Open Pull Request

## License

MIT License - See LICENSE file

## Links

- **Repository:** https://github.com/outlawexotix/OutlawExotix_AI_Suite
- **Documentation:** See main README.md
- **Bug Reports:** https://github.com/outlawexotix/OutlawExotix_AI_Suite/issues

---

**Built with ❤️ by Outlaw Exotix**
