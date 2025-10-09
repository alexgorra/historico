#!/bin/bash
# Game Run Script
# Removes existing virtual environment, creates new one, installs pygame, and runs the game

echo "Setting up game environment..."

# Navigate to src directory
cd src

# Remove existing virtual environment if it exists
if [ -d "game_env" ]; then
    echo "Removing existing virtual environment..."
    rm -rf game_env
fi

# Create new virtual environment
echo "Creating new virtual environment..."
python3 -m venv game_env

# Activate virtual environment
echo "Activating virtual environment..."
source game_env/bin/activate

# Install pygame
echo "Installing pygame..."
pip install pygame

# Run the game
echo "Starting the game..."
python3 game_client.py

# Deactivate virtual environment
deactivate

# Return to original directory
cd ..

echo "Game script completed."