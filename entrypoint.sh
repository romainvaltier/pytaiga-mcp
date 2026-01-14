#!/bin/bash

# Entrypoint script for pytaiga-mcp server
# Handles transport mode selection based on TAIGA_TRANSPORT environment variable

# Default to stdio if not specified
TRANSPORT=${TAIGA_TRANSPORT:-stdio}

if [ "$TRANSPORT" == "sse" ]; then
    # Run in SSE (Server-Sent Events) mode for HTTP/Docker
    exec python -m src.server --sse
else
    # Run in stdio mode for CLI/terminal access
    exec python -m src.server
fi
