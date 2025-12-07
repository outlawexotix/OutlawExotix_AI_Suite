#!/bin/bash
AGENT_NAME=$1
shift
REMAINING_ARGS="$@"

# Resolve paths
TEMPLATE_PATH="$HOME/.claude/templates/${AGENT_NAME}.md"
MEMORY_PATH="$HOME/.claude/memory_protocol.md"

# Check if agent exists
if [ ! -f "$TEMPLATE_PATH" ]; then
    echo "Error: Agent template '$AGENT_NAME' not found at $TEMPLATE_PATH"
    exit 1
fi

# Combine Agent Persona + Memory Protocol
SYSTEM_PROMPT=$(cat "$TEMPLATE_PATH" "$MEMORY_PATH")

echo -e "\e[36mDeploying Agent: $AGENT_NAME (with Mnemosyne Memory)\e[0m"

# Execute Claude
claude --system-prompt "$SYSTEM_PROMPT" $REMAINING_ARGS
