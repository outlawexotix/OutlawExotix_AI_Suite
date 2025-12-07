# Google Antigravity Integration - Quick Start Guide

## ✓ Upgrades Completed

Your Outlaw Exotix AI Suite has been upgraded for Google Antigravity integration!

### What's New

1. **Gemini 3 Pro Support** - `tools/gemini_bridge.py` now defaults to `gemini-3-pro`
2. **Antigravity Extension** - Full VS Code extension in `antigravity-extension/`
3. **Complete Documentation** - `ANTIGRAVITY_INTEGRATION.md` with detailed guides

---

## Option 1: Quick Integration (No Installation Required)

### Just use Antigravity's Terminal

1. **Download Antigravity:** https://antigravity.google/
2. **Open your project:**
   ```bash
   antigravity /path/to/OutlawExotix_AI_Suite
   ```
3. **Open integrated terminal** in Antigravity (`Ctrl+` ` or View → Terminal)
4. **Run War Room:**
   ```bash
   python tools/war_room.py
   ```
5. **Use agents:**
   ```bash
   agent overwatch -p "Analyze this codebase"
   ```

**Done!** Your agents now work in Antigravity.

---

## Option 2: Full Extension Installation

### Install the Extension

**Step 1: Build Extension**
```bash
cd antigravity-extension
npm install
npx vsce package
```

This creates `antigravity-warroom-1.0.0.vsix`

**Step 2: Install in Antigravity**
1. Open Antigravity
2. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
3. Type "Extensions: Install from VSIX"
4. Select `antigravity-warroom-1.0.0.vsix`
5. Reload Antigravity

### Use Extension Commands

Press `Ctrl+Shift+P` and type "War Room":

- **War Room: Summon Overwatch** - Strategic analysis
- **War Room: Summon Ethical Hacker** - Security audit
- **War Room: Summon Code Auditor** - Code review
- **War Room: Open Console** - Full War Room interface
- **War Room: Run Test Suite** - Execute tests
- **War Room: View Shared Memory** - See PROJECT_MEMORY.md

---

## Features You Get

### 🎯 Context-Aware Agents
1. Select code in editor
2. Right-click → "War Room: Summon Code Auditor"
3. Agent analyzes selected code with full context

### 💾 Shared Memory
- All agents write to `PROJECT_MEMORY.md`
- Antigravity agents can read War Room insights
- War Room agents can read Antigravity work
- Unified context across tools

### 🔄 Gemini 3 Pro
- Upgraded from `gemini-1.5-flash` to `gemini-3-pro`
- Better strategic analysis
- Improved code understanding
- Latest Google AI capabilities

### 🧪 Integrated Testing
- Run test suite from Antigravity
- View coverage reports
- 56 tests, 37% coverage baseline

---

## Configuration

### Set Your API Keys

**Google API Key (Gemini 3):**
```bash
# Windows PowerShell
$env:GOOGLE_API_KEY="your-key-here"

# Linux/Mac
export GOOGLE_API_KEY="your-key-here"
```

**Claude API Key (Optional):**
If using Claude in Antigravity directly, set:
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

### Extension Settings

In Antigravity Settings (`Ctrl+,`):

```json
{
  "warroom.pythonPath": "python",
  "warroom.toolsPath": "./tools",
  "warroom.binPath": "./bin",
  "warroom.memoryFile": "./PROJECT_MEMORY.md",
  "warroom.autoShowMemory": true
}
```

---

## Example Workflow

### Scenario: Build a Feature with Security

**1. In Antigravity IDE:**
```
Use Antigravity's AI to generate authentication code
```

**2. In War Room Terminal:**
```bash
agent ethical-hacker -p "Security audit new auth code"
```

**3. Back in Antigravity:**
```
Read PROJECT_MEMORY.md for security findings
Fix vulnerabilities highlighted by Ethical Hacker
```

**4. Run Tests:**
```bash
./run_tests.sh --coverage
```

**5. Final Review:**
```bash
agent code-auditor -p "Final quality check"
```

---

## Keyboard Shortcuts (Optional)

Add to Antigravity `keybindings.json`:

```json
[
  {
    "key": "ctrl+shift+o",
    "command": "warroom.summonOverwatch"
  },
  {
    "key": "ctrl+shift+h",
    "command": "warroom.summonEthicalHacker"
  },
  {
    "key": "ctrl+shift+m",
    "command": "warroom.viewMemory"
  }
]
```

---

## Troubleshooting

### "vsce not found"

Install vsce globally:
```bash
npm install -g @vscode/vsce
```

### "Gemini 3 not available"

Gemini 3 is in preview. If you get errors, fall back:
```bash
python tools/gemini_bridge.py -m gemini-1.5-flash "your prompt"
```

### Extension Won't Load

Check Antigravity Developer Console:
1. Help → Toggle Developer Tools
2. Look for errors in Console tab
3. Check Extension Host logs

---

## What's in the Extension

### File Structure
```
antigravity-extension/
├── package.json          # Extension manifest
├── extension.js          # Main extension code
├── README.md            # Extension documentation
└── .vscodeignore        # Files to exclude from package
```

### Features Implemented
- ✅ 8 Command Palette commands
- ✅ Context menu integration
- ✅ Output channel for agent results
- ✅ Terminal integration
- ✅ Memory file watcher
- ✅ Auto-notifications
- ✅ Configuration settings
- ✅ Activity bar view (sidebar)

---

## Next Steps

### Enhance the Extension (Optional)

**1. Add Icons:**
Create `media/` folder with custom icons for each agent

**2. Add Webview Panel:**
Display agent results in rich HTML panel instead of text output

**3. Add Agent Status Bar:**
Show currently running agent in status bar

**4. Add Inline Decorations:**
Highlight security issues directly in code

**5. Publish to Marketplace:**
```bash
npx vsce publish
```

---

## Resources

- **Antigravity:** https://antigravity.google/
- **Your Repo:** https://github.com/outlawexotix/OutlawExotix_AI_Suite
- **Full Integration Guide:** See `ANTIGRAVITY_INTEGRATION.md`
- **Extension Docs:** See `antigravity-extension/README.md`

---

**You're all set! Your War Room is now integrated with Google Antigravity.** 🚀

Choose Option 1 for quick use, or Option 2 for the full extension experience.
