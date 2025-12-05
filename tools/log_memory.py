import sys
import datetime
import os

def log_entry(entry):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "PROJECT_MEMORY.md"
    
    # Header if new file
    if not os.path.exists(log_file):
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("# PROJECT MEMORY LOG\n\n")

    formatted_entry = f"\n## [{timestamp}]\n{entry}\n"
    
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(formatted_entry)
    
    print(f"Memory updated in {log_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python log_memory.py \"Your log entry here\"")
        sys.exit(1)
    
    entry = " ".join(sys.argv[1:])
    log_entry(entry)
