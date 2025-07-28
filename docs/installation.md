# Installation Guide

This guide will help you install and set up Discord Username Monitor.

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows 10+, macOS 10.15+, or Linux
- **RAM**: Minimum 2GB, recommended 4GB+
- **Storage**: 500MB free space
- **Internet**: Stable broadband connection
- **Browser**: Google Chrome (required for session acquisition)

## Installation Methods

### Method 1: Git Clone (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/discord-username-monitor.git
cd discord-username-monitor

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Method 2: Download ZIP

1. Download the latest release from GitHub
2. Extract the ZIP file to your desired location
3. Open terminal/command prompt in the extracted folder
4. Follow the virtual environment setup above

### Method 3: pip install (Coming Soon)

```bash
pip install discord-username-monitor
```

## Quick Start

1. **Run the setup script**:
   ```bash
   # Windows
   scripts\setup.bat
   
   # macOS/Linux
   bash scripts/setup.sh
   ```

2. **Add your tokens**:
   - Copy `accounts/tokens.txt.example` to `accounts/tokens.txt`
   - Add your Discord account credentials

3. **Run the monitor**:
   ```bash
   python src/main.py
   ```

## Detailed Setup

### 1. Python Installation

#### Windows
- Download Python from [python.org](https://python.org)
- During installation, check "Add Python to PATH"
- Verify: `python --version`

#### macOS
```bash
# Using Homebrew
brew install python

# Or download from python.org
```

#### Linux (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### 2. Chrome Installation

The tool requires Google Chrome for browser session acquisition:

- **Windows/macOS**: Download from [google.com/chrome](https://google.com/chrome)
- **Linux**: 
  ```bash
  # Ubuntu/Debian
  wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
  sudo sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
  sudo apt update
  sudo apt install google-chrome-stable
  ```

### 3. Virtual Environment (Recommended)

Using a virtual environment prevents dependency conflicts:

```bash
# Create virtual environment
python -m venv discord-monitor-env

# Activate it
# Windows:
discord-monitor-env\Scripts\activate
# macOS/Linux:
source discord-monitor-env/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configuration

#### Token Setup
1. Create `accounts/tokens.txt` from the example file
2. Add your Discord tokens in supported formats
3. The tool will validate tokens on startup

#### Webhook Setup
- Configure Discord webhook URLs during first run
- Test webhooks automatically
- Support for multiple webhook categories

#### Username Lists
- Create custom lists in `usernames/` directory
- Use built-in dictionary word generation
- Generate random usernames with specified parameters

## Troubleshooting

### Common Issues

#### "Chrome not found"
- Ensure Google Chrome is installed and in PATH
- Try specifying Chrome location in config

#### "Module not found" errors
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

#### "Permission denied" errors
- **Windows**: Run as Administrator
- **macOS/Linux**: Check file permissions with `chmod +x`

#### Token validation fails
- Verify token format and validity
- Check internet connection
- Ensure tokens haven't expired

#### Webhook notifications not working
- Test webhook URLs in Discord
- Check firewall settings
- Verify webhook permissions

### Performance Issues

#### High memory usage
- Reduce thread count in configuration
- Close unnecessary browser tabs during session acquisition
- Check for memory leaks in logs

#### Slow username checking
- Enable proxy rotation
- Adjust delay settings
- Check internet connection speed

#### Rate limiting
- Reduce thread count
- Increase delays between requests
- Enable proxy support

## Advanced Configuration

### Custom Settings
Edit `config/settings.json` for advanced options:
- Thread counts and delays
- Browser behavior
- Logging levels
- Proxy settings

### Environment Variables
```bash
export DEBUG_MODE=1          # Enable debug logging
export HEADLESS_BROWSER=1    # Run browser in headless mode
export MAX_THREADS=10        # Override default thread count
```

### Proxy Configuration
- Add proxies to `proxies/proxies.txt`
- Supports HTTP/HTTPS proxies
- Automatic rotation and validation
- Format: `ip:port` or `ip:port:user:pass`

## Next Steps

- Read the [Configuration Guide](configuration.md)
- Check the [API Reference](api_reference.md)
- Review [Troubleshooting](troubleshooting.md)
- Join the community discussions

## Support

If you encounter issues:
1. Check this installation guide
2. Review the troubleshooting section
3. Search existing GitHub issues
4. Create a new issue with detailed information

Happy monitoring!