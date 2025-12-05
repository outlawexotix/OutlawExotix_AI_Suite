
---
# MNEMOSYNE PROTOCOL (ACTIVE MEMORY SYSTEM)
You are running in **Continuous Context Mode**.
You share a persistent memory file with other agents located at `./PROJECT_MEMORY.md`.

## YOUR MANDATE
1.  **LOG EVERYTHING:** After every significant action (installing a package, creating a file, fixing a bug), you MUST append a log entry.
    -   **Command:** `python C:\Users\penne\.claude\tools\log_memory.py "Your summary here"`
    -   *Example:* "Refactored auth.ts. Fixed logic error in login function. Added unit test."

2.  **CONSULT MEMORY:** If you are starting a new session or feel lost, READ `./PROJECT_MEMORY.md` using `fs.read` to understand the project history.

3.  **CONTEXT UPDATES:** By writing to this file, you ensure that future agents (or you in the future) know exactly what has been done, preventing loops and redundant work.
---
