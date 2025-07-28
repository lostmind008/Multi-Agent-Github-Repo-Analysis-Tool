#!/usr/bin/env python3
"""
Automated setup script for Multi-Agent GitHub Repository Analysis Tool
Handles environment creation, dependency installation, and configuration.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

class SetupManager:
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.venv_path = self.project_root / "venv"
        self.python_cmd = self.get_python_command()
        self.system = platform.system().lower()
        
    def get_python_command(self):
        """Get the appropriate Python command for this system."""
        for cmd in ["python3", "python"]:
            try:
                result = subprocess.run([cmd, "--version"], capture_output=True, text=True)
                if result.returncode == 0 and "Python 3." in result.stdout:
                    return cmd
            except FileNotFoundError:
                continue
        raise RuntimeError("Python 3.8+ is required but not found")
    
    def check_python_version(self):
        """Ensure Python version is compatible."""
        version = sys.version_info
        if version.major != 3 or version.minor < 8:
            raise RuntimeError(f"Python 3.8+ required, got {version.major}.{version.minor}")
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    
    def create_virtual_environment(self):
        """Create virtual environment if it doesn't exist."""
        if self.venv_path.exists():
            print("✅ Virtual environment already exists")
            return
        
        print("🔨 Creating virtual environment...")
        subprocess.run([self.python_cmd, "-m", "venv", str(self.venv_path)], check=True)
        print("✅ Virtual environment created")
    
    def get_venv_python(self):
        """Get path to virtual environment Python executable."""
        if self.system == "windows":
            return str(self.venv_path / "Scripts" / "python.exe")
        else:
            return str(self.venv_path / "bin" / "python")
    
    def get_venv_pip(self):
        """Get path to virtual environment pip executable."""
        if self.system == "windows":
            return str(self.venv_path / "Scripts" / "pip.exe")
        else:
            return str(self.venv_path / "bin" / "pip")
    
    def upgrade_pip(self):
        """Upgrade pip to latest version."""
        print("🔨 Upgrading pip...")
        subprocess.run([
            self.get_venv_python(), "-m", "pip", "install", "--upgrade", "pip"
        ], check=True)
        print("✅ Pip upgraded")
    
    def install_dependencies(self):
        """Install project dependencies."""
        requirements_file = "requirements-updated.txt"
        if not (self.project_root / requirements_file).exists():
            requirements_file = "requirements.txt"
        
        print(f"🔨 Installing dependencies from {requirements_file}...")
        subprocess.run([
            self.get_venv_pip(), "install", "-r", requirements_file
        ], check=True)
        print("✅ Dependencies installed")
    
    def setup_environment_file(self):
        """Create .env file from template if it doesn't exist."""
        env_file = self.project_root / ".env"
        env_example = self.project_root / ".env.example"
        
        if env_file.exists():
            print("✅ .env file already exists")
            return
        
        if env_example.exists():
            shutil.copy(env_example, env_file)
            print("✅ .env file created from template")
            print("⚠️  Please edit .env file with your API keys")
        else:
            print("❌ .env.example not found")
    
    def create_run_scripts(self):
        """Create platform-specific run scripts."""
        # Unix/macOS run script
        unix_script = self.project_root / "run.sh"
        unix_content = f'''#!/bin/bash
# Multi-Agent GitHub Analysis Tool - Frictionless Runner
# No need to activate virtual environment manually!

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${{BASH_SOURCE[0]}}" )" &> /dev/null && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run setup.py first."
    exit 1
fi

# Run with virtual environment Python
./venv/bin/python main.py "$@"
'''
        unix_script.write_text(unix_content)
        unix_script.chmod(0o755)
        
        # Windows run script
        windows_script = self.project_root / "run.ps1"
        windows_content = '''# Multi-Agent GitHub Analysis Tool - Frictionless Runner
# No need to activate virtual environment manually!

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Check if virtual environment exists
if (!(Test-Path "venv")) {
    Write-Host "❌ Virtual environment not found. Run setup.py first." -ForegroundColor Red
    exit 1
}

# Run with virtual environment Python
& ".\\venv\\Scripts\\python.exe" main.py $args
'''
        windows_script.write_text(windows_content)
        
        # Windows batch script for compatibility
        batch_script = self.project_root / "run.bat"
        batch_content = '''@echo off
REM Multi-Agent GitHub Analysis Tool - Frictionless Runner

cd /d "%~dp0"

if not exist "venv" (
    echo ❌ Virtual environment not found. Run setup.py first.
    exit /b 1
)

.\\venv\\Scripts\\python.exe main.py %*
'''
        batch_script.write_text(batch_content)
        
        print("✅ Run scripts created (run.sh, run.ps1, run.bat)")
    
    def validate_installation(self):
        """Validate that installation was successful."""
        print("🔍 Validating installation...")
        
        try:
            # Test import of critical modules
            result = subprocess.run([
                self.get_venv_python(), "-c", 
                "import langchain, langgraph, github, reportlab; print('All modules imported successfully')"
            ], capture_output=True, text=True, check=True)
            print("✅ All dependencies validated")
            
            # Test main.py --validate-only
            result = subprocess.run([
                self.get_venv_python(), "main.py", "--validate-only"
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Application validation successful")
            else:
                print("⚠️  Application validation found issues (likely missing API keys)")
                print("   This is normal - configure your .env file with API keys")
        
        except subprocess.CalledProcessError as e:
            print(f"❌ Validation failed: {e}")
            print("   Some dependencies may not be properly installed")
    
    def setup(self):
        """Run complete setup process."""
        print("🚀 Multi-Agent GitHub Analysis Tool - Automated Setup")
        print("   Built by LostMind AI (www.LostMindAI.com)")
        print()
        
        try:
            self.check_python_version()
            self.create_virtual_environment()
            self.upgrade_pip()
            self.install_dependencies()
            self.setup_environment_file()
            self.create_run_scripts()
            self.validate_installation()
            
            print()
            print("🎉 Setup Complete!")
            print()
            print("Next steps:")
            print("  1. Edit .env file with your API keys")
            print("  2. Run analysis with: ./run.sh --user YOUR_USERNAME")
            print("     (Windows: .\\run.ps1 --user YOUR_USERNAME)")
            print()
            print("No need to activate virtual environment - the run scripts handle it!")
            
        except Exception as e:
            print(f"❌ Setup failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    setup_manager = SetupManager()
    setup_manager.setup()