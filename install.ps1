# Multi-Agent GitHub Analysis Tool - PowerShell Installer
# Works on Windows, macOS, and Linux with PowerShell
# Built by LostMind AI (www.LostMindAI.com)

# Enable strict mode for better error handling
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Helper functions for colored output
function Write-Header {
    Write-Host "🚀 Multi-Agent GitHub Analysis Tool - PowerShell Installer" -ForegroundColor Blue
    Write-Host "   Built by LostMind AI (www.LostMindAI.com)" -ForegroundColor Blue
    Write-Host ""
}

function Write-Success {
    param([string]$Message)
    Write-Host "✅ $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "⚠️  $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "❌ $Message" -ForegroundColor Red
}

function Write-Info {
    param([string]$Message)
    Write-Host "ℹ️  $Message" -ForegroundColor Cyan
}

# Detect operating system
function Get-OperatingSystem {
    if ($PSVersionTable.Platform -eq "Unix") {
        if (Test-Path "/System/Library/CoreServices/SystemVersion.plist") {
            return "macOS"
        } else {
            return "Linux"
        }
    } else {
        return "Windows"
    }
}

# Check Python installation
function Test-PythonInstallation {
    Write-Info "Checking Python installation..."
    
    $pythonCommands = @("python3", "python", "py")
    $pythonCmd = $null
    
    foreach ($cmd in $pythonCommands) {
        try {
            $version = & $cmd --version 2>&1
            if ($version -match "Python\s+(\d+)\.(\d+)") {
                $major = [int]$matches[1]
                $minor = [int]$matches[2]
                
                if ($major -eq 3 -and $minor -ge 8) {
                    $pythonCmd = $cmd
                    Write-Success "Found Python $($matches[0]) using command '$cmd'"
                    break
                }
            }
        }
        catch {
            # Command not found, continue to next
        }
    }
    
    if (-not $pythonCmd) {
        Write-Error "Python 3.8+ is required but not found"
        Write-Info "Please install Python 3.8+ from python.org and try again"
        exit 1
    }
    
    return $pythonCmd
}

# Install system dependencies
function Install-SystemDependencies {
    param([string]$OS)
    
    Write-Info "Checking system dependencies for $OS..."
    
    switch ($OS) {
        "Windows" {
            # Check if Python was installed with pip
            try {
                & python -m pip --version | Out-Null
                Write-Success "Pip is available"
            }
            catch {
                Write-Warning "Pip may not be available. Ensure Python was installed with pip."
            }
            
            # Check for Git
            try {
                & git --version | Out-Null
                Write-Success "Git is available"
            }
            catch {
                Write-Warning "Git not found. Consider installing Git for Windows."
            }
        }
        "macOS" {
            # Check for Homebrew
            try {
                & brew --version | Out-Null
                Write-Info "Homebrew detected - dependencies likely satisfied"
            }
            catch {
                Write-Warning "Consider installing Homebrew for easier package management"
            }
        }
        "Linux" {
            Write-Info "Linux detected. Ensure python3-venv and python3-pip are installed."
            Write-Info "On Ubuntu/Debian: sudo apt-get install python3-venv python3-pip"
            Write-Info "On RHEL/CentOS: sudo yum install python3-venv python3-pip"
        }
    }
}

# Run Python setup script
function Invoke-PythonSetup {
    param([string]$PythonCmd)
    
    Write-Info "Running automated Python setup..."
    
    if (Test-Path "setup.py") {
        try {
            & $PythonCmd setup.py
            Write-Success "Python setup completed successfully"
        }
        catch {
            Write-Error "Python setup failed: $($_.Exception.Message)"
            exit 1
        }
    }
    else {
        Write-Error "setup.py not found in current directory"
        Write-Info "Please run this script from the project root directory"
        exit 1
    }
}

# Create convenience commands
function New-ConvenienceCommands {
    param([string]$OS)
    
    Write-Info "Setting up convenience commands..."
    
    # Ensure run scripts are properly configured
    if (Test-Path "run.ps1") {
        Write-Success "PowerShell run script available"
    }
    
    if ($OS -eq "Windows" -and (Test-Path "run.bat")) {
        Write-Success "Batch run script available"
    }
    
    # Offer to create desktop shortcut on Windows
    if ($OS -eq "Windows") {
        $createShortcut = Read-Host "Create desktop shortcut? (y/n)"
        if ($createShortcut -eq "y" -or $createShortcut -eq "Y") {
            try {
                $desktopPath = [Environment]::GetFolderPath("Desktop")
                $shortcutPath = Join-Path $desktopPath "GitHub Analyzer.lnk"
                $targetPath = Join-Path $PWD "run.bat"
                
                $WScriptShell = New-Object -ComObject WScript.Shell
                $shortcut = $WScriptShell.CreateShortcut($shortcutPath)
                $shortcut.TargetPath = $targetPath
                $shortcut.WorkingDirectory = $PWD
                $shortcut.Description = "Multi-Agent GitHub Analysis Tool"
                $shortcut.Save()
                
                Write-Success "Desktop shortcut created"
            }
            catch {
                Write-Warning "Could not create desktop shortcut: $($_.Exception.Message)"
            }
        }
    }
}

# Test installation
function Test-Installation {
    Write-Info "Testing installation..."
    
    # Test run script
    $runScript = if (Test-Path "run.ps1") { ".\run.ps1" } 
                elseif (Test-Path "run.bat") { ".\run.bat" }
                else { $null }
    
    if ($runScript) {
        try {
            $output = & $runScript --validate-only 2>&1
            if ($LASTEXITCODE -eq 0) {
                Write-Success "Installation test passed"
            }
            else {
                Write-Warning "Installation test found issues (likely missing API keys)"
                Write-Info "This is normal - configure your .env file with API keys"
            }
        }
        catch {
            Write-Warning "Could not test installation: $($_.Exception.Message)"
        }
    }
}

# Main installation function
function Install-GitHubAnalyzer {
    try {
        Write-Header
        
        $os = Get-OperatingSystem
        Write-Info "Detected operating system: $os"
        
        $pythonCmd = Test-PythonInstallation
        Install-SystemDependencies -OS $os
        Invoke-PythonSetup -PythonCmd $pythonCmd
        New-ConvenienceCommands -OS $os
        Test-Installation
        
        Write-Host ""
        Write-Success "Installation Complete!"
        Write-Host ""
        Write-Info "Quick Start:"
        Write-Host "  1. Edit .env file with your API keys"
        if ($os -eq "Windows") {
            Write-Host "  2. Run: .\run.ps1 --user YOUR_USERNAME"
            Write-Host "     Or: .\run.bat --user YOUR_USERNAME"
        } else {
            Write-Host "  2. Run: ./run.sh --user YOUR_USERNAME"
        }
        Write-Host ""
        Write-Info "For help: $($runScript) --help"
        Write-Info "Documentation: https://github.com/lostmind008/Multi-Agent-Github-Repo-Analysis-Tool"
    }
    catch {
        Write-Error "Installation failed: $($_.Exception.Message)"
        exit 1
    }
}

# Handle script interruption
trap {
    Write-Error "Installation interrupted"
    exit 1
}

# Run installation
Install-GitHubAnalyzer