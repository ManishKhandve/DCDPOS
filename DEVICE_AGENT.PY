
from flask import Flask, request, jsonify
import socket
import requests
import sys
import traceback
import os
import subprocess
import platform
from datetime import datetime

DEVICE_NAME = "a"  # Change this for each device (a, b, c, etc.) CUSTOME NAME
CENTRAL_SERVER_IP = "127.0.0.1"  # Change to your main PC IP CENTRAL PRASER IP

app = Flask(__name__)

def create_full_environment():
    """Create a full execution environment with all system capabilities"""
    # Import all commonly needed modules
    env = {
        '__builtins__': __builtins__,
        'os': os,
        'sys': sys,
        'subprocess': subprocess,
        'platform': platform,
        'print': print,
        'len': len,
        'str': str,
        'int': int,
        'float': float,
        'range': range,
        'list': list,
        'dict': dict,
        'True': True,
        'False': False,
        'None': None,
    }
   
    # Add commonly used modules
    modules_to_add = [
        'webbrowser', 'pyautogui', 'time', 'requests', 'json',
        'shutil', 'glob', 're', 'datetime', 'random', 'urllib',
        'pathlib', 'threading', 'psutil'
    ]
   
    for module_name in modules_to_add:
        try:
            module = __import__(module_name)
            env[module_name] = module
        except ImportError:
            pass  # Module not available, skip it
   
    # Configure pyautogui if available
    if 'pyautogui' in env:
        try:
            env['pyautogui'].FAILSAFE = False  # Disable failsafe for full control
            env['pyautogui'].PAUSE = 0.1
        except:
            pass
   
    return env

@app.route('/execute', methods=['POST'])
def execute():
    data = request.get_json()
    exec_code = data.get('exec', '')
    command = data.get('command', 'Unknown command')
   
    if not exec_code:
        return jsonify({"error": "No executable code received"})
   
    try:
        # Create full execution environment with all capabilities
        full_env = create_full_environment()
       
        # Log what we're about to execute
        print(f"[{DEVICE_NAME}] Executing: {command}")
        print(f"[{DEVICE_NAME}] Generated code:\n{exec_code}")
       
        # Execute the code with full system access
        exec(exec_code, full_env)
       
        log_execution(command, exec_code, "SUCCESS", "Executed successfully")
        return jsonify({
            "status": "Command executed successfully",
            "device": DEVICE_NAME,
            "command": command
        })
       
    except Exception as e:
        error_msg = f"Execution failed: {str(e)}"
        error_traceback = traceback.format_exc()
       
        print(f"[{DEVICE_NAME}] Error: {error_msg}")
        print(f"[{DEVICE_NAME}] Traceback:\n{error_traceback}")
       
        log_execution(command, exec_code, "ERROR", f"{error_msg}\n{error_traceback}")
        return jsonify({
            "error": error_msg,
            "device": DEVICE_NAME,
            "traceback": error_traceback
        })

def log_execution(command: str, code: str, status: str, details: str = ""):
    """Log executed commands with timestamp and status"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"""
{'='*50}
TIMESTAMP: {timestamp}
DEVICE: {DEVICE_NAME}
COMMAND: {command}
STATUS: {status}
CODE:
{code}
DETAILS: {details}
{'='*50}

"""
   
    try:
        with open(f"{DEVICE_NAME}_execution_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Failed to write log: {e}")

@app.route('/status', methods=['GET'])
def status():
    """Health check endpoint"""
    return jsonify({
        "device": DEVICE_NAME,
        "status": "online",
        "platform": platform.system(),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/test', methods=['POST'])
def test():
    """Test endpoint to verify device capabilities"""
    capabilities = {}
   
    # Test pyautogui
    try:
        import pyautogui
        screen_size = pyautogui.size()
        capabilities["pyautogui"] = {"available": True, "screen_size": screen_size}
    except Exception as e:
        capabilities["pyautogui"] = {"available": False, "error": str(e)}
   
    # Test subprocess
    try:
        result = subprocess.run(['echo', 'test'], capture_output=True, text=True, timeout=5)
        capabilities["subprocess"] = {"available": True, "test_output": result.stdout.strip()}
    except Exception as e:
        capabilities["subprocess"] = {"available": False, "error": str(e)}
   
    # Test file system access
    try:
        current_dir = os.getcwd()
        file_count = len(os.listdir(current_dir))
        capabilities["filesystem"] = {"available": True, "current_dir": current_dir, "files_in_dir": file_count}
    except Exception as e:
        capabilities["filesystem"] = {"available": False, "error": str(e)}
   
    return jsonify({
        "device": DEVICE_NAME,
        "platform": platform.system(),
        "capabilities": capabilities
    })

@app.route('/run_command', methods=['POST'])
def run_command():
    """Direct system command execution endpoint"""
    data = request.get_json()
    command = data.get('command', '')
   
    if not command:
        return jsonify({"error": "No command provided"})
   
    try:
        # Execute system command directly
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
       
        return jsonify({
            "device": DEVICE_NAME,
            "command": command,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "success": result.returncode == 0
        })
       
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Command timed out"})
    except Exception as e:
        return jsonify({"error": str(e)})

def register_with_central():
    """Register this device with the central server"""
    try:
        # Get local IP
        ip = socket.gethostbyname(socket.gethostname())
       
        # Register with central server
        response = requests.post(
            f"http://{CENTRAL_SERVER_IP}:5000/register",
            json={"name": DEVICE_NAME, "ip": ip, "platform": platform.system()},
            timeout=5
        )
       
        if response.status_code == 200:
            print(f"[{DEVICE_NAME}] Successfully registered with central parser at {ip}")
        else:
            print(f"[{DEVICE_NAME}] Registration failed: {response.status_code}")
           
    except Exception as e:
        print(f"[{DEVICE_NAME}] Failed to register with central server: {e}")

if __name__ == '__main__':
    print(f"[{DEVICE_NAME}] Starting DCDPOS Device Agent with FULL OS ACCESS...")
    print(f"[{DEVICE_NAME}] Platform: {platform.system()}")
    print(f"[{DEVICE_NAME}] WARNING: This agent has unrestricted system access!")
   
    # Register with central server
    register_with_central()
   
    # Start the Flask app
    print(f"[{DEVICE_NAME}] Device agent running on port 8080")
    app.run(host='0.0.0.0', port=8080, debug=False)
