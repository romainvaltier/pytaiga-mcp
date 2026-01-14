#!/bin/bash

# Entrypoint script for pytaiga-mcp server
# Transport mode is determined by TAIGA_TRANSPORT environment variable
# (handled in src/server.py __main__ block)

exec python -m src.server
