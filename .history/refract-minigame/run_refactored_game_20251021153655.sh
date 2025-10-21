#!/bin/bash
# Refactored Game Run Script

echo "Setting up game environment..."

cd "$(dirname "$0")"

if [ -d "game_env" ]; then
    echo "Removing existing virtual environment..."
    rm -rf game_env
fi

echo "Creating new virtual environment..."
python3 -m venv game_env

echo "Activating virtual environment..."
source game_env/bin/activate

echo "Installing pygame..."
pip install pygame

echo "Starting the game..."
cd game
python3 main.py

deactivate

cd ..

echo "Game script completed."
