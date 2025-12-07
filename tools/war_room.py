import subprocess
import sys
import os
import time
import shutil
from colorama import Fore, Back, Style, init

init()

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
GEMINI_BRIDGE = os.path.join(current_dir, "gemini_bridge.py")
CODEX_BRIDGE = os.path.join(current_dir, "codex_bridge.py")
TEMPLATES_DIR = os.path.join(project_root, "templates")

if os.name == "nt":
    CLAUDE_EXE = r"C:\Users\penne\.local\bin\claude.exe"
else:
    CLAUDE_EXE = shutil.which("claude") or "claude"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def draw_header():
    clear_screen()
    print(f"{Fore.RED}{Style.BRIGHT}")
    print("=============================================================")
    print("   OUTLAW EXOTIX // WAR ROOM CONSOLE // MK.II CROSS-PLATFORM")
    print("=============================================================")
    print(f"{Style.RESET_ALL}")

def main():
    draw_header()
    print(f"{Fore.GREEN}[SYSTEM] ALL SYSTEMS ONLINE.{Style.RESET_ALL}\n")
    
    current_system_prompt = None
    active_persona_name = "Default"
    
    # Cache available templates on startup for performance
    available_templates = []
    try:
        available_templates = [f.replace('.md','') for f in os.listdir(TEMPLATES_DIR) if f.endswith('.md')]
    except Exception:
        pass

    while True:
        try:
            prompt_color = Fore.RED if active_persona_name == "Default" else Fore.MAGENTA
            user_input = input(f"{prompt_color}COMMANDER [{active_persona_name}] > {Style.RESET_ALL}")
            
            if user_input.lower() in ["exit", "quit", "/q"]: break
            if not user_input.strip(): continue

            # --- COMMAND PARSING ---
            cmd_lower = user_input.lower()
            
            # 1. MODE SWITCHING (/mode)
            if cmd_lower.startswith("/mode "):
                target_mode = user_input[6:].strip()
                
                if target_mode.lower() == "reset":
                    current_system_prompt = None
                    active_persona_name = "Default"
                    print(f"{Fore.YELLOW}[SYSTEM] Persona reset to Default.{Style.RESET_ALL}")
                    continue

                template_path = os.path.join(TEMPLATES_DIR, f"{target_mode}.md")
                if os.path.exists(template_path):
                    try:
                        with open(template_path, "r", encoding="utf-8") as f:
                            current_system_prompt = f.read()
                        active_persona_name = target_mode.upper()
                        print(f"{Fore.YELLOW}[SYSTEM] Persona Active: {active_persona_name}{Style.RESET_ALL}")
                    except Exception as e:
                        print(f"{Fore.RED}[ERROR] Failed to load template: {e}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}[ERROR] Template not found: {template_path}{Style.RESET_ALL}")
                    print(f"Available: {available_templates}")
                continue

            # 2. EXECUTION FLAGS
            skip_advisor = False
            skip_execution = False
            advisor_script = GEMINI_BRIDGE
            advisor_color = Fore.CYAN
            advisor_type = "GEMINI STRATEGY"
            
            real_prompt = user_input # Default prompt
            
            if cmd_lower.startswith("/execute "):
                # Direct Link: Skip Advisor
                skip_advisor = True
                real_prompt = user_input[9:].strip()
                
            elif cmd_lower.startswith("/consult "):
                # Silent Mode: Skip Execution
                skip_execution = True
                real_prompt = user_input[9:].strip()
                # Optional: Consult Codex specific
                if real_prompt.lower().startswith("codex "):
                    advisor_script = CODEX_BRIDGE
                    advisor_color = Fore.BLUE
                    advisor_type = "CODEX BLUEPRINT"
                    real_prompt = real_prompt[6:].strip()

            elif cmd_lower.startswith("/codex "):
                # Codex Mode: Use Codex Advisor
                advisor_script = CODEX_BRIDGE
                advisor_color = Fore.BLUE
                advisor_type = "CODEX BLUEPRINT"
                real_prompt = user_input[7:].strip()

            # --- STEP 1: ADVISOR PHASE ---
            advice_content = ""
            if not skip_advisor:
                print(f"\n{advisor_color}>>> UPLINKING TO {advisor_type.split()[0]}...{Style.RESET_ALL}")
                try:
                    # Construct prompt for advisor
                    advisor_input = f"Advice for: {real_prompt}"
                    # If Codex, just pass the prompt directly as a task
                    if advisor_script == CODEX_BRIDGE:
                        advisor_input = real_prompt
                        
                    advisor_process = subprocess.run(
                        [sys.executable, advisor_script, advisor_input], 
                        capture_output=True, text=True
                    )
                    advice_content = advisor_process.stdout.strip()
                    
                    # Print Advisor Output
                    print(f"{advisor_color}{advice_content}{Style.RESET_ALL}")
                    
                    if advisor_process.stderr:
                         # Optional: Print stderr if verbose, or just if it looks like a real error
                         pass 

                except Exception as e:
                    print(f"{Fore.RED}[ADVISOR ERROR] {e}{Style.RESET_ALL}")
            
            # --- STEP 2: CLAUDE PHASE ---
            if not skip_execution:
                print(f"{Fore.GREEN}>>> CLAUDE EXECUTING...{Style.RESET_ALL}")
                
                # Construct Combined Prompt
                if skip_advisor:
                    combined_prompt = real_prompt
                else:
                    combined_prompt = f"REQUEST: {real_prompt}\n\n[{advisor_type}]:\n{advice_content}"
                
                # Build Command - Use temp files to avoid shell injection
                import tempfile

                cmd = []
                prompt_file = None
                system_file = None

                try:
                    # Write prompt to temp file for security
                    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as pf:
                        pf.write(combined_prompt)
                        prompt_file = pf.name

                    # Write system prompt to temp file if exists
                    if current_system_prompt:
                        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as sf:
                            sf.write(current_system_prompt)
                            system_file = sf.name

                    # Build command with file arguments (no shell injection risk)
                    cmd = [CLAUDE_EXE, "-p", f"@{prompt_file}", "--dangerously-skip-permissions"]
                    if system_file:
                        cmd.extend(["--system-prompt", f"@{system_file}"])

                except Exception as e:
                    print(f"{Fore.RED}[ERROR] Failed to create temp files: {e}{Style.RESET_ALL}")
                    continue

                try:
                    claude_process = subprocess.run(cmd, capture_output=True, text=True)
                    print(f"{Fore.GREEN}{claude_process.stdout}{Style.RESET_ALL}")
                    if claude_process.stderr: print(f"{Fore.RED}{claude_process.stderr}{Style.RESET_ALL}")
                except Exception as e:
                     print(f"{Fore.RED}[CLAUDE ERROR] {e}{Style.RESET_ALL}")
                finally:
                    # Cleanup temp files
                    if prompt_file and os.path.exists(prompt_file):
                        try:
                            os.unlink(prompt_file)
                        except:
                            pass
                    if system_file and os.path.exists(system_file):
                        try:
                            os.unlink(system_file)
                        except:
                            pass

        except KeyboardInterrupt:
            break
