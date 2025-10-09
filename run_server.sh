#!/bin/bash
# Server Run Script
# Compiles and runs the Java GameServer

echo "Starting GameServer..."

# Navigate to src directory
cd src

# Compile the Java file
echo "Compiling GameServer.java..."
if javac GameServer.java; then
    echo "Compilation successful!"
    echo "Starting GameServer..."
    java GameServer
else
    echo "Compilation failed! Please check for errors."
    exit 1
fi

# Return to original directory
cd ..

echo "Server script completed."