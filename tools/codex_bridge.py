import os
import sys
import argparse
import logging

# Try importing openai, handle missing dependency gracefully
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

def get_context():
    context = ""
    
    # 1. SPATIAL AWARENESS: List files in the shared directory
    try:
        files = os.listdir('.')
        # Limit to 50 files to save tokens
        file_list = ', '.join(files[:50])
        if len(files) > 50: file_list += "..."
        context += f"\n[SHARED DIRECTORY CONTENT]: {file_list}"
    except Exception:
        pass

    # 2. HISTORICAL AWARENESS: Read the Project Memory Log
    if os.path.exists("PROJECT_MEMORY.md"):
        try:
            with open("PROJECT_MEMORY.md", "r", encoding="utf-8") as f:
                memory = f.read()[-3000:] 
                context += f"\n\n[SHARED PROJECT MEMORY (Recent Activity)]:\n{memory}\n"
        except Exception as e:
            context += f"\n[MEMORY READ ERROR]: {e}"
            
    return context

def load_env_key():
    """Check Env Var, Local .env, and Global Key File for OPENAI_API_KEY."""
    # 1. Environment Variable
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key
    
    # 2. Local .env File
    if os.path.exists(".env"):
        try:
            with open(".env", "r") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("#") or "=" not in line:
                        continue
                    key, value = line.split("=", 1)
                    if key.strip() == "OPENAI_API_KEY":
                        return value.strip().strip('"').strip("'")
        except Exception:
            pass

    # 3. Global Credential File (The "User Login" Equivalent)
    # Windows: C:\Users\penne\.openai\api_key
    # Linux: /home/penne/.openai/api_key
    global_key_path = os.path.join(os.path.expanduser("~"), ".openai", "api_key")
    if os.path.exists(global_key_path):
        try:
            with open(global_key_path, "r") as f:
                return f.read().strip()
        except Exception:
            pass

    return None

def query_codex(prompt, api_key, model="gpt-4o"):
    if not OPENAI_AVAILABLE:
        print("ERROR: 'openai' python package is missing. Install with: pip install openai")
        return

    if not api_key:
        print("ERROR: OPENAI_API_KEY not found via Flag, Env, or .env.")
        return

    client = OpenAI(api_key=api_key)
    
    context_data = get_context()
    
    system_prompt = (
        "You are CODEX, an elite programming intelligence within the Outlaw Exotix suite. "
        "Your code is aggressive, efficient, and modern. "
        "You do not explain trivialities. You output high-performance solutions. "
        "You have access to the current directory context below."
    )
    
    user_message = f"CONTEXT:{context_data}\n\nTASK: {prompt}"

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.2 # Low temp for precise coding
        )
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"CODEX UPLINK ERROR: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outlaw Exotix Codex Bridge (OpenAI)")
    
    parser.add_argument("prompt", nargs="*", help="The coding task for Codex")
    parser.add_argument("--api-key", "-k", help="Directly provide the OpenAI API Key")
    parser.add_argument("--model", "-m", default="gpt-4o", help="OpenAI Model ID (default: gpt-4o)")

    args = parser.parse_args()
    
    if not args.prompt:
        print("Usage: python codex_bridge.py [OPTIONS] <prompt>")
        sys.exit(1)

    prompt_text = " ".join(args.prompt)
    
    # Resolve Key
    resolved_key = args.api_key if args.api_key else load_env_key()
    
    query_codex(prompt_text, resolved_key, args.model)
