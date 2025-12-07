import os
import sys
import argparse
import google.generativeai as genai

def get_context():
    context = ""
    
    # 1. SPATIAL AWARENESS: List files in the shared directory
    try:
        files = os.listdir('.')
        # Limit to 50 files to save tokens, just to give a "sense" of the room
        file_list = ', '.join(files[:50])
        if len(files) > 50: file_list += "..."
        context += f"\n[SHARED DIRECTORY CONTENT]: {file_list}"
    except Exception:
        pass

    # 2. HISTORICAL AWARENESS: Read the Project Memory Log
    # This is the file Claude writes to. Now Gemini reads it too.
    if os.path.exists("PROJECT_MEMORY.md"):
        try:
            with open("PROJECT_MEMORY.md", "r", encoding="utf-8") as f:
                # Read the last 3000 characters to keep context fresh but concise
                memory = f.read()[-3000:] 
                context += f"\n\n[SHARED PROJECT MEMORY (Recent Activity)]:\n{memory}\n"
        except Exception as e:
            context += f"\n[MEMORY READ ERROR]: {e}"
            
    return context

def load_env_file(filepath=".env"):
    """Manually parses a .env file to find GOOGLE_API_KEY."""
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#") or "=" not in line:
                    continue
                key, value = line.split("=", 1)
                if key.strip() == "GOOGLE_API_KEY":
                    return value.strip().strip('"').strip("'")
    except Exception:
        pass
    return None

def get_api_key(args):
    """Resolves API Key from multiple sources in priority order."""
    # 1. CLI Argument
    if args.api_key:
        return args.api_key
    
    # 2. Environment Variable
    env_key = os.getenv("GOOGLE_API_KEY")
    if env_key:
        return env_key
    
    # 3. Local .env File
    dotenv_key = load_env_file()
    if dotenv_key:
        return dotenv_key

    # 4. Specific Key File
    if args.key_file and os.path.exists(args.key_file):
        try:
            with open(args.key_file, "r") as f:
                return f.read().strip()
        except Exception:
            pass

    return None

def get_intel(prompt, api_key=None, credentials=None, model_name='gemini-1.5-flash'):
    if credentials:
        try:
            genai.configure(credentials=credentials)
        except Exception as e:
            print(f"ERROR: Failed to configure Gemini with provided credentials: {e}")
            return
    elif api_key:
        genai.configure(api_key=api_key)
    else:
        print("ERROR: No authentication method provided (API Key or ADC).")
        return
    
    # Using Gemini 3 Pro for advanced capabilities (upgrade from gemini-1.5-flash)
    # Falls back to specified model if Gemini 3 not available
    model = genai.GenerativeModel(model_name)
    
    # Inject the Shared Context into the prompt
    context_data = get_context()
    full_prompt = f"SYSTEM: You are sharing a workspace with an autonomous agent named Claude. Below is the shared context of the directory and recent logs.\n\nCONTEXT:{context_data}\n\nUSER QUERY: {prompt}"
    
    try:
        response = model.generate_content(full_prompt)
        print(response.text)
    except Exception as e:
        print(f"GEMINI UPLINK ERROR: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Outlaw Exotix Gemini Bridge")
    
    # Positional Argument: The Prompt (combined)
    parser.add_argument("prompt", nargs="*", help="The prompt to send to Gemini")
    
    # Optional Arguments for Auth & Config
    parser.add_argument("--api-key", "-k", help="Directly provide the Google API Key (overrides ADC)")
    parser.add_argument("--key-file", "-f", help="Path to a file containing the Google API Key")
    parser.add_argument("--model", "-m", default="gemini-3-pro", help="Gemini Model ID (default: gemini-3-pro, fallback: gemini-1.5-flash)")

    args = parser.parse_args()
    
    if not args.prompt:
        print("Usage: python gemini_bridge.py [OPTIONS] <prompt>")
        sys.exit(1)

    # Reconstruct prompt from nargs list
    prompt_text = " ".join(args.prompt)
    
    creds = None
    resolved_key = None

    if args.api_key: # Highest priority: Explicit API Key via flag
        resolved_key = args.api_key
    else: # Otherwise, attempt ADC as the preferred 'user account' method
        try:
            import google.auth
            creds, _ = google.auth.default()
            # If ADC successfully loaded, use it.
            # Otherwise, creds will be None, and we'll fall back to API Key methods.
        except ImportError:
            # google-auth not installed, ADC not possible. Log warning, proceed to API Key.
            print("WARNING: 'google-auth' library is required for ADC. Falling back to API Key methods.")
            # Note: Do not sys.exit here, allow fallback
        except Exception as e:
            # ADC failed for other reasons. Log warning, proceed to API Key.
            print(f"WARNING: Failed to load Application Default Credentials: {e}. Falling back to API Key methods.")
            print("Tip: Run 'gcloud auth application-default login' to set up user credentials.")
            # Note: Do not sys.exit here, allow fallback
        
        if not creds: # If ADC wasn't successful or available, try other API key methods
            resolved_key = get_api_key(args)
            if not resolved_key:
                print("ERROR: No authentication method found. Please provide an API key or set up ADC.")
                print("Tip: Run 'gcloud auth application-default login' to set up user credentials.")
                sys.exit(1)

    get_intel(prompt_text, api_key=resolved_key, credentials=creds, model_name=args.model)
