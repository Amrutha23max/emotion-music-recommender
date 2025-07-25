#!/usr/bin/env python3
"""
Emotion Music Recommender - Development Setup Script
Run this script to set up your development environment
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e.stderr}")
        return False

def create_env_file():
    """Create .env file from template"""
    env_example = Path(".env.example")
    env_file = Path(".env")
    
    if not env_file.exists() and env_example.exists():
        print("\n🔧 Creating .env file from template...")
        env_content = env_example.read_text()
        env_file.write_text(env_content)
        print("✅ .env file created! Please update it with your actual credentials.")
    else:
        print("ℹ️  .env file already exists or template not found")

def main():
    print("🎵 Emotion Music Recommender - Development Setup")
    print("=" * 50)
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return
    
    print(f"✅ Python version: {sys.version}")
    
    # Create virtual environment if it doesn't exist
    if not Path("venv").exists():
        if not run_command("python -m venv venv", "Creating virtual environment"):
            return
    
    # Activate virtual environment and install dependencies
    if os.name == 'nt':  # Windows
        pip_command = "venv\\Scripts\\pip"
        python_command = "venv\\Scripts\\python"
    else:  # Unix/Linux/MacOS
        pip_command = "venv/bin/pip"
        python_command = "venv/bin/python"
    
    # Upgrade pip
    run_command(f"{pip_command} install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    if not run_command(f"{pip_command} install -r requirements.txt", "Installing Python dependencies"):
        print("⚠️  Some packages might have failed to install. Check the output above.")
    
    # Create .env file
    create_env_file()
    
    # Create necessary directories
    directories = [
        "data/datasets",
        "data/processed", 
        "models/emotion_detection",
        "models/music_features",
        "logs"
    ]
    
    print("\n📁 Creating project directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    print("✅ Project directories created!")
    
    # Check if we can import key packages
    print("\n🧪 Testing key imports...")
    test_imports = [
        ("fastapi", "FastAPI"),
        ("cv2", "OpenCV"),
        ("tensorflow", "TensorFlow"),
        ("sklearn", "Scikit-learn"),
        ("spotipy", "Spotipy")
    ]
    
    failed_imports = []
    for package, name in test_imports:
        try:
            __import__(package)
            print(f"✅ {name} imported successfully")
        except ImportError:
            print(f"❌ {name} import failed")
            failed_imports.append(name)
    
    # Final instructions
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    
    if failed_imports:
        print(f"⚠️  Some packages failed to import: {', '.join(failed_imports)}")
        print("   You might need to install them manually or check for compatibility issues.")
    
    print("\n📋 Next steps:")
    print("1. Update .env file with your Spotify API credentials")
    print("2. Run the backend: python backend/main.py")
    print("3. Open http://localhost:8000/docs to see the API documentation")
    print("4. Start building the frontend!")
    
    print("\n🚀 Happy coding!")

if __name__ == "__main__":
    main()
