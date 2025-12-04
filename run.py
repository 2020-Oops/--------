#!/usr/bin/env python3
"""
Launcher script for Arkanoid Game
Запускає гру Арканоїд
"""
import sys
from pathlib import Path

# Add src directory to Python path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

if __name__ == '__main__':
    # Import and run the game
    from main import *  # This will execute the game loop
