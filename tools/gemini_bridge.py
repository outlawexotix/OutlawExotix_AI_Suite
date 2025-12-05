import os
import sys
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

def get_intel(prompt):
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("ERROR: GOOGLE_API_KEY environment variable not set. Cannot contact Gemini Command.")
        return

    genai.configure(api_key=api_key)
    
    # Using Flash for high-speed context processing
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    # Inject the Shared Context into the prompt
    context_data = get_context()
    full_prompt = f"SYSTEM: You are sharing a workspace with an autonomous agent named Claude. Below is the shared context of the directory and recent logs.\n\nCONTEXT:{context_data}\n\nUSER QUERY: {prompt}"
    
    try:
        response = model.generate_content(full_prompt)
        print(response.text)
    except Exception as e:
        print(f"GEMINI UPLINK ERROR: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gemini_bridge.py <prompt>")
        sys.exit(1)
    
    prompt = " ".join(sys.argv[1:])
    get_intel(prompt)
