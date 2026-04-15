#!/usr/bin/env python3
"""
Quick Start Script for Book RAG System
Handles virtual environment setup and launches the Streamlit app
"""

import os
import sys
import subprocess
import platform

def main():
    print("\n" + "="*40)
    print("  Book RAG System - Streamlit Launch")
    print("="*40 + "\n")
    
    # # Detect OS
    # system = platform.system()
    
    # # Check if virtual environment exists
    # env_exists = os.path.isdir("env")
    
    # if not env_exists:
    #     print("Creating virtual environment...")
    #     subprocess.run([sys.executable, "-m", "venv", "env"], check=True)
    #     print("✓ Virtual environment created\n")
    
    # # Activate virtual environment (for display purposes)
    # print("Activating virtual environment...")
    
    # # Determine the activate script based on OS
    # if system == "Windows":
    #     activate_script = os.path.join("env", "Scripts", "activate.bat")
    #     activate_cmd = f"call {activate_script}"
    # else:
    #     activate_script = os.path.join("env", "bin", "activate")
    #     activate_cmd = f"source {activate_script}"
    
    # print(f"✓ Virtual environment ready\n")
    
    # # Install dependencies
    # print("Installing dependencies (if needed)...")
    # pip_executable = os.path.join(
    #     "env",
    #     "Scripts" if system == "Windows" else "bin",
    #     "pip"
    # )
    
    # subprocess.run([pip_executable, "install", "-r", "requirements.txt"], check=True)
    # print("✓ Dependencies installed\n")
    
    # Run Streamlit app
    print("Starting Streamlit application...")
    print("Opening in browser at http://localhost:8501\n")
    print("Press Ctrl+C to stop the server\n")
    
    # streamlit_executable = os.path.join(
    #     "env",
    #     "Scripts" if system == "Windows" else "bin",
    #     "streamlit"
    # )
    
    os.chdir("app")
    subprocess.run(["streamlit", "run", "app.py"])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
