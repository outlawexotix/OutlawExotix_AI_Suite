import os
import datetime
import time

MEMORY_FILE = "PROJECT_MEMORY.md"

def append_log(source: str, content: str, category: str = "INTEL"):
    """
    Appends a structured log entry to the project memory.
    Format: [TIMESTAMP] [SOURCE] [CATEGORY] Content
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"\n## [{timestamp}] [{source.upper()}] [{category.upper()}]\n{content}\n"
    
    _write_entry(entry)

def fetch_context(char_limit: int = 4000) -> str:
    """
    Reads the tail of the memory file to provide context.
    """
    if not os.path.exists(MEMORY_FILE):
        return ""
        
    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            # Read all, then slice the end. 
            # For massive files, we'd want seek(), but let's keep it simple for now.
            content = f.read()
            return content[-char_limit:]
    except Exception as e:
        return f"[MEMORY READ ERROR] {e}"

def _write_entry(text: str):
    """
    Internal write with simple retry locking.
    """
    max_retries = 5
    retry_delay = 0.1
    
    # Ensure header exists
    if not os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                f.write("# PROJECT MEMORY LOG\n\n")
        except: pass

    for attempt in range(max_retries):
        try:
            with open(MEMORY_FILE, "a", encoding="utf-8") as f:
                f.write(text)
                f.flush()
                # Windows doesn't strictly need fsync for atomic appends usually, 
                # but good for safety.
                os.fsync(f.fileno()) 
            return
        except (IOError, OSError):
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2
            else:
                print(f"[MEMORY CORE] Failed to write to {MEMORY_FILE}")

if __name__ == "__main__":
    # Test CLI
    append_log("TEST", "Memory Core Initialization Verified.")
    print(fetch_context(500))
