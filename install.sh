#!/bin/bash
# Multi-Agent GitHub Analysis Tool - Universal Installer
# Works on macOS, Linux, and Windows (with bash)
# Built by LostMind AI (www.LostMindAI.com)

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_header() {
    echo -e "${BLUE}🚀 Multi-Agent GitHub Analysis Tool - Universal Installer${NC}"
    echo -e "${BLUE}   Built by LostMind AI (www.LostMindAI.com)${NC}"
    echo
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        OS="linux"
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
    elif [[ "$OSTYPE" == "cygwin" ]] || [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        OS="windows"
    else
        OS="unknown"
    fi
    print_info "Detected OS: $OS"
}

# Check if Python 3.8+ is available
check_python() {
    print_info "Checking Python installation..."
    
    PYTHON_CMD=""
    for cmd in python3 python; do
        if command -v "$cmd" >/dev/null 2>&1; then
            VERSION=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
            MAJOR=$(echo "$VERSION" | cut -d. -f1)
            MINOR=$(echo "$VERSION" | cut -d. -f2)
            
            if [[ "$MAJOR" -eq 3 ]] && [[ "$MINOR" -ge 8 ]]; then
                PYTHON_CMD="$cmd"
                print_success "Found Python $VERSION at $(which "$cmd")"
                break
            fi
        fi
    done
    
    if [[ -z "$PYTHON_CMD" ]]; then
        print_error "Python 3.8+ is required but not found"
        print_info "Please install Python 3.8+ and try again"
        exit 1
    fi
}

# Install system dependencies based on OS
install_system_deps() {
    print_info "Checking system dependencies..."
    
    case "$OS" in
        "linux")
            # Check if we have package manager access
            if command -v apt-get >/dev/null 2>&1; then
                print_info "Detected apt package manager"
                if [[ $EUID -eq 0 ]]; then
                    apt-get update && apt-get install -y python3-venv python3-pip git
                else
                    print_warning "Consider running: sudo apt-get install python3-venv python3-pip git"
                fi
            elif command -v yum >/dev/null 2>&1; then
                print_info "Detected yum package manager"
                if [[ $EUID -eq 0 ]]; then
                    yum install -y python3-venv python3-pip git
                else
                    print_warning "Consider running: sudo yum install python3-venv python3-pip git"
                fi
            fi
            ;;
        "macos")
            # Check if Homebrew is available
            if command -v brew >/dev/null 2>&1; then
                print_info "Homebrew detected - dependencies likely satisfied"
            else
                print_warning "Consider installing Homebrew for easier Python management"
            fi
            ;;
        "windows")
            print_info "Windows detected - ensure Python was installed with pip"
            ;;
    esac
}

# Run the Python setup script
run_setup() {
    print_info "Running automated Python setup..."
    
    if [[ -f "setup.py" ]]; then
        "$PYTHON_CMD" setup.py
    else
        print_error "setup.py not found in current directory"
        print_info "Please run this script from the project root directory"
        exit 1
    fi
}

# Create convenience aliases
create_aliases() {
    print_info "Creating convenience commands..."
    
    # Make run scripts executable
    if [[ -f "run.sh" ]]; then
        chmod +x run.sh
        print_success "run.sh made executable"
    fi
    
    # Create global command if requested
    read -p "Create global 'github-analyzer' command? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        SCRIPT_PATH="$(pwd)/run.sh"
        
        case "$OS" in
            "linux"|"macos")
                if [[ -w "/usr/local/bin" ]]; then
                    ln -sf "$SCRIPT_PATH" "/usr/local/bin/github-analyzer"
                    print_success "Global command created: github-analyzer"
                else
                    print_warning "Cannot create global command (permission denied)"
                    print_info "You can manually add: alias github-analyzer='$SCRIPT_PATH'"
                fi
                ;;
            "windows")
                print_info "For Windows, add the project directory to your PATH"
                print_info "Or use the full path: $SCRIPT_PATH"
                ;;
        esac
    fi
}

# Main installation process
main() {
    print_header
    
    detect_os
    check_python
    install_system_deps
    run_setup
    create_aliases
    
    echo
    print_success "Installation Complete!"
    echo
    print_info "Quick Start:"
    echo "  1. Edit .env file with your API keys"
    echo "  2. Run: ./run.sh --user YOUR_USERNAME"
    echo
    print_info "For help: ./run.sh --help"
    print_info "Documentation: https://github.com/lostmind008/Multi-Agent-Github-Repo-Analysis-Tool"
}

# Handle script interruption
trap 'print_error "Installation interrupted"; exit 1' INT TERM

# Run main function
main "$@"