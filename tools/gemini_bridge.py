import os
import sys
import argparse
import google.generativeai as genai
from typing import Optional, List, Any

# OAuth Imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    OAUTH_AVAILABLE = True
except ImportError:
    OAUTH_AVAILABLE = False

import memory_core

def get_context() -> str:
    """
    Gathers context from the environment to provide spatial and historical awareness to Gemini.
    """
    context = ""
    
    # 1. SPATIAL AWARENESS: List files in the shared directory
    try:
        files = os.listdir('.')
        # Limit to 50 files to save tokens, just to give a "sense" of the room
        file_list = ', '.join(files[:50])
        if len(files) > 50: file_list += "..."
        context += f"\n[SHARED DIRECTORY CONTENT]: {file_list}"
    except Exception as e:
        context += f"\n[DIRECTORY READ ERROR]: {str(e)}"

    # 2. HISTORICAL AWARENESS: Read the Project Memory Core
    memory = memory_core.fetch_context(char_limit=3000)
    if memory:
        context += f"\n\n[SHARED PROJECT MEMORY (Recent Activity)]:\n{memory}\n"
    
    return context

def authenticate_oauth() -> Any:
    """
    Attempts to authenticate using Native OAuth (InstalledAppFlow).
    1. Checks for saved 'token.json'.
    2. If missing/invalid, checks for 'client_secret.json'.
    3. If present, launches browser flow.
    """
    if not OAUTH_AVAILABLE:
        return None

    SCOPES = ['https://www.googleapis.com/auth/generative-language.retriever', 'https://www.googleapis.com/auth/cloud-platform']
    creds = None

    # 1. Load Saved Credentials
    if os.path.exists('token.json'):
        try:
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        except Exception:
            pass # Invalid token, will refresh or re-login

    # 2. Refresh or Login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception:
                creds = None # forced re-login
        
        if not creds:
            if os.path.exists('client_secret.json'):
                print("[AUTH] 'client_secret.json' found. Launching Browser Login...")
                try:
                    flow = InstalledAppFlow.from_client_secrets_file('client_secret.json', SCOPES)
                    creds = flow.run_local_server(port=0)
                    # Save the credentials for the next run
                    with open('token.json', 'w') as token:
                        token.write(creds.to_json())
                except Exception as e:
                    print(f"[AUTH ERROR] API Login failed: {e}")
                    return None
            else:
                # No client secret, cannot perform Oauth
                return None
                
    return creds

def load_env_file(filepath: str = ".env") -> Optional[str]:
    """Manually parses a .env file to find GOOGLE_API_KEY."""
    if not os.path.exists(filepath):
        return None
    
    try:
        with open(filepath, "r", encoding="utf-8") as f:
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

def get_api_key(args: argparse.Namespace) -> Optional[str]:
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
            with open(args.key_file, "r", encoding="utf-8") as f:
                return f.read().strip()
        except Exception:
            pass

    return None

def get_intel(prompt: str, api_key: Optional[str] = None, credentials: Any = None, model_name: str = 'gemini-1.5-flash') -> None:
    """
    Sends a query to Gemini with injected context and prints the response.
    """
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
    
    # Using Flash for high-speed context processing
    model = genai.GenerativeModel(model_name)
    
    # Inject the Shared Context into the prompt
    context_data = get_context()
    full_prompt = f"SYSTEM: You are sharing a workspace with an autonomous agent named Claude. Below is the shared context of the directory and recent logs.\n\nCONTEXT:{context_data}\n\nUSER QUERY: {prompt}"
    
    try:
        response = model.generate_content(full_prompt)
        # Check if response was blocked
        if response.prompt_feedback and response.prompt_feedback.block_reason:
             print(f"GEMINI BLOCKED RESPONSE: {response.prompt_feedback.block_reason}")
             return
             
        if response.text:
            print(response.text)
        else:
             print("[GEMINI SILENCE] (No text content returned)")

    except Exception as e:
        print(f"GEMINI UPLINK ERROR: {str(e)}")

def main() -> None:
    parser = argparse.ArgumentParser(description="Outlaw Exotix Gemini Bridge")
    
    # Positional Argument: The Prompt (combined)
    parser.add_argument("prompt", nargs="*", help="The prompt to send to Gemini")
    
    # Optional Arguments for Auth & Config
    parser.add_argument("--api-key", "-k", help="Directly provide the Google API Key (overrides ADC)")
    parser.add_argument("--key-file", "-f", help="Path to a file containing the Google API Key")
    parser.add_argument("--model", "-m", default="gemini-1.5-flash", help="Gemini Model ID (default: gemini-1.5-flash)")

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
    else: # Otherwise, attempt User Account (OAuth > ADC)
        
        # 1. Try Native OAuth (Personal Account)
        creds = authenticate_oauth()
        
        # 2. If no OAuth, try ADC (Enterprise/Cloud)
        adc_error = None
        if not creds:
             try:
                import google.auth
                creds, _ = google.auth.default()
                if not creds:
                    adc_error = "No credentials found via google.auth.default()."
             except ImportError:
                adc_error = "Library 'google-auth' is not installed."
             except Exception as e:
                adc_error = f"ADC Load Error: {str(e)}"
        
        if not creds: # If User Auth wasn't successful, try other API key methods
            resolved_key = get_api_key(args)
            
            # Use strict checking: if neither User Auth nor API Key worked, THEN complain.
            if not resolved_key:
                print("ERROR: Authentication failed. No valid credentials found.")
                print(f"1. Native Login: 'client_secret.json' not found or login failed.")
                print(f"2. ADC Login: {adc_error or 'Not configured.'}")
                print(f"3. API Key: Not provided via flag, environment variable, or .env.")
                print("\nTo Sign In (Personal Account):")
                print("   -> Download OAuth Client JSON from Google Cloud Console.")
                print("   -> Save it as 'client_secret.json' in this folder.")
                print("   -> Run this script again.")
                sys.exit(1)

    get_intel(prompt_text, api_key=resolved_key, credentials=creds, model_name=args.model)

if __name__ == "__main__":
    main()
