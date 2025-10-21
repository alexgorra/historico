#!/bin/bash

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo "Starting GameServer..."

echo "Compiling GameServer.java..."
if javac GameServer.java; then
    echo "Compilation successful!"
    echo "Starting GameServer..."
    java GameServer
else
    echo "Compilation failed! Please check for errors."
    exit 1
fi

echo "Server script completed."