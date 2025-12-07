#!/bin/bash
AGENT_NAME=$1
shift
REMAINING_ARGS="$@"

# Input validation: prevent path traversal
if [[ "$AGENT_NAME" =~ [/.\\] ]]; then
    echo "Error: Agent name contains invalid characters (path traversal attempt)"
    exit 1
fi

# Validate agent name is not empty
if [ -z "$AGENT_NAME" ]; then
    echo "Usage: agent.sh <agent-name> [args...]"
    exit 1
fi

# Resolve paths
TEMPLATE_PATH="$HOME/.claude/templates/${AGENT_NAME}.md"
MEMORY_PATH="$HOME/.claude/memory_protocol.md"

# Check if agent exists
if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "Error: Agent template '$AGENT_NAME' not found at $TEMPLATE_PATH"
    exit 1
fi

# Check if memory protocol exists
if [ ! -f "$MEMORY_PATH" ]; then
    echo "Warning: Memory protocol not found at $MEMORY_PATH"
fi

# Combine Agent Persona + Memory Protocol
SYSTEM_PROMPT=$(cat "$TEMPLATE_PATH" "$MEMORY_PATH")

echo -e "\e[36mDeploying Agent: $AGENT_NAME (with Mnemosyne Memory)\e[0m"

# Execute Claude
claude --system-prompt "$SYSTEM_PROMPT" $REMAINING_ARGS
