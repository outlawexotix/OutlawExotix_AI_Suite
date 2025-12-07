import sys
import datetime
import os
import time

# fcntl is Unix-only, not available on Windows
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

def log_entry(entry):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = "PROJECT_MEMORY.md"

    # Cross-platform file locking
    max_retries = 5
    retry_delay = 0.1

    for attempt in range(max_retries):
        try:
            # Header if new file
            if not os.path.exists(log_file):
                with open(log_file, "w", encoding="utf-8") as f:
                    if HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                    f.write("# PROJECT MEMORY LOG\n\n")
                    if HAS_FCNTL:
                        fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            formatted_entry = f"\n## [{timestamp}]\n{entry}\n"

            with open(log_file, "a", encoding="utf-8") as f:
                if HAS_FCNTL:
                    fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                f.write(formatted_entry)
                f.flush()
                os.fsync(f.fileno())  # Force write to disk
                if HAS_FCNTL:
                    fcntl.flock(f.fileno(), fcntl.LOCK_UN)

            print(f"Memory updated in {log_file}")
            return

        except (IOError, OSError) as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"Error: Failed to write to {log_file} after {max_retries} attempts: {e}")
                raise

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python log_memory.py \"Your log entry here\"")
        sys.exit(1)
    
    entry = " ".join(sys.argv[1:])
    log_entry(entry)
