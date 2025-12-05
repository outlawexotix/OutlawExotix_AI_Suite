import subprocess
import sys
import os
import time
import shutil
from colorama import Fore, Back, Style, init

# Initialize colors
init()

# --- CONFIGURATION ---
# Use environment variables for flexibility, or fallback to your hardcoded paths
GEMINI_BRIDGE = os.getenv("GEMINI_BRIDGE_PATH", r"gemini_bridge.py") 
# Note: Ensure claude.exe is in your PATH or provide full absolute path below
CLAUDE_EXE = os.getenv("CLAUDE_EXE_PATH", r"C:\Users\penne\.local\bin\claude.exe")

# --- UTILITIES ---

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def check_dependencies():
    """Verifies that external tools exist before starting."""
    missing = []
    
    # Check Gemini Bridge
    if not os.path.exists(GEMINI_BRIDGE):
        # If it's just a filename, check if it's in the current dir
        if not os.path.exists(os.path.join(os.getcwd(), GEMINI_BRIDGE)):
            missing.append(f"Gemini Bridge not found at: {GEMINI_BRIDGE}")

    # Check Claude Executable
    # If it's a full path, check it. If it's just a command, check shutil.which
    if os.path.isabs(CLAUDE_EXE):
        if not os.path.exists(CLAUDE_EXE):
            missing.append(f"Claude Executable not found at: {CLAUDE_EXE}")
    else:
        if shutil.which(CLAUDE_EXE) is None:
             missing.append(f"Command '{CLAUDE_EXE}' not found in PATH.")

    if missing:
        print(f"{Fore.RED}[SYSTEM CRITICAL] MISSING DEPENDENCIES:{Style.RESET_ALL}")
        for m in missing:
            print(f"{Fore.RED} - {m}{Style.RESET_ALL}")
        print(f"\n{Fore.YELLOW}Please configure paths in outlaw_exotix.py or set environment variables.{Style.RESET_ALL}")
        sys.exit(1)

def type_effect(text, delay=0.01, color=Fore.WHITE):
    """Prints text character by character for a typing effect."""
    sys.stdout.write(color)
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print(Style.RESET_ALL)

def draw_header():
    clear_screen()
    print(f"{Fore.RED}{Style.BRIGHT}")
    print(r"██╗     ██╗ █████╗ ██████╗      ██████╗  ██████╗  ██████╗ ███╗   ███╗")
    print(r"██║     ██║██╔══██╗██╔══██╗     ██╔══██╗██╔═══██╗██╔═══██╗████╗ ████║")
    print(r"██║  █╗ ██║███████║██████╔╝     ██████╔╝██║   ██║██║   ██║██╔████╔██║")
    print(r"██║███╗██║██╔══██║██╔══██╗     ██╔══██╗██║   ██║██║   ██║██║╚██╔╝██║")
    print(r"╚███╔███╔╝██║  ██║██║  ██║     ██║  ██║╚██████╔╝╚██████╔╝██║ ╚═╝ ██║")
    print(r" ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚═════╝ ╚═╝     ╚═╝")
    print(f"{Fore.YELLOW} >> OUTLAW EXOTIX // SYSTEM OVERRIDE // AUTH: LORD PENNE << {Style.RESET_ALL}")
    print("\n")

def print_panel(title, text, color, width=60):
    """Generic panel printer for cleaner code."""
    border_color = color
    print(f"\n{border_color}╔═ [ {title} ] {'═' * (width - len(title) - 7)}╗{Style.RESET_ALL}")
    
    lines = text.strip().split('\n')
    for line in lines:
        # Simple word wrapping could go here, but for code/CLI output, direct printing is safer
        # to preserve formatting of lists/code blocks.
        clean_line = line.replace('\t', '    ')
        print(f"{border_color}║{Style.RESET_ALL} {clean_line}")

    print(f"{border_color}╚{'═' * (width - 2)}╝{Style.RESET_ALL}")

def loading_sequence():
    chars = "/-\|"
    print(f"{Fore.YELLOW}[SYSTEM] ESTABLISHING SECURE CONNECTION...", end="")
    for _ in range(10):
        for char in chars:
            sys.stdout.write(f"\b{char}")
            sys.stdout.flush()
            time.sleep(0.1)
    print(f"\b{Fore.GREEN}LOCKED.{Style.RESET_ALL}")
    time.sleep(0.5)

# --- MAIN LOOP ---

def main():    
    check_dependencies()
    draw_header()
    loading_sequence()

    type_effect("[INFO] GEMINI BRIDGE: ACTIVE", 0.02, Fore.CYAN)
    type_effect("[INFO] CLAUDE ENGINE: ACTIVE", 0.02, Fore.GREEN)
    type_effect("[INFO] MNEMOSYNE MEMORY: LINKED", 0.02, Fore.MAGENTA)
    print("\n")

    while True:
        try:
            print(f"{Fore.RED}┌──( {Fore.WHITE}COMMANDER {Fore.RED})-[ {Fore.WHITE}WAR ROOM {Fore.RED}]")
            user_input = input(f"└─{Fore.RED}► {Style.RESET_ALL}")

            if user_input.lower() in ['exit', 'quit', '/q']:
                print(f"\n{Fore.RED}[SYSTEM] TERMINATING LINK. GOOD HUNTING, MY LORD.{Style.RESET_ALL}")
                break

            if not user_input.strip():
                continue

            # PHASE 1: GEMINI ANALYSIS
            print(f"\n{Fore.CYAN}>>> UPLINKING TO ORBIT...{Style.RESET_ALL}")
            gemini_prompt = f"You are a Strategic Advisor. The user wants to: '{user_input}'. Provide specific tactical advice, warnings, or the best way to do this via CLI. Keep it brief and punchy."

            # Use sys.executable to ensure we use the same python interpreter
            gemini_process = subprocess.run(
                [sys.executable, GEMINI_BRIDGE, gemini_prompt],
                capture_output=True, text=True, encoding='utf-8'
            )
            
            gemini_advice = gemini_process.stdout.strip()
            
            if gemini_process.returncode != 0:
                print(f"{Fore.RED}[ERROR] GEMINI UPLINK FAILED:{Style.RESET_ALL}")
                print(gemini_process.stderr)
                gemini_advice = "ADVISORY UNAVAILABLE due to connection error."
            
            print_panel("GEMINI SATELLITE UPLINK", gemini_advice, Fore.CYAN)

            # PHASE 2: CLAUDE EXECUTION
            print(f"\n{Fore.GREEN}>>> DEPLOYING ASSETS...{Style.RESET_ALL}")

            combined_prompt = f"USER REQUEST: {user_input}\n\nSTRATEGIC ADVICE: {gemini_advice}\n\nINSTRUCTIONS: Execute the user request, adhering to the strategic advice."

            # Execute Claude. 
            # Note: The original code used PowerShell wrapping. We keep that if on Windows.
            if os.name == 'nt':
                claude_process = subprocess.run(
                    ["powershell", "-Command", f'& "{CLAUDE_EXE}" -p "{combined_prompt}" --dangerously-skip-permissions'],
                    capture_output=True, text=True, encoding='utf-8'
                )
            else:
                # Linux/Mac direct execution
                claude_process = subprocess.run(
                    [CLAUDE_EXE, "-p", combined_prompt, "--dangerously-skip-permissions"],
                    capture_output=True, text=True, encoding='utf-8'
                )

            output = claude_process.stdout if claude_process.stdout.strip() else claude_process.stderr
            print_panel("CLAUDE FIELD OPS", output, Fore.GREEN)

            print(f"{Fore.YELLOW}[MISSION CYCLE COMPLETE]{Style.RESET_ALL}\n")

        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[SYSTEM] EMERGENCY HALT.{Style.RESET_ALL}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}[CRITICAL FAILURE] {str(e)}{Style.RESET_ALL}")

if __name__ == "__main__":
    main()