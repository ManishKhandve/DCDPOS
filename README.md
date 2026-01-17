# DCDPOS - Distributed Computer Device Control System

A distributed computer automation system that lets you control multiple devices using natural language commands through Telegram. Uses **Ollama** (local LLM) to interpret commands - no cloud API keys required!

---

## SECURITY WARNING

> **NO SECURITY MEASURES IMPLEMENTED**
> 
> This project is a proof-of-concept and does **NOT** include any security features:
> - No authentication or authorization
> - No encryption of communications
> - No input validation or sanitization
> - No rate limiting
> - No audit logging for security purposes
> 
> **Device agents have unrestricted system access and execute arbitrary code. This is designed for trusted networks only.**

### Risks:
- Anyone on the same network can send commands to device agents
- Malicious commands can damage systems, steal data, or compromise security
- The Telegram bot token, if exposed, allows anyone to control your devices
- Commands are transmitted in plaintext over HTTP

### Recommendations:
- Only use on isolated, trusted networks
- Never expose ports to the internet
- Keep your Telegram bot token secret
- Consider this for educational/experimental purposes only

---

## Architecture

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Telegram      │────▶│  Central Parser  │────▶│  Device Agent   │
│   User Input    │     │  (Flask + Ollama)│     │  (Flask Server) │
└─────────────────┘     └──────────────────┘     └─────────────────┘
        │                       │                        │
        │                       ▼                        │
        │               ┌───────────────┐                │
        │               │  Ollama LLM   │                │
        │               │  (Local AI)   │                │
        │               └───────────────┘                │
        │                                                │
        └─────────── Same Network (LAN/WiFi) ────────────┘
```

**Components:**
1. **Telegram Bot** (`TELEGRAM_BOT.PY`) - User interface for sending commands via Telegram
2. **Central Parser** (`CENTRAL_PARSER.PY`) - Brain of the system; uses Ollama to understand natural language and generate executable code
3. **Device Agent** (`DEVICE_AGENT.PY`) - Runs on each controlled device; receives and executes commands

**How it works:**
1. User sends a command via Telegram (e.g., "Open Chrome on alpha")
2. Telegram Bot forwards the command to Central Parser
3. Central Parser uses Ollama LLM to interpret the command
4. Central Parser generates Python code and sends it to the target Device Agent
5. Device Agent executes the code on the target machine
6. Result is sent back to user via Telegram

---

## Current Limitations

> **This is a proof-of-concept with limited functionality**

**What it CAN do:**
- Open predefined applications (Chrome, VS Code, Notepad, Figma, Spotify, etc.)
- Open websites (YouTube, GitHub, Gmail)
- Search on Google/YouTube
- Take screenshots
- System actions (shutdown, restart, lock screen)
- Media controls (play/pause, volume, next/previous track)
- Basic automation (type text, press keys, click, scroll)
- File operations (create folder, list files)
- System monitoring (battery, disk usage)

**What it CANNOT do (yet):**
- Interactive conversations or context-aware responses
- Complex multi-step workflows
- Read screen content or understand what's displayed
- Interact with application contents (click buttons inside apps, fill forms)
- Remember previous commands or maintain session state
- Custom or dynamic command generation beyond predefined patterns

The LLM is only used to **map natural language to predefined command patterns**, not to generate arbitrary code or interact with applications intelligently.

---

## Features

- **Natural Language Processing** - Uses Ollama (local LLM like Llama 3) to understand commands
- **Multi-Device Control** - Control multiple computers from one Telegram interface
- **Telegram Integration** - Send commands from anywhere via Telegram
- **48+ Predefined Commands** - Applications, web, files, system, automation
- **100% Local** - No cloud APIs, everything runs on your network
- **Cross-Platform** - Works on Windows, Linux, and macOS

### Supported Commands

| Category | Commands |
|----------|----------|
| **Applications** | Open VS Code, Chrome, Figma, Notepad, Calculator, File Explorer, Terminal, Spotify, Discord, **any app** |
| **Web** | Open YouTube, GitHub, Gmail, Search Google/YouTube |
| **Files** | Take screenshot, Create folder, List files, Delete file |
| **System** | Shutdown, Restart, Lock screen, System info |
| **Media** | Play/Pause, Next/Previous track, Volume up/down/mute |
| **Automation** | Type text, Press keys, Mouse click, Scroll up/down |
| **Window** | Minimize, Maximize, Switch windows |
| **Clipboard** | Copy, Paste, Select all, Undo |
| **Monitoring** | Battery status, Disk usage, Running processes |

---

## Requirements

### Main PC (Central Server)
- Python 3.8+
- Ollama with a model (e.g., llama3, llama3.2, mistral)
- Telegram Bot Token

### Controlled Devices (Device Agents)
- Python 3.8+
- Network access to Central Server

### Python Dependencies

**For Central Server & Telegram Bot** (`requirements.txt`):
```
flask
requests
pyautogui
psutil
python-telegram-bot==20.3
pillow
```

**For Device Agents** (`requirements2.txt`):
```
flask
requests
pyautogui
psutil
pillow
```

---

## Setup

### Step 1: Install Ollama (on Main PC only)

Download from https://ollama.ai or run:
```bash
# Windows
winget install Ollama.Ollama

# Linux
curl -fsSL https://ollama.com/install.sh | sh
```

Pull a model:
```bash
ollama pull llama3
```

Verify it's running:
```bash
ollama list
```

### Step 2: Create Telegram Bot

1. Open Telegram and search for [@BotFather](https://t.me/botfather)
2. Send `/newbot` and follow instructions
3. Give your bot a name and username
4. **Copy the bot token** (looks like `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`)

### Step 3: Find Your Main PC's IP Address

```bash
# Windows
ipconfig

# Linux/Mac
ifconfig
```

Look for your IPv4 address (e.g., `192.168.1.100` or `10.39.103.1`)

### Step 4: Install Dependencies

**On Main PC:**
```bash
cd path/to/dcdppos
pip install -r requirements.txt
```

**On each Device Agent PC:**
```bash
cd path/to/dcdppos
pip install -r requirements2.txt
```

### Step 5: Configure Files

**CENTRAL_PARSER.PY** (Lines 11-12):
```python
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"  # Change to your installed model
```

**TELEGRAM_BOT.PY** (Lines 5-6):
```python
BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CENTRAL_PARSER_URL = "http://127.0.0.1:5000/command"  # Use 127.0.0.1 if bot runs on same PC
```

**DEVICE_AGENT.PY** (Lines 12-13) - on each controlled device:
```python
DEVICE_NAME = "alpha"  # Unique name for each device (alpha, beta, gamma, etc.)
CENTRAL_SERVER_IP = "10.39.103.1"  # Your main PC's IP address (NOT 127.0.0.1)
```

> **Important:** `CENTRAL_SERVER_IP` should be the actual IP of your main PC, not `127.0.0.1`, unless the device agent runs on the same machine.

---

## Running the System

### 1. Start Central Parser (on Main PC):
```bash
python CENTRAL_PARSER.PY
```

You should see:
```
Starting Enhanced DCDPOS Central Parser...
Total Commands Available: 48
Running on http://127.0.0.1:5000
Running on http://10.39.103.1:5000
```

### 2. Start Device Agent (on each controlled PC):
```bash
python DEVICE_AGENT.PY
```

You should see:
```
[alpha] Starting DCDPOS Device Agent with FULL OS ACCESS...
[alpha] Successfully registered with central parser
[alpha] Device agent running on port 8080
```

### 3. Start Telegram Bot (on Main PC):
```bash
python TELEGRAM_BOT.PY
```

The bot will start silently and listen for messages.

---

## Usage

### Command Format
```
<action> on <device_name>
```

### Examples

**Opening Applications:**
```
Open Chrome on alpha
Open VS Code on alpha
Open Figma on alpha
Open Spotify on alpha
Open calculator on alpha
Open notepad on alpha
```

**Web Browsing:**
```
Open YouTube on alpha
Open GitHub on alpha
Search Python tutorials on YouTube on alpha
Search weather on Google on alpha
```

**Screenshots & Files:**
```
Take screenshot on alpha
Create folder called projects on alpha
List files on alpha
```

**System Control:**
```
Lock screen on alpha
Shutdown on alpha
Restart on alpha
Get system info on alpha
```

**Volume & Media:**
```
Volume up on alpha
Volume down on alpha
Mute on alpha
Play pause on alpha
Next track on alpha
Previous track on alpha
```

**Automation:**
```
Type hello world on alpha
Press ctrl+c on alpha
Press alt+tab on alpha
Scroll down on alpha
Scroll up on alpha
```

**Window Management:**
```
Minimize window on alpha
Maximize window on alpha
Switch window on alpha
```

**Clipboard:**
```
Copy on alpha
Paste on alpha
Select all on alpha
Undo on alpha
Refresh page on alpha
```

**System Monitoring:**
```
Battery status on alpha
Disk usage on alpha
Check processes on alpha
Get IP address on alpha
Check internet on alpha
```

---

## API Endpoints

### Central Parser (Port 5000)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/command` | POST | Process natural language command |
| `/devices` | GET | List registered devices |
| `/commands` | GET | List all available commands |
| `/register` | POST | Register a device agent |
| `/test-ai` | POST | Test Ollama connectivity |

### Device Agent (Port 8080)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/execute` | POST | Execute generated code |
| `/status` | GET | Device health check |
| `/test` | POST | Test device capabilities |
| `/run_command` | POST | Run system command |

---

## Troubleshooting

### Ollama not responding
```bash
# Check if Ollama is running
ollama list

# Start/restart Ollama
ollama serve
```

### "Device not found" error
- Make sure Device Agent is running on the target PC
- Check that `CENTRAL_SERVER_IP` in DEVICE_AGENT.PY is correct (your main PC's IP)
- Verify both devices are on the same network
- Check Central Parser terminal - you should see "Device registered: <name>"

### Device Agent won't start
- Check for typos: use `__name__` (double underscores), not `_name_`
- Make sure all dependencies are installed: `pip install -r requirements2.txt`

### Telegram bot not responding
- Verify bot token is correct
- Check `CENTRAL_PARSER_URL` points to correct IP
- Ensure Central Parser is running
- Check for Markdown parsing errors in bot responses

### Firewall issues
```bash
# Windows - Allow ports through firewall
netsh advfirewall firewall add rule name="DCDPOS Central" dir=in action=allow protocol=tcp localport=5000
netsh advfirewall firewall add rule name="DCDPOS Agent" dir=in action=allow protocol=tcp localport=8080
```

### Command not recognized
- Check the Central Parser terminal for debug output
- The command might not be in the predefined list
- Try rephrasing the command (e.g., "open youtube" instead of "launch youtube")

---

## File Structure

```
dcdppos/
├── CENTRAL_PARSER.PY    # Main server with Ollama integration
├── DEVICE_AGENT.PY      # Agent for controlled devices
├── TELEGRAM_BOT.PY      # Telegram interface
├── requirements.txt     # Dependencies for Central Server
├── requirements2.txt    # Dependencies for Device Agents
└── README.md            # This file
```

---

## License

This project is for educational purposes only. Use at your own risk.

---

## Disclaimer

This software is provided "as is" without warranty of any kind. The authors are not responsible for any damage, data loss, or security breaches resulting from the use of this software. **Use only in controlled, trusted environments.**
