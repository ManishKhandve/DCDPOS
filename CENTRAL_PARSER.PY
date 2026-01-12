from flask import Flask, request, jsonify
import requests
import platform
import re
import json

app = Flask(__name__)

device_registry = {}

# Ollama local LLM setup
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"  # Change to your installed model (e.g., llama3.2, llama3, mistral, etc.)

# Comprehensive command patterns and their corresponding code (30+ commands)
COMMAND_PATTERNS = {
    # Applications (8 commands)
    'open_vscode': {
        'windows': 'subprocess.run(["code"], shell=True)\nprint("Opening VS Code")',
        'linux': 'subprocess.run(["code"])\nprint("Opening VS Code")',
        'darwin': 'subprocess.run(["code"])\nprint("Opening VS Code")'
    },
    
    'open_chrome': {
        'windows': 'subprocess.run(["start", "chrome"], shell=True)\nprint("Opening Chrome")',
        'linux': 'subprocess.run(["google-chrome"])\nprint("Opening Chrome")',
        'darwin': 'subprocess.run(["open", "-a", "Google Chrome"])\nprint("Opening Chrome")'
    },
    
    'open_figma': {
        'windows': 'subprocess.run(["start", "figma"], shell=True)\nprint("Opening Figma")',
        'linux': 'subprocess.run(["figma"])\nprint("Opening Figma")',
        'darwin': 'subprocess.run(["open", "-a", "Figma"])\nprint("Opening Figma")'
    },
    
    'open_app': {
        'windows': 'app_name = "{app_name}"\nsubprocess.run(["start", app_name], shell=True)\nprint(f"Opening {app_name}")',
        'linux': 'app_name = "{app_name}"\nsubprocess.run([app_name])\nprint(f"Opening {app_name}")',
        'darwin': 'app_name = "{app_name}"\nsubprocess.run(["open", "-a", app_name])\nprint(f"Opening {app_name}")'
    },
    
    'open_notepad': {
        'windows': 'os.startfile("notepad")\nprint("Opening Notepad")',
        'linux': 'subprocess.run(["gedit"])\nprint("Opening Text Editor")',
        'darwin': 'subprocess.run(["open", "-a", "TextEdit"])\nprint("Opening TextEdit")'
    },
    
    'open_calculator': {
        'windows': 'os.startfile("calc")\nprint("Opening Calculator")',
        'linux': 'subprocess.run(["gnome-calculator"])\nprint("Opening Calculator")',
        'darwin': 'subprocess.run(["open", "-a", "Calculator"])\nprint("Opening Calculator")'
    },
    
    'open_file_explorer': {
        'windows': 'os.startfile("explorer")\nprint("Opening File Explorer")',
        'linux': 'subprocess.run(["nautilus"])\nprint("Opening File Manager")',
        'darwin': 'subprocess.run(["open", "."])\nprint("Opening Finder")'
    },
    
    'open_terminal': {
        'windows': 'subprocess.run(["start", "cmd"], shell=True)\nprint("Opening Command Prompt")',
        'linux': 'subprocess.run(["gnome-terminal"])\nprint("Opening Terminal")',
        'darwin': 'subprocess.run(["open", "-a", "Terminal"])\nprint("Opening Terminal")'
    },
    
    'open_spotify': {
        'windows': 'subprocess.run(["start", "spotify"], shell=True)\nprint("Opening Spotify")',
        'linux': 'subprocess.run(["spotify"])\nprint("Opening Spotify")',
        'darwin': 'subprocess.run(["open", "-a", "Spotify"])\nprint("Opening Spotify")'
    },
    
    'open_discord': {
        'windows': 'subprocess.run(["start", "discord"], shell=True)\nprint("Opening Discord")',
        'linux': 'subprocess.run(["discord"])\nprint("Opening Discord")',
        'darwin': 'subprocess.run(["open", "-a", "Discord"])\nprint("Opening Discord")'
    },
    
    # Close/Kill Application Commands
    'close_chrome': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], shell=True)\nprint("Closing Chrome")',
        'linux': 'subprocess.run(["pkill", "-f", "chrome"])\nprint("Closing Chrome")',
        'darwin': 'subprocess.run(["pkill", "-f", "Chrome"])\nprint("Closing Chrome")'
    },
    
    'close_vscode': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "Code.exe"], shell=True)\nprint("Closing VS Code")',
        'linux': 'subprocess.run(["pkill", "-f", "code"])\nprint("Closing VS Code")',
        'darwin': 'subprocess.run(["pkill", "-f", "Code"])\nprint("Closing VS Code")'
    },
    
    'close_notepad': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "notepad.exe"], shell=True)\nprint("Closing Notepad")',
        'linux': 'subprocess.run(["pkill", "-f", "gedit"])\nprint("Closing Text Editor")',
        'darwin': 'subprocess.run(["pkill", "-f", "TextEdit"])\nprint("Closing TextEdit")'
    },
    
    'close_spotify': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "Spotify.exe"], shell=True)\nprint("Closing Spotify")',
        'linux': 'subprocess.run(["pkill", "-f", "spotify"])\nprint("Closing Spotify")',
        'darwin': 'subprocess.run(["pkill", "-f", "Spotify"])\nprint("Closing Spotify")'
    },
    
    'close_discord': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "Discord.exe"], shell=True)\nprint("Closing Discord")',
        'linux': 'subprocess.run(["pkill", "-f", "discord"])\nprint("Closing Discord")',
        'darwin': 'subprocess.run(["pkill", "-f", "Discord"])\nprint("Closing Discord")'
    },
    
    'close_figma': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "Figma.exe"], shell=True)\nprint("Closing Figma")',
        'linux': 'subprocess.run(["pkill", "-f", "figma"])\nprint("Closing Figma")',
        'darwin': 'subprocess.run(["pkill", "-f", "Figma"])\nprint("Closing Figma")'
    },
    
    'close_calculator': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "Calculator.exe"], shell=True)\nprint("Closing Calculator")',
        'linux': 'subprocess.run(["pkill", "-f", "gnome-calculator"])\nprint("Closing Calculator")',
        'darwin': 'subprocess.run(["pkill", "-f", "Calculator"])\nprint("Closing Calculator")'
    },
    
    'close_file_explorer': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], shell=True)\nsubprocess.run(["start", "explorer"], shell=True)\nprint("Restarting File Explorer")',
        'linux': 'subprocess.run(["pkill", "-f", "nautilus"])\nprint("Closing File Manager")',
        'darwin': 'subprocess.run(["pkill", "-f", "Finder"])\nprint("Closing Finder")'
    },
    
    'close_app': {
        'windows': 'app_name = "{app_name}"\nsubprocess.run(["taskkill", "/f", "/im", f"{app_name}.exe"], shell=True)\nprint(f"Closing {app_name}")',
        'linux': 'app_name = "{app_name}"\nsubprocess.run(["pkill", "-f", app_name])\nprint(f"Closing {app_name}")',
        'darwin': 'app_name = "{app_name}"\nsubprocess.run(["pkill", "-f", app_name])\nprint(f"Closing {app_name}")'
    },
    
    'close_all_browsers': {
        'windows': 'subprocess.run(["taskkill", "/f", "/im", "chrome.exe"], shell=True)\nsubprocess.run(["taskkill", "/f", "/im", "msedge.exe"], shell=True)\nsubprocess.run(["taskkill", "/f", "/im", "firefox.exe"], shell=True)\nprint("Closing all browsers")',
        'linux': 'subprocess.run(["pkill", "-f", "chrome"])\nsubprocess.run(["pkill", "-f", "firefox"])\nprint("Closing all browsers")',
        'darwin': 'subprocess.run(["pkill", "-f", "Chrome"])\nsubprocess.run(["pkill", "-f", "Firefox"])\nsubprocess.run(["pkill", "-f", "Safari"])\nprint("Closing all browsers")'
    },
    
    # Web operations (5 commands)
    'open_youtube': {
        'all': 'webbrowser.open("https://youtube.com")\nprint("Opening YouTube")'
    },
    
    'open_github': {
        'all': 'webbrowser.open("https://github.com")\nprint("Opening GitHub")'
    },
    
    'open_gmail': {
        'all': 'webbrowser.open("https://gmail.com")\nprint("Opening Gmail")'
    },
    
    'search_youtube': {
        'all': 'query = "{query}"\nwebbrowser.open(f"https://www.youtube.com/results?search_query={query.replace(\' \', \'+\')}")\nprint(f"Searching YouTube for: {query}")'
    },
    
    'search_google': {
        'all': 'query = "{query}"\nwebbrowser.open(f"https://www.google.com/search?q={query.replace(\' \', \'+\')}")\nprint(f"Searching Google for: {query}")'
    },
    
    # File operations (4 commands)
    'take_screenshot': {
        'all': 'screenshot = pyautogui.screenshot()\nfilename = f"screenshot_{datetime.datetime.now().strftime(\'%Y%m%d_%H%M%S\')}.png"\nscreenshot.save(filename)\nprint(f"Screenshot saved as {filename}")'
    },
    
    'create_folder': {
        'all': 'folder_name = "{folder_name}"\nos.makedirs(folder_name, exist_ok=True)\nprint(f"Created folder: {folder_name}")'
    },
    
    'list_files': {
        'all': 'files = os.listdir(".")\nprint("Files in current directory:")\nfor f in files:\n    print(f"  {f}")'
    },
    
    'delete_file': {
        'all': 'filename = "{filename}"\nif os.path.exists(filename):\n    os.remove(filename)\n    print(f"Deleted file: {filename}")\nelse:\n    print(f"File not found: {filename}")'
    },
    
    # System operations (4 commands)
    'shutdown_system': {
        'windows': 'subprocess.run(["shutdown", "/s", "/t", "10"], shell=True)\nprint("System will shutdown in 10 seconds")',
        'linux': 'subprocess.run(["shutdown", "-h", "+1"])\nprint("System will shutdown in 1 minute")',
        'darwin': 'subprocess.run(["shutdown", "-h", "+1"])\nprint("System will shutdown in 1 minute")'
    },
    
    'restart_system': {
        'windows': 'subprocess.run(["shutdown", "/r", "/t", "10"], shell=True)\nprint("System will restart in 10 seconds")',
        'linux': 'subprocess.run(["shutdown", "-r", "+1"])\nprint("System will restart in 1 minute")',
        'darwin': 'subprocess.run(["shutdown", "-r", "+1"])\nprint("System will restart in 1 minute")'
    },
    
    'lock_screen': {
        'windows': 'subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"], shell=True)\nprint("Screen locked")',
        'linux': 'subprocess.run(["gnome-screensaver-command", "-l"])\nprint("Screen locked")',
        'darwin': 'subprocess.run(["/System/Library/CoreServices/Menu Extras/User.menu/Contents/Resources/CGSession", "-suspend"])\nprint("Screen locked")'
    },
    
    'get_system_info': {
        'all': 'print(f"Platform: {platform.system()}")\nprint(f"Release: {platform.release()}")\nprint(f"Machine: {platform.machine()}")\nprint(f"Processor: {platform.processor()}")'
    },
    
    # Automation operations (5 commands)
    'type_text': {
        'all': 'text = "{text}"\ntime.sleep(1)\npyautogui.write(text)\nprint(f"Typed: {text}")'
    },
    
    'press_keys': {
        'all': 'keys = "{keys}"\nif "+" in keys:\n    key_combo = keys.split("+")\n    pyautogui.hotkey(*key_combo)\n    print(f"Pressed: {keys}")\nelse:\n    pyautogui.press(keys)\n    print(f"Pressed: {keys}")'
    },
    
    'volume_up': {
        'all': 'pyautogui.press("volumeup")\nprint("Volume increased")'
    },
    
    'volume_down': {
        'all': 'pyautogui.press("volumedown")\nprint("Volume decreased")'
    },
    
    'mute_volume': {
        'all': 'pyautogui.press("volumemute")\nprint("Volume muted/unmuted")'
    },
    
    # Network operations (2 commands)
    'check_internet': {
        'all': 'try:\n    response = requests.get("https://www.google.com", timeout=5)\n    print("Internet connection: Active")\nexcept:\n    print("Internet connection: Not available")'
    },
    
    'get_ip_address': {
        'all': 'try:\n    response = requests.get("https://api.ipify.org", timeout=5)\n    print(f"Public IP: {response.text}")\nexcept:\n    print("Could not retrieve IP address")'
    },
    
    # Process operations (2 commands)
    'check_processes': {
        'all': 'try:\n    import psutil\n    processes = [p.info for p in psutil.process_iter([\'pid\', \'name\', \'cpu_percent\'])]\n    print("Top 10 processes:")\n    for p in sorted(processes, key=lambda x: x[\'cpu_percent\'], reverse=True)[:10]:\n        print(f"  {p[\'name\']} (PID: {p[\'pid\']}) - CPU: {p[\'cpu_percent\']}%")\nexcept ImportError:\n    print("psutil not available for process monitoring")'
    },
    
    'kill_process': {
        'windows': 'process_name = "{process_name}"\nsubprocess.run([f"taskkill", "/f", "/im", f"{process_name}.exe"], shell=True)\nprint(f"Attempted to kill process: {process_name}")',
        'linux': 'process_name = "{process_name}"\nsubprocess.run(["pkill", "-f", process_name])\nprint(f"Attempted to kill process: {process_name}")',
        'darwin': 'process_name = "{process_name}"\nsubprocess.run(["pkill", "-f", process_name])\nprint(f"Attempted to kill process: {process_name}")'
    },
    
    # NEW COMMANDS (10 additional commands)
    
    # Media Control Commands (3)
    'play_pause_media': {
        'all': 'pyautogui.press("playpause")\nprint("Play/Pause toggled")'
    },
    
    'next_track': {
        'all': 'pyautogui.press("nexttrack")\nprint("Skipped to next track")'
    },
    
    'previous_track': {
        'all': 'pyautogui.press("prevtrack")\nprint("Skipped to previous track")'
    },
    
    # Window Management Commands (3)
    'minimize_window': {
        'windows': 'pyautogui.hotkey("win", "down")\nprint("Window minimized")',
        'linux': 'pyautogui.hotkey("alt", "F9")\nprint("Window minimized")',
        'darwin': 'pyautogui.hotkey("cmd", "m")\nprint("Window minimized")'
    },
    
    'maximize_window': {
        'windows': 'pyautogui.hotkey("win", "up")\nprint("Window maximized")',
        'linux': 'pyautogui.hotkey("alt", "F10")\nprint("Window maximized")',
        'darwin': 'pyautogui.hotkey("cmd", "ctrl", "f")\nprint("Window maximized")'
    },
    
    'switch_window': {
        'windows': 'pyautogui.hotkey("alt", "tab")\nprint("Switched to next window")',
        'linux': 'pyautogui.hotkey("alt", "tab")\nprint("Switched to next window")',
        'darwin': 'pyautogui.hotkey("cmd", "tab")\nprint("Switched to next window")'
    },
    
    # Clipboard Commands (2)
    'copy_to_clipboard': {
        'windows': 'pyautogui.hotkey("ctrl", "c")\ntime.sleep(0.5)\nprint("Content copied to clipboard")',
        'linux': 'pyautogui.hotkey("ctrl", "c")\ntime.sleep(0.5)\nprint("Content copied to clipboard")',
        'darwin': 'pyautogui.hotkey("cmd", "c")\ntime.sleep(0.5)\nprint("Content copied to clipboard")'
    },
    
    'paste_from_clipboard': {
        'windows': 'pyautogui.hotkey("ctrl", "v")\ntime.sleep(0.5)\nprint("Content pasted from clipboard")',
        'linux': 'pyautogui.hotkey("ctrl", "v")\ntime.sleep(0.5)\nprint("Content pasted from clipboard")',
        'darwin': 'pyautogui.hotkey("cmd", "v")\ntime.sleep(0.5)\nprint("Content pasted from clipboard")'
    },
    
    # Mouse Control Commands (2)
    'mouse_click': {
        'all': 'x, y = {x}, {y}\npyautogui.click(x, y)\nprint(f"Clicked at position ({x}, {y})")'
    },
    
    'scroll_down': {
        'all': 'pyautogui.scroll(-3)\nprint("Scrolled down")'
    },
    
    'scroll_up': {
        'all': 'pyautogui.scroll(3)\nprint("Scrolled up")'
    },
    
    # System Monitoring Commands (2)
    'get_battery_status': {
        'all': 'try:\n    import psutil\n    battery = psutil.sensors_battery()\n    if battery:\n        print(f"Battery: {battery.percent}% - {"Charging" if battery.power_plugged else "Not Charging"}")\n    else:\n        print("No battery information available")\nexcept ImportError:\n    print("psutil not available for battery monitoring")'
    },
    
    'get_disk_usage': {
        'all': 'try:\n    import psutil\n    disk_usage = psutil.disk_usage("/")\n    total_gb = disk_usage.total / (1024**3)\n    used_gb = disk_usage.used / (1024**3)\n    free_gb = disk_usage.free / (1024**3)\n    usage_percent = (used_gb / total_gb) * 100\n    print(f"Disk Usage: {used_gb:.1f}GB / {total_gb:.1f}GB ({usage_percent:.1f}% used)")\n    print(f"Free Space: {free_gb:.1f}GB")\nexcept ImportError:\n    print("psutil not available for disk monitoring")'
    },
    
    # Text Editing Commands (2)
    'select_all': {
        'windows': 'pyautogui.hotkey("ctrl", "a")\nprint("Selected all text")',
        'linux': 'pyautogui.hotkey("ctrl", "a")\nprint("Selected all text")',
        'darwin': 'pyautogui.hotkey("cmd", "a")\nprint("Selected all text")'
    },
    
    'undo_action': {
        'windows': 'pyautogui.hotkey("ctrl", "z")\nprint("Undo performed")',
        'linux': 'pyautogui.hotkey("ctrl", "z")\nprint("Undo performed")',
        'darwin': 'pyautogui.hotkey("cmd", "z")\nprint("Undo performed")'
    },
    
    # Web Browser Commands (1)
    'refresh_page': {
        'windows': 'pyautogui.hotkey("ctrl", "r")\nprint("Page refreshed")',
        'linux': 'pyautogui.hotkey("ctrl", "r")\nprint("Page refreshed")',
        'darwin': 'pyautogui.hotkey("cmd", "r")\nprint("Page refreshed")'
    }
}

def convert_natural_command_to_pattern(natural_command):
    """Use Mistral AI to convert natural language to our predefined command patterns"""
    
    # Create a list of available commands for the AI
    available_commands = list(COMMAND_PATTERNS.keys())
    commands_description = {
        # Open commands
        'open_vscode': 'Opens Visual Studio Code editor',
        'open_chrome': 'Opens Google Chrome browser',
        'open_figma': 'Opens Figma design application',
        'open_app': 'Opens any application by name (requires app_name parameter)',
        'open_notepad': 'Opens text editor (Notepad/TextEdit/gedit)',
        'open_calculator': 'Opens calculator application',
        'open_file_explorer': 'Opens file manager (Explorer/Finder/Nautilus)',
        'open_terminal': 'Opens command line terminal',
        'open_spotify': 'Opens Spotify music application',
        'open_discord': 'Opens Discord chat application',
        'open_youtube': 'Opens YouTube website',
        'open_github': 'Opens GitHub website',
        'open_gmail': 'Opens Gmail website',
        
        # Close commands
        'close_chrome': 'Closes/kills Google Chrome browser',
        'close_vscode': 'Closes/kills Visual Studio Code',
        'close_notepad': 'Closes/kills Notepad/text editor',
        'close_spotify': 'Closes/kills Spotify',
        'close_discord': 'Closes/kills Discord',
        'close_figma': 'Closes/kills Figma',
        'close_calculator': 'Closes/kills Calculator',
        'close_file_explorer': 'Closes/restarts File Explorer',
        'close_app': 'Closes/kills any application by name (requires app_name parameter)',
        'close_all_browsers': 'Closes all web browsers (Chrome, Edge, Firefox)',
        
        # Other commands
        'search_youtube': 'Searches for content on YouTube (requires query parameter)',
        'search_google': 'Searches on Google (requires query parameter)',
        'take_screenshot': 'Takes a screenshot and saves it',
        'create_folder': 'Creates a new folder (requires folder_name parameter)',
        'list_files': 'Lists all files in current directory',
        'delete_file': 'Deletes a specific file (requires filename parameter)',
        'shutdown_system': 'Shuts down the computer',
        'restart_system': 'Restarts the computer',
        'lock_screen': 'Locks the screen/computer',
        'get_system_info': 'Gets system information',
        'type_text': 'Types specific text (requires text parameter)',
        'press_keys': 'Presses keyboard keys (requires keys parameter)',
        'volume_up': 'Increases system volume',
        'volume_down': 'Decreases system volume',
        'mute_volume': 'Mutes/unmutes system volume',
        'check_internet': 'Checks internet connectivity',
        'get_ip_address': 'Gets public IP address',
        'check_processes': 'Shows running processes',
        'kill_process': 'Kills a specific process (requires process_name parameter)',
        
        # New commands
        'play_pause_media': 'Plays or pauses current media',
        'next_track': 'Skips to next track/song',
        'previous_track': 'Goes to previous track/song',
        'minimize_window': 'Minimizes the current window',
        'maximize_window': 'Maximizes the current window',
        'switch_window': 'Switches to next open window',
        'copy_to_clipboard': 'Copies selected content to clipboard',
        'paste_from_clipboard': 'Pastes content from clipboard',
        'mouse_click': 'Clicks at specific coordinates (requires x, y parameters)',
        'scroll_down': 'Scrolls down on current page/window',
        'scroll_up': 'Scrolls up on current page/window',
        'get_battery_status': 'Shows battery level and charging status',
        'get_disk_usage': 'Shows disk space usage information',
        'select_all': 'Selects all text/content',
        'undo_action': 'Undoes the last action',
        'refresh_page': 'Refreshes current web page or window'
    }
    
    prompt = f"""
You are a command parser for a computer automation system. Your job is to convert natural language commands into predefined command patterns.

USER COMMAND: "{natural_command}"

AVAILABLE COMMANDS:
{chr(10).join([f"- {cmd}: {desc}" for cmd, desc in commands_description.items()])}

INSTRUCTIONS:
1. Analyze the user's natural language command
2. Find the best matching predefined command from the list above
3. Extract any parameters needed (like text to type, folder names, search queries, coordinates, etc.)
4. Return ONLY a JSON response in this exact format:

For commands without parameters:
{{"command": "command_name"}}

For commands with parameters:
{{"command": "command_name", "parameters": {{"param_name": "param_value"}}}}

EXAMPLES:
- "open vs code" → {{"command": "open_vscode"}}
- "take a screenshot" → {{"command": "take_screenshot"}}
- "search for python tutorials on youtube" → {{"command": "search_youtube", "parameters": {{"query": "python tutorials"}}}}
- "create a folder called projects" → {{"command": "create_folder", "parameters": {{"folder_name": "projects"}}}}
- "type hello world" → {{"command": "type_text", "parameters": {{"text": "hello world"}}}}
- "press ctrl+c" → {{"command": "press_keys", "parameters": {{"keys": "ctrl+c"}}}}
- "click at 100 200" → {{"command": "mouse_click", "parameters": {{"x": "100", "y": "200"}}}}
- "play music" → {{"command": "play_pause_media"}}
- "next song" → {{"command": "next_track"}}
- "minimize window" → {{"command": "minimize_window"}}
- "copy this" → {{"command": "copy_to_clipboard"}}
- "paste here" → {{"command": "paste_from_clipboard"}}
- "scroll down" → {{"command": "scroll_down"}}
- "battery status" → {{"command": "get_battery_status"}}
- "disk space" → {{"command": "get_disk_usage"}}
- "select all" → {{"command": "select_all"}}
- "undo" → {{"command": "undo_action"}}
- "refresh page" → {{"command": "refresh_page"}}
- "close chrome" → {{"command": "close_chrome"}}
- "close vscode" → {{"command": "close_vscode"}}
- "close spotify" → {{"command": "close_spotify"}}
- "close notepad" → {{"command": "close_notepad"}}
- "close figma" → {{"command": "close_figma"}}
- "close calculator" → {{"command": "close_calculator"}}
- "close discord" → {{"command": "close_discord"}}
- "close photoshop" → {{"command": "close_app", "parameters": {{"app_name": "photoshop"}}}}
- "kill chrome" → {{"command": "close_chrome"}}
- "exit spotify" → {{"command": "close_spotify"}}
- "close all browsers" → {{"command": "close_all_browsers"}}

Return ONLY the JSON, no explanations or additional text.
"""

    try:
        print(f" Sending to Ollama (local LLM): '{natural_command}'")
        
        # Call Ollama local API
        ollama_response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": f"You are a precise command parser. Return only valid JSON responses for command conversion.\n\n{prompt}",
                "stream": False
            },
            timeout=60
        )
        
        if ollama_response.status_code != 200:
            print(f" Ollama error: {ollama_response.status_code}")
            return None, None
        
        response_text = ollama_response.json().get("response", "").strip()
        print(f" Ollama raw response: '{response_text}'")
        
        # Clean up response to extract JSON
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text:
            response_text = response_text.split("```")[1].strip()
        
        print(f" Cleaned response: '{response_text}'")
        
        # Parse JSON response
        parsed_response = json.loads(response_text)
        print(f" Parsed JSON: {parsed_response}")
        
        command = parsed_response.get('command')
        parameters = parsed_response.get('parameters', {})
        
        print(f" Extracted command: '{command}', parameters: {parameters}")
        
        if command in COMMAND_PATTERNS:
            print(f" Command '{command}' found in patterns")
            return command, parameters
        else:
            print(f" Command '{command}' NOT found in patterns")
            print(f"Available commands: {list(COMMAND_PATTERNS.keys())}")
            return None, None
            
    except json.JSONDecodeError as e:
        print(f" JSON parsing error: {e}")
        print(f"Response that failed to parse: '{response_text}'")
        return None, None
    except Exception as e:
        print(f" Error in AI command conversion: {e}")
        return None, None

def generate_code_from_pattern(command_key, parameters, platform_name):
    """Generate code from predefined pattern with parameters"""
    if command_key not in COMMAND_PATTERNS:
        return None
    
    code_dict = COMMAND_PATTERNS[command_key]
    platform_key = platform_name.lower()
    
    # Get the appropriate code for the platform
    if 'all' in code_dict:
        code_template = code_dict['all']
    elif platform_key in code_dict:
        code_template = code_dict[platform_key]
    elif 'windows' in code_dict:  # Fallback to windows
        code_template = code_dict['windows']
    else:
        return None
    
    # Replace parameters in the template
    for param_name, param_value in parameters.items():
        code_template = code_template.replace(f"{{{param_name}}}", str(param_value))
    
    return code_template

# Add a fallback function for simple pattern matching (updated with new commands)
def simple_pattern_match(natural_command):
    """Fallback pattern matching without AI"""
    cmd_lower = natural_command.lower().strip()
    
    # Simple mappings (updated with new commands)
    simple_mappings = {
        # Open commands
        'open youtube': 'open_youtube',
        'youtube': 'open_youtube',
        'open chrome': 'open_chrome',
        'chrome': 'open_chrome',
        'open vs code': 'open_vscode',
        'open vscode': 'open_vscode',
        'vs code': 'open_vscode',
        'vscode': 'open_vscode',
        'open notepad': 'open_notepad',
        'notepad': 'open_notepad',
        'open calculator': 'open_calculator',
        'calculator': 'open_calculator',
        'calc': 'open_calculator',
        'open spotify': 'open_spotify',
        'spotify': 'open_spotify',
        'open discord': 'open_discord',
        'discord': 'open_discord',
        'open figma': 'open_figma',
        'figma': 'open_figma',
        'open gmail': 'open_gmail',
        'gmail': 'open_gmail',
        'open github': 'open_github',
        'github': 'open_github',
        
        # Close commands
        'close chrome': 'close_chrome',
        'kill chrome': 'close_chrome',
        'exit chrome': 'close_chrome',
        'close vscode': 'close_vscode',
        'close vs code': 'close_vscode',
        'kill vscode': 'close_vscode',
        'close notepad': 'close_notepad',
        'kill notepad': 'close_notepad',
        'close spotify': 'close_spotify',
        'kill spotify': 'close_spotify',
        'exit spotify': 'close_spotify',
        'close discord': 'close_discord',
        'kill discord': 'close_discord',
        'exit discord': 'close_discord',
        'close figma': 'close_figma',
        'kill figma': 'close_figma',
        'exit figma': 'close_figma',
        'close calculator': 'close_calculator',
        'kill calculator': 'close_calculator',
        'close all browsers': 'close_all_browsers',
        'kill all browsers': 'close_all_browsers',
        
        # Other commands
        'take screenshot': 'take_screenshot',
        'screenshot': 'take_screenshot',
        'volume up': 'volume_up',
        'volume down': 'volume_down',
        'mute': 'mute_volume',
        'shutdown': 'shutdown_system',
        'restart': 'restart_system',
        'lock screen': 'lock_screen',
        'system info': 'get_system_info',
        'check internet': 'check_internet',
        'get ip': 'get_ip_address',
        'list files': 'list_files',
        'check processes': 'check_processes',
        
        # Media commands
        'play': 'play_pause_media',
        'pause': 'play_pause_media',
        'play pause': 'play_pause_media',
        'next song': 'next_track',
        'next track': 'next_track',
        'previous song': 'previous_track',
        'previous track': 'previous_track',
        'minimize': 'minimize_window',
        'minimize window': 'minimize_window',
        'maximize': 'maximize_window',
        'maximize window': 'maximize_window',
        'switch window': 'switch_window',
        'alt tab': 'switch_window',
        'copy': 'copy_to_clipboard',
        'paste': 'paste_from_clipboard',
        'scroll down': 'scroll_down',
        'scroll up': 'scroll_up',
        'battery': 'get_battery_status',
        'battery status': 'get_battery_status',
        'disk space': 'get_disk_usage',
        'disk usage': 'get_disk_usage',
        'select all': 'select_all',
        'undo': 'undo_action',
        'refresh': 'refresh_page',
        'refresh page': 'refresh_page'
    }
    
    # Check for exact matches
    if cmd_lower in simple_mappings:
        return simple_mappings[cmd_lower], {}
    
    # Check for partial matches
    for pattern, command in simple_mappings.items():
        if pattern in cmd_lower:
            return command, {}
    
    # Check for generic close/kill app command
    if cmd_lower.startswith('close ') or cmd_lower.startswith('kill ') or cmd_lower.startswith('exit '):
        app_name = cmd_lower.replace('close ', '').replace('kill ', '').replace('exit ', '').strip()
        if app_name:
            return 'close_app', {'app_name': app_name}
    
    # Check for commands with parameters
    if 'search' in cmd_lower and 'youtube' in cmd_lower:
        query = cmd_lower.replace('search', '').replace('on youtube', '').replace('youtube', '').strip()
        if query:
            return 'search_youtube', {'query': query}
        else:
            return 'open_youtube', {}
    
    if 'search' in cmd_lower and ('google' in cmd_lower or 'search' == cmd_lower.split()[0]):
        query = cmd_lower.replace('search', '').replace('on google', '').replace('google', '').strip()
        if query:
            return 'search_google', {'query': query}
    
    if 'type' in cmd_lower:
        text = cmd_lower.replace('type', '').strip()
        if text:
            return 'type_text', {'text': text}
    
    if 'create folder' in cmd_lower or 'make folder' in cmd_lower:
        folder_name = cmd_lower.replace('create folder', '').replace('make folder', '').strip()
        if folder_name:
            return 'create_folder', {'folder_name': folder_name}
    
    # Check for mouse click with coordinates
    if 'click' in cmd_lower:
        # Try to extract coordinates
        import re
        coords = re.findall(r'\d+', cmd_lower)
        if len(coords) >= 2:
            return 'mouse_click', {'x': coords[0], 'y': coords[1]}
    
    return None, None

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    device_name = data.get('name')
    device_ip = data.get('ip')
    device_platform = data.get('platform', 'Unknown')
    
    if not device_name or not device_ip:
        return jsonify({"error": "Missing device name or IP"}), 400
    
    device_registry[device_name] = {
        "ip": device_ip,
        "platform": device_platform,
        "status": "online"
    }
    
    print(f"Device registered: {device_name} ({device_platform}) at {device_ip}")
    
    return jsonify({
        "status": "Registered successfully", 
        "device": device_name,
        "platform": device_platform,
        "devices": device_registry
    })

@app.route('/command', methods=['POST'])
def command():
    data = request.get_json()
    cmd = data.get('command', '')
    
    if not cmd:
        return jsonify({'error': 'No command provided'}), 400
    
    # Parse command to extract device name
    if ' on ' not in cmd.lower():
        return jsonify({'error': 'Command must include device name like "open youtube on a"'}), 400
    
    # Split command and device name
    parts = cmd.lower().rsplit(' on ', 1)
    if len(parts) != 2:
        return jsonify({'error': 'Invalid command format. Use: "command on device_name"'}), 400
    
    natural_cmd = parts[0].strip()
    device_name = parts[1].strip()
    
    if device_name not in device_registry:
        available_devices = list(device_registry.keys())
        return jsonify({
            'error': f'Device "{device_name}" not found',
            'available_devices': available_devices
        }), 404
    
    device_info = device_registry[device_name]
    target_ip = device_info["ip"]
    target_platform = device_info.get("platform", "Windows")
    
    try:
        print(f"Processing command: '{natural_cmd}' for device: {device_name} ({target_platform})")
        
        # First try AI conversion
        command_key, parameters = convert_natural_command_to_pattern(natural_cmd)
        
        # If AI fails, try simple pattern matching
        if not command_key:
            print(" AI failed, trying simple pattern matching...")
            command_key, parameters = simple_pattern_match(natural_cmd)
        
        if not command_key:
            return jsonify({
                'error': f'Could not understand command: "{natural_cmd}"',
                'suggestion': 'Try commands like: "open youtube", "take screenshot", "play music", "minimize window", etc.',
                'debug': {
                    'available_patterns': list(COMMAND_PATTERNS.keys())
                }
            }), 400
        
        # Generate code from predefined pattern
        generated_code = generate_code_from_pattern(command_key, parameters, target_platform)
        
        if not generated_code:
            return jsonify({'error': f'No code available for command "{command_key}" on platform "{target_platform}"'}), 400
        
        print(f" Matched command: {command_key}")
        print(f" Parameters: {parameters}")
        print(f" Generated code:\n{generated_code}")
        
        # Test device connectivity
        try:
            test_response = requests.get(f"http://{target_ip}:8080/status", timeout=5)
            if test_response.status_code != 200:
                return jsonify({'error': f'Device {device_name} is not responding'}), 503
        except requests.exceptions.RequestException:
            return jsonify({'error': f'Cannot connect to device {device_name} at {target_ip}'}), 503
        
        # Send code to device
        payload = {
            "command": natural_cmd,
            "exec": generated_code
        }
        
        response = requests.post(
            f"http://{target_ip}:8080/execute",
            json=payload,
            timeout=60
        )
        
        device_response = response.json()
        
        return jsonify({
            "success": True,
            "original_command": natural_cmd,
            "matched_command": command_key,
            "parameters": parameters,
            "device": device_name,
            "platform": target_platform,
            "generated_code": generated_code,
            "device_response": device_response
        })
        
    except Exception as e:
        print(f" Unexpected error: {str(e)}")
        return jsonify({'error': f'Unexpected error: {str(e)}'}), 500

@app.route('/devices', methods=['GET'])
def get_devices():
    """Get list of registered devices with their status"""
    device_status = {}
    
    for name, info in device_registry.items():
        ip = info["ip"]
        try:
            response = requests.get(f"http://{ip}:8080/status", timeout=3)
            if response.status_code == 200:
                status_data = response.json()
                device_status[name] = {
                    "ip": ip, 
                    "status": "online",
                    "platform": status_data.get("platform", info.get("platform", "Unknown"))
                }
            else:
                device_status[name] = {"ip": ip, "status": "error", "platform": info.get("platform", "Unknown")}
        except:
            device_status[name] = {"ip": ip, "status": "offline", "platform": info.get("platform", "Unknown")}
    
    return jsonify(device_status)

@app.route('/commands', methods=['GET'])
def list_commands():
    """List all available command patterns with descriptions"""
    commands_info = {
        'total_commands': len(COMMAND_PATTERNS),
        'categories': {
            'Applications (8)': [
                'open vscode / open vs code / launch visual studio code',
                'open chrome / launch chrome / start google chrome',
                'open notepad / open text editor',
                'open calculator / launch calc',
                'open file explorer / open finder / open files',
                'open terminal / open command prompt / launch cmd',
                'open spotify / launch spotify music',
                'open discord / launch discord chat'
            ],
            'Web Operations (5)': [
                'open youtube / go to youtube',
                'open github / visit github',
                'open gmail / check email',
                'search [query] on youtube',
                'search [query] on google / google [query]'
            ],
            'File Operations (4)': [
                'take screenshot / capture screen',
                'create folder [name] / make directory [name]',
                'list files / show files / what files are here',
                'delete file [name] / remove file [name]'
            ],
            'System Operations (4)': [
                'shutdown / shutdown computer / turn off pc',
                'restart / restart computer / reboot',
                'lock screen / lock computer',
                'get system info / show system information'
            ],
            'Automation (5)': [
                'type [text] / write [text]',
                'press [keys] / hit [keys] / keyboard [keys]',
                'volume up / increase volume / louder',
                'volume down / decrease volume / quieter',
                'mute / mute volume / silence'
            ],
            'Network (2)': [
                'check internet / test connection / ping internet',
                'get ip address / what is my ip / show ip'
            ],
            'Process Management (2)': [
                'check processes / show running programs / list processes',
                'kill process [name] / end process [name] / stop [name]'
            ],
            'Media Control (3) - NEW': [
                'play / pause / play pause / toggle music',
                'next song / next track / skip forward',
                'previous song / previous track / skip back'
            ],
            'Window Management (3) - NEW': [
                'minimize / minimize window',
                'maximize / maximize window / fullscreen',
                'switch window / alt tab / next window'
            ],
            'Clipboard Operations (2) - NEW': [
                'copy / copy to clipboard / ctrl+c',
                'paste / paste from clipboard / ctrl+v'
            ],
            'Mouse Control (3) - NEW': [
                'click at [x] [y] / mouse click at coordinates',
                'scroll down / page down',
                'scroll up / page up'
            ],
            'System Monitoring (2) - NEW': [
                'battery status / check battery / battery level',
                'disk usage / disk space / storage info'
            ],
            'Text Editing (2) - NEW': [
                'select all / ctrl+a',
                'undo / ctrl+z / undo last action'
            ],
            'Browser Control (1) - NEW': [
                'refresh / refresh page / reload / F5'
            ]
        },
        'usage_examples': [
            # Original examples
            'open vs code on computer1',
            'take screenshot on laptop',
            'search python tutorial on youtube on pc',
            'create folder projects on workstation',
            'type hello world on device1',
            'press ctrl+c on computer2',
            'volume up on speaker_device',
            'shutdown on old_laptop',
            'get system info on server1',
            'check internet on router_pc',
            
            # New command examples
            'play music on media_pc',
            'next song on spotify_device',
            'minimize window on laptop',
            'maximize chrome on desktop',
            'switch window on workstation',
            'copy this on computer1',
            'paste here on laptop',
            'click at 500 300 on gaming_pc',
            'scroll down on tablet',
            'battery status on laptop',
            'disk space on server',
            'select all on notepad_pc',
            'undo on editor_machine',
            'refresh page on browser_pc'
        ]
    }
    
    return jsonify(commands_info)

# Add a test endpoint to check AI connectivity
@app.route('/test-ai', methods=['POST'])
def test_ai():
    """Test the Mistral AI connection"""
    data = request.get_json()
    test_command = data.get('command', 'open youtube')
    
    try:
        command_key, parameters = convert_natural_command_to_pattern(test_command)
        return jsonify({
            'success': True,
            'test_command': test_command,
            'matched_command': command_key,
            'parameters': parameters,
            'ai_working': command_key is not None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'ai_working': False
        })

if __name__ == '__main__':
    print(" Starting Enhanced DCDPOS Central Parser with 10+ NEW Commands...")
    print(f" Total Commands Available: {len(COMMAND_PATTERNS)}")
    print(" Command list at: http://localhost:5000/commands")
    print(" Device status at: http://localhost:5000/devices")
    print(" Test AI at: http://localhost:5000/test-ai")
    print(" Using Mistral AI for natural language processing")
    print(" Fallback pattern matching enabled")
    print("\n NEW COMMANDS ADDED:")
    print("    Media Control: play/pause, next/previous track")
    print("    Window Management: minimize, maximize, switch windows")
    print("    Clipboard: copy, paste operations")
    print("    Mouse Control: click at coordinates, scroll up/down")
    print("    System Monitoring: battery status, disk usage")
    print("    Text Editing: select all, undo actions")
    print("    Browser Control: refresh page")
    print(" Ready for advanced automation with 30+ predefined patterns!")
    app.run(host='0.0.0.0', port=5000, debug=True)
