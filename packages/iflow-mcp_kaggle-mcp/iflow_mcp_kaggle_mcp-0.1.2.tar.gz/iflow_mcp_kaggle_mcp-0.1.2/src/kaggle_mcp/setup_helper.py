#!/usr/bin/env python3
"""
Setup helper for Kaggle-MCP

This script helps users set up Kaggle-MCP with Claude Desktop by:
1. Finding the Claude Desktop config file
2. Adding the necessary configuration to the mcpServers section
3. Checking for Kaggle API credentials
"""

import os
import json
import sys
import shutil
from pathlib import Path

def find_claude_config():
    """Find the Claude Desktop configuration file"""
    # Common locations for the Claude Desktop config file
    possible_locations = []
    
    # macOS
    if sys.platform == 'darwin':
        possible_locations.append(Path.home() / "Library/Application Support/Claude/claude_desktop_config.json")
    
    # Windows
    elif sys.platform == 'win32':
        app_data = os.environ.get('APPDATA', '')
        if app_data:
            possible_locations.append(Path(app_data) / "Claude/claude_desktop_config.json")
    
    # Linux
    else:
        config_home = os.environ.get('XDG_CONFIG_HOME', Path.home() / '.config')
        possible_locations.append(Path(config_home) / "Claude/claude_desktop_config.json")
    
    # Check all possible locations
    for location in possible_locations:
        if location.exists():
            return location
    
    return None

def check_kaggle_credentials():
    """Check if Kaggle credentials are configured"""
    kaggle_json_path = Path.home() / ".kaggle/kaggle.json"
    
    if kaggle_json_path.exists():
        # Check if the file has proper permissions
        try:
            permissions = oct(kaggle_json_path.stat().st_mode)[-3:]
            if permissions != '600':
                print(f"Warning: Your Kaggle API key file permissions are {permissions}")
                print("For security, this should be set to 600 (user read/write only)")
                print(f"Run: chmod 600 {kaggle_json_path}")
        except Exception:
            print("Warning: Could not check permissions on Kaggle API key file")
        
        return True
    
    print("Kaggle API credentials not found")
    print("You will need to set these up before using Kaggle-MCP")
    print("1. Go to https://www.kaggle.com/settings/account")
    print("2. Click 'Create New API Token' to download kaggle.json")
    print("3. Move this file to ~/.kaggle/kaggle.json")
    print("4. Set correct permissions with: chmod 600 ~/.kaggle/kaggle.json")
    print("\nAlternatively, you can use the authenticate() tool in Claude to set up your credentials.")
    
    return False

def setup_claude_config():
    """Set up the Claude Desktop configuration for Kaggle-MCP"""
    config_file = find_claude_config()
    
    if not config_file:
        print("Could not find Claude Desktop configuration file.")
        print("Please manually add the configuration to your Claude Desktop config.")
        print_manual_instructions()
        return False
    
    print(f"Found Claude Desktop configuration at: {config_file}")
    
    # Read the existing config
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        # If the file doesn't exist or is not valid JSON, start with an empty config
        config = {}
    
    # Ensure mcpServers section exists
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
    
    # Find the full path to kaggle-mcp
    kaggle_mcp_path = find_kaggle_mcp_path()
    
    # Add the Kaggle-MCP configuration with full path
    kaggle_mcp_config = {
        "command": kaggle_mcp_path if kaggle_mcp_path else "kaggle-mcp"
    }
    
    # Add to the config
    config['mcpServers']['kaggle'] = kaggle_mcp_config
    
    # Write the updated config back to the file
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        
        print("\nSuccessfully updated Claude Desktop configuration!")
        if kaggle_mcp_path:
            print(f"Using kaggle-mcp at: {kaggle_mcp_path}")
        else:
            print("Warning: Could not find full path to kaggle-mcp, using command name only.")
        print("Please restart Claude Desktop for the changes to take effect.")
        return True
    except Exception as e:
        print(f"Error updating configuration file: {str(e)}")
        print_manual_instructions()
        return False
def print_manual_instructions():
    """Print instructions for manual configuration"""
    print("\nManual Configuration Instructions:")
    print("1. Open Claude Desktop")
    print("2. Go to Settings > Developer > Edit Config")
    print("3. Add the following to your claude_desktop_config.json:")
    
    # Try to find the full path for the manual instructions
    kaggle_mcp_path = find_kaggle_mcp_path()
    command_value = kaggle_mcp_path if kaggle_mcp_path else "kaggle-mcp"
    
    print(f"""
{{
    "mcpServers": {{
        "kaggle": {{
            "command": "{command_value}"
        }}
    }}
}}
""")
    
    print("4. Save the file and restart Claude Desktop")

def find_kaggle_mcp_path():
    """Find the full path to the kaggle-mcp executable
    
    Returns:
        str: Full path to kaggle-mcp or None if not found
    """
    # Try to find in PATH
    search_paths = os.environ.get("PATH", "").split(os.pathsep)
    
    # Add common bin directories
    if sys.platform == 'darwin':  # macOS
        for path in ['/usr/local/bin', '/opt/homebrew/bin']:
            if path not in search_paths:
                search_paths.append(path)
    elif sys.platform == 'win32':  # Windows
        # Add scripts directory in Python installation
        if hasattr(sys, 'base_prefix'):
            scripts_dir = os.path.join(sys.base_prefix, 'Scripts')
            if scripts_dir not in search_paths:
                search_paths.append(scripts_dir)
    else:  # Linux/Unix
        for path in ['/usr/local/bin', '/usr/bin', '/bin']:
            if path not in search_paths:
                search_paths.append(path)
    
    # Look for kaggle-mcp in all search paths
    for path in search_paths:
        executable = os.path.join(path, 'kaggle-mcp')
        # Add .exe extension for Windows
        if sys.platform == 'win32' and not executable.endswith('.exe'):
            executable += '.exe'
        
        if os.path.isfile(executable) and os.access(executable, os.X_OK):
            return executable
    
    # Check if we're running from a development environment (e.g., with python -m)
    try:
        import kaggle_mcp
        main_module = getattr(kaggle_mcp, '__main__', None)
        if main_module and hasattr(main_module, '__file__'):
            # Running from source, use Python to execute the module
            python_exec = sys.executable
            if python_exec:
                kaggle_mcp_module = 'kaggle_mcp.server'
                return f"{python_exec} -m {kaggle_mcp_module}"
    except ImportError:
        pass
    
    # Could not find the executable
    return None

def main():
    """Main function"""
    import argparse
    
    # Create argument parser
    parser = argparse.ArgumentParser(
        description="Kaggle-MCP Setup Helper: Configure Claude Desktop to use Kaggle-MCP."
    )
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle version flag
    if args.version:
        import kaggle_mcp
        print(f"Kaggle-MCP Setup Helper version {kaggle_mcp.__version__}")
        return 0
    
    print("Kaggle-MCP Setup Helper")
    print("======================")
    print("This utility will help you configure Claude Desktop to use Kaggle-MCP.")
    
    # Check Kaggle credentials
    print("\nChecking Kaggle API credentials...")
    check_kaggle_credentials()
    
    # Run the setup
    print("\nConfiguring Claude Desktop...")
    success = setup_claude_config()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
