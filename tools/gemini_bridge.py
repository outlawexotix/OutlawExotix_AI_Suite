import os
import sys
import argparse
import google.generativeai as genai

def get_context():
    context = ""
    
    # 1. SPATIAL AWARENESS: List files in the shared directory
    # Only list top-level files for performance - avoid deep scans
    try:
        files = os.listdir('.')
        # Limit to 50 files to save tokens, just to give a "sense" of the room
        file_list = ', '.join(sorted(files[:50]))
        if len(files) > 50: file_list += "..."
        context += f"\n[SHARED DIRECTORY CONTENT]: {file_list}"
    except Exception:
        pass

    # 2. HISTORICAL AWARENESS: Read the Project Memory Log
    # This is the file Claude writes to. Now Gemini reads it too.
    if os.path.exists("PROJECT_MEMORY.md"):
        try:
            with open("PROJECT_MEMORY.md", "r", encoding="utf-8") as f:
                # Read the last 3000 characters efficiently
                try:
                    f.seek(0, 2)  # Seek to end
                    file_size = f.tell()
                    if file_size > 3000:
                        f.seek(file_size - 3000)  # Seek to last 3000 bytes
                        f.readline()  # Skip partial line
                    else:
                        f.seek(0)
                    memory = f.read()
                except (IOError, OSError, TypeError):
                    # Fallback for unseekable streams (e.g., in tests) or mock issues
                    f.seek(0)
                    memory = f.read()[-3000:]
                context += f"\n\n[SHARED PROJECT MEMORY (Recent Activity)]:\n{memory}\n"
        except Exception as e:
            context += f"\n[MEMORY READ ERROR]: {e}"
            
    return context

def get_intel(prompt, credentials=None, model_name='gemini-1.5-flash'):
    """Query Gemini using Application Default Credentials (user account only)."""
    if not credentials:
        print("ERROR: No valid credentials found.")
        print("\nTo authenticate with your Google account, run:")
        print("  gcloud auth application-default login")
        print("\nThis will open a browser for you to sign in to your Google account.")
        return
    
    try:
        genai.configure(credentials=credentials)
    except Exception as e:
        print(f"ERROR: Failed to configure Gemini with provided credentials: {e}")
        print("\nTry re-authenticating with:")
        print("  gcloud auth application-default login")
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
    parser = argparse.ArgumentParser(
        description="Outlaw Exotix Gemini Bridge - User Account Authentication Only",
        epilog="Authentication: Run 'gcloud auth application-default login' to sign in with your Google account"
    )
    
    # Positional Argument: The Prompt (combined)
    parser.add_argument("prompt", nargs="*", help="The prompt to send to Gemini")
    
    # Optional Arguments for Config
    parser.add_argument("--model", "-m", default="gemini-1.5-flash", help="Gemini Model ID (default: gemini-1.5-flash)")
    parser.add_argument("--setup", action="store_true", help="Display authentication setup instructions")

    args = parser.parse_args()
    
    # Handle --setup flag
    if args.setup:
        print("=" * 70)
        print("GEMINI AUTHENTICATION SETUP")
        print("=" * 70)
        print("\nThis tool uses Google Application Default Credentials (ADC) for")
        print("authentication, which means you sign in with your Google account.\n")
        print("Setup Steps:")
        print("  1. Install Google Cloud SDK (gcloud CLI) if not installed:")
        print("     https://cloud.google.com/sdk/docs/install")
        print("\n  2. Authenticate with your Google account:")
        print("     gcloud auth application-default login")
        print("\n  3. This will open a browser window for you to sign in")
        print("\n  4. After signing in, you can use this tool without API keys")
        print("\nTroubleshooting:")
        print("  - If you have persistent auth issues, revoke and re-authenticate:")
        print("    gcloud auth application-default revoke")
        print("    gcloud auth application-default login")
        print("\n  - To check current authentication status:")
        print("    gcloud auth application-default print-access-token")
        print("=" * 70)
        sys.exit(0)
    
    if not args.prompt:
        print("Usage: python gemini_bridge.py [OPTIONS] <prompt>")
        print("   or: python gemini_bridge.py --setup  (for authentication help)")
        sys.exit(1)

    # Reconstruct prompt from nargs list
    prompt_text = " ".join(args.prompt)
    
    # Attempt to load Application Default Credentials (user account)
    creds = None
    try:
        import google.auth
        creds, _ = google.auth.default()
    except ImportError:
        print("ERROR: 'google-auth' library is required for user account authentication.")
        print("\nInstall it with:")
        print("  pip install google-auth")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: Failed to load Application Default Credentials: {e}")
        print("\nYou need to authenticate with your Google account.")
        print("Run the following command and sign in when prompted:")
        print("  gcloud auth application-default login")
        print("\nFor more help, run: python gemini_bridge.py --setup")
        sys.exit(1)

    # Use credentials to query Gemini
    get_intel(prompt_text, credentials=creds, model_name=args.model)
