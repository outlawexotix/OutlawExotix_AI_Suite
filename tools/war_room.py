import subprocess
import sys
import os
import time
import shutil
import tempfile
from typing import Optional, List, Dict, Any, Tuple
from colorama import Fore, Back, Style, init

# Initialize Colorama
init()

# Constants
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
GEMINI_BRIDGE = os.path.join(CURRENT_DIR, "gemini_bridge.py")
CODEX_BRIDGE = os.path.join(CURRENT_DIR, "codex_bridge.py")
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")

def get_claude_exe() -> str:
    """Detects and returns the path to the Claude executable."""
    if os.name == "nt":
        return r"C:\Users\penne\.local\bin\claude.exe"
    else:
        return shutil.which("claude") or "claude"

CLAUDE_EXE = get_claude_exe()

class WarRoomConsole:
    def __init__(self):
        self.active_persona_name: str = "Default"
        self.current_system_prompt: Optional[str] = None
        self.running: bool = True

    def clear_screen(self) -> None:
        """Clears the terminal screen."""
        os.system("cls" if os.name == "nt" else "clear")

    def draw_header(self) -> None:
        """Renders the artistic header."""
        self.clear_screen()
        print(f"{Fore.RED}{Style.BRIGHT}")
        print("=============================================================")
        print("   OUTLAW EXOTIX // WAR ROOM CONSOLE // MK.II CROSS-PLATFORM")
        print("=============================================================")
        print(f"{Style.RESET_ALL}")
        print(f"{Fore.GREEN}[SYSTEM] ALL SYSTEMS ONLINE.{Style.RESET_ALL}\n")

    def load_persona(self, mode_name: str) -> None:
        """Loads a persona template."""
        target_mode = mode_name.lower().strip()
        
        if target_mode == "reset":
            self.current_system_prompt = None
            self.active_persona_name = "Default"
            print(f"{Fore.YELLOW}[SYSTEM] Persona reset to Default.{Style.RESET_ALL}")
            return

        template_path = os.path.join(TEMPLATES_DIR, f"{target_mode}.md")
        if os.path.exists(template_path):
            try:
                with open(template_path, "r", encoding="utf-8") as f:
                    self.current_system_prompt = f.read()
                self.active_persona_name = target_mode.upper()
                print(f"{Fore.YELLOW}[SYSTEM] Persona Active: {self.active_persona_name}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[ERROR] Failed to load template: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}[ERROR] Template not found: {template_path}{Style.RESET_ALL}")
            available = [f.replace('.md','') for f in os.listdir(TEMPLATES_DIR) if f.endswith('.md')]
            print(f"Available: {available}")

    def call_advisor(self, script_path: str, prompt: str, advisor_name: str, color: str) -> str:
        """Calls an external advisor script (Gemini/Codex)."""
        print(f"\n{color}>>> UPLINKING TO {advisor_name}...{Style.RESET_ALL}")
        try:
            # Construct input
            # If Codex, just pass the prompt. If Gemini, prefix with "Advice for:"
            advisor_input = prompt if script_path == CODEX_BRIDGE else f"Advice for: {prompt}"
            
            process = subprocess.run(
                [sys.executable, script_path, advisor_input],
                capture_output=True, text=True, check=False
            )
            
            output = process.stdout.strip()
            print(f"{color}{output}{Style.RESET_ALL}")
            
            if process.stderr:
                 # Log stderr if needed, but don't clutter UI unless critical
                 pass
            
            return output
        except Exception as e:
            print(f"{Fore.RED}[ADVISOR ERROR] {e}{Style.RESET_ALL}")
            return ""

    def execute_claude(self, prompt: str, advice: str, advisor_type: str) -> None:
        """Executes Claude with the combined prompt."""
        print(f"{Fore.GREEN}>>> CLAUDE EXECUTING...{Style.RESET_ALL}")
        
        # 1. Construct Combined Prompt
        if not advice:
             combined_prompt = prompt
        else:
             combined_prompt = f"REQUEST: {prompt}\n\n[{advisor_type} STRATEGY]:\n{advice}"

        # 2. Use temp files for safe execution (prevents shell injection)
        prompt_file = None
        system_file = None

        try:
            with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as pf:
                pf.write(combined_prompt)
                prompt_file = pf.name

            cmd = [CLAUDE_EXE, "-p", f"@{prompt_file}", "--dangerously-skip-permissions"]

            if self.current_system_prompt:
                with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as sf:
                    sf.write(self.current_system_prompt)
                    system_file = sf.name
                cmd.extend(["--system-prompt", f"@{system_file}"])

            # 3. Execute
            process = subprocess.run(cmd, capture_output=True, text=True, check=False)
            print(f"{Fore.GREEN}{process.stdout}{Style.RESET_ALL}")
            if process.stderr:
                print(f"{Fore.RED}{process.stderr}{Style.RESET_ALL}")

        except Exception as e:
            print(f"{Fore.RED}[CLAUDE ERROR] {e}{Style.RESET_ALL}")
        finally:
            # Cleanup
            for fpath in [prompt_file, system_file]:
                if fpath and os.path.exists(fpath):
                    try:
                        os.unlink(fpath)
                    except OSError:
                        pass

    def parse_command(self, user_input: str) -> None:
        """Parses and executes a single user command."""
        cmd_lower = user_input.lower()

        # 1. Mode Switching
        if cmd_lower.startswith("/mode "):
            self.load_persona(user_input[6:])
            return

        # 2. Execution Logic
        skip_advisor = False
        skip_execution = False
        advisor_script = GEMINI_BRIDGE
        advisor_color = Fore.CYAN
        advisor_name = "GEMINI"
        
        real_prompt = user_input

        if cmd_lower.startswith("/execute "):
            skip_advisor = True
            real_prompt = user_input[9:].strip()
        elif cmd_lower.startswith("/consult "):
            skip_execution = True
            real_prompt = user_input[9:].strip()
            if real_prompt.lower().startswith("codex "):
                advisor_script = CODEX_BRIDGE
                advisor_color = Fore.BLUE
                advisor_name = "CODEX"
                real_prompt = real_prompt[6:].strip()
        elif cmd_lower.startswith("/codex "):
            advisor_script = CODEX_BRIDGE
            advisor_color = Fore.BLUE
            advisor_name = "CODEX"
            real_prompt = user_input[7:].strip()
        elif cmd_lower.startswith("/interpreter "):
            # Open Interpreter Integration
            print(f"{Fore.MAGENTA}>>> LAUNCHING OPEN INTERPRETER...{Style.RESET_ALL}")
            interpreter_script = os.path.join(CURRENT_DIR, "interpreter_bridge.py")
            subprocess.run([sys.executable, interpreter_script, user_input[13:].strip()])
            return # Return to loop after interactive session
        elif cmd_lower.startswith("/opencode"):
            # OpenCode CLI Integration (Go)
            print(f"{Fore.CYAN}>>> LAUNCHING OPENCODE CLI...{Style.RESET_ALL}")
            if shutil.which("opencode"):
                subprocess.run(["opencode"] + user_input.split()[1:])
            else:
                print(f"{Fore.RED}[ERROR] 'opencode' binary not found in PATH.{Style.RESET_ALL}")
                print("To enable this feature, you must install Go and OpenCode:")
                print("1. Install Go: winget install GoLang.Go")
                print("2. Install OpenCode: go install github.com/opencode/opencode@latest")
            return
        elif cmd_lower.startswith("/youtube ") or cmd_lower.startswith("/vision "):
            # Operation Vision: Universal Summarizer (God Mode)
            print(f"{Fore.RED}>>> ACTIVATING UNIVERSAL VISION PROTOCOLS...{Style.RESET_ALL}")
            vision_script = os.path.join(CURRENT_DIR, "vision_bridge.py")
            parts = user_input.split(maxsplit=1)
            if len(parts) > 1:
                subprocess.run([sys.executable, vision_script, parts[1].strip()])
            else:
                 print(f"{Fore.RED}[ERROR] URL required. Usage: /vision <url>{Style.RESET_ALL}")
            return
        elif cmd_lower.startswith("/harvest ") or cmd_lower.startswith("/scrape "):
            # Operation Harvester: Web Intelligence
            print(f"{Fore.MAGENTA}>>> DEPLOYING HARVESTER AGENT...{Style.RESET_ALL}")
            harvester_script = os.path.join(CURRENT_DIR, "harvester_bridge.py")
            parts = user_input.split(maxsplit=2) # /harvest <url> [query]
            if len(parts) >= 2:
                target_url = parts[1].strip()
                query = parts[2].strip() if len(parts) > 2 else "Download all relevant files"
                subprocess.run([sys.executable, harvester_script, target_url, query])
            else:
                 print(f"{Fore.RED}[ERROR] Usage: /harvest <url> [search_query]{Style.RESET_ALL}")
            return

        # 3. Advisor Phase
        advice_content = ""
        if not skip_advisor:
            advice_content = self.call_advisor(advisor_script, real_prompt, advisor_name, advisor_color)

        # 4. Executor Phase
        if not skip_execution:
            self.execute_claude(real_prompt, advice_content, advisor_name)

    def run(self) -> None:
        """Main event loop."""
        self.draw_header()
        
        while self.running:
            try:
                # Dynamic prompt color
                prompt_color = Fore.RED if self.active_persona_name == "Default" else Fore.MAGENTA
                try:
                    user_input = input(f"{prompt_color}COMMANDER [{self.active_persona_name}] > {Style.RESET_ALL}")
                except EOFError:
                    break # Handle Ctrl+D gracefully

                if user_input.lower() in ["exit", "quit", "/q"]:
                    self.running = False
                    break
                
                if not user_input.strip():
                    continue

                self.parse_command(user_input)

            except KeyboardInterrupt:
                print("\n[SYSTEM] Interrupted. Exiting...")
                self.running = False

def main() -> None:
    console = WarRoomConsole()
    console.run()

if __name__ == "__main__":
    main()
