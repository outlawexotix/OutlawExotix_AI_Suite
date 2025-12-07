import argparse
import sys
import os
import time

try:
    from interpreter import interpreter
    INTERPRETER_AVAILABLE = True
except ImportError:
    INTERPRETER_AVAILABLE = False

def get_context() -> str:
    """
    Gathers context from the environment (Spatial & Historical).
    Reuses logic similar to Gemini/Codex bridges for consistency.
    """
    context = ""
    
    # 1. SPATIAL AWARENESS
    try:
        files = os.listdir('.')
        file_list = ', '.join(files[:50])
        if len(files) > 50: file_list += "..."
        context += f"\n[SHARED DIRECTORY CONTENT]: {file_list}"
    except Exception:
        pass

    # 2. HISTORICAL AWARENESS
    memory_path = "PROJECT_MEMORY.md"
    if os.path.exists(memory_path):
        max_retries = 5
        retry_delay = 0.1
        for attempt in range(max_retries):
            try:
                with open(memory_path, "r", encoding="utf-8") as f:
                    memory = f.read()[-3000:] 
                    context += f"\n\n[SHARED PROJECT MEMORY]:\n{memory}\n"
                break
            except (IOError, OSError):
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    retry_delay *= 2
    return context

def main():
    parser = argparse.ArgumentParser(description="Outlaw Exotix Open Interpreter Bridge")
    parser.add_argument("prompt", nargs="*", help="Instructions for the interpreter")
    parser.add_argument("--auto-run", "-y", action="store_true", help="Bypass confirmation (Dangerous)")
    parser.add_argument("--model", "-m", default="gpt-4o", help="Model to use (default: gpt-4o)")
    
    args = parser.parse_args()

    if not INTERPRETER_AVAILABLE:
        print("ERROR: 'open-interpreter' package not installed.")
        print("Run: pip install open-interpreter")
        sys.exit(1)

    if not args.prompt:
        # If no prompt, start interactive mode
        print(">>> OPEN INTERPRETER INTERACTIVE MODE <<<")
    
    prompt_text = " ".join(args.prompt) if args.prompt else ""
    
    # Configure Interpreter
    interpreter.auto_run = args.auto_run
    interpreter.model = args.model
    interpreter.system_message += """
    You are an agent of Outlaw Exotix. 
    Your mission is to EXECUTE code locally to solve the user's request.
    Be efficient. Be accurate.
    """
    
    # Inject Context
    context_data = get_context()
    interpreter.system_message += f"\nDEBUG CONTEXT:{context_data}"

    try:
        if prompt_text:
            interpreter.chat(prompt_text)
        else:
            interpreter.chat() # Interactive loop
    except Exception as e:
        print(f"[INTERPRETER ERROR] {e}")

if __name__ == "__main__":
    main()
