"""
JARVIS AI - Enhanced Intelligent Backend with Screen Vision
Features: Better app opening, folder access, screen vision, click commands
Run: pip install pyautogui pillow easyocr torch
Then: python jarvis_backend_enhanced.py
"""

import os
import sys
import webbrowser
import subprocess
import platform
import speech_recognition as sr
import pyttsx3
from urllib.parse import quote
import requests
import json
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import threading
import time
import google.generativeai as genai
import re
import pyautogui
from PIL import Image
import base64
from io import BytesIO

app = Flask(__name__)
CORS(app)

class JarvisAI:
    def __init__(self, use_voice=True):
        self.use_voice = use_voice
        self.is_listening = False
        
        if use_voice:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 0.9)
            
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
        
        self.os_type = platform.system()
        
        # Enable PyAutoGUI fail-safe
        pyautogui.FAILSAFE = True
        
        self.context = {
            'last_browser_tab': None,
            'last_app': None,
            'conversation_history': [],
            'screen_elements': []
        }
        
        # LLM Configuration
        self.llm_config = {
            'provider': 'gemini',
            'gemini_api_key': 'AIzaSyBoL9PJ22_qoJe8iaiY4aO5QcnDZkNO7dM',
            'gemini_model': 'models/gemini-2.5-flash'
        }
        
        # Configure Gemini
        if self.llm_config['gemini_api_key']:
            genai.configure(api_key=self.llm_config['gemini_api_key'])
        
        print("🤖 Jarvis AI initialized with ENHANCED VISION and INTELLIGENCE!")
        print("👁️ Screen vision enabled - I can see and click!")
    
    def speak(self, text):
        """Convert text to speech"""
        print(f"Jarvis: {text}")
        if self.use_voice:
            try:
                self.engine.say(text)
                self.engine.runAndWait()
            except:
                pass
        return text
    
    def capture_screen(self):
        """Capture current screen"""
        try:
            screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"Screen capture error: {e}")
            return None
    
    def image_to_base64(self, image):
        """Convert PIL image to base64"""
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode()
    
    def analyze_screen_with_vision(self, user_query):
        """Use Gemini Vision to analyze screen and find clickable elements"""
        try:
            screenshot = self.capture_screen()
            if not screenshot:
                return None
            
            # Use Gemini Vision model
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            prompt = f"""Analyze this screenshot and help with this user request: "{user_query}"

IMPORTANT: Provide your response as a JSON object with this structure:
{{
    "action": "CLICK" | "INFORMATION" | "NOT_FOUND",
    "target_description": "description of what to click",
    "approximate_position": {{"x": percentage_x, "y": percentage_y}},
    "confidence": "high" | "medium" | "low",
    "reasoning": "explanation of what you found",
    "response": "what to say to user"
}}

For click requests (e.g., "click 1st website", "click search button"):
- Identify the element's position
- Give x,y as percentages (0-100) of screen dimensions
- Describe what you're clicking

If analyzing screen content:
- Describe what you see
- List numbered items if relevant

Example for "click 1st website":
{{
    "action": "CLICK",
    "target_description": "First search result link",
    "approximate_position": {{"x": 30, "y": 35}},
    "confidence": "high",
    "reasoning": "Found first blue link in search results",
    "response": "Clicking the first website in the search results"
}}"""

            response = model.generate_content([prompt, screenshot])
            response_text = response.text.strip()
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return {
                "action": "INFORMATION",
                "response": response_text
            }
            
        except Exception as e:
            print(f"Vision analysis error: {e}")
            return None
    
    def click_screen_position(self, x_percent, y_percent):
        """Click at screen position given as percentages"""
        try:
            screen_width, screen_height = pyautogui.size()
            x = int(screen_width * x_percent / 100)
            y = int(screen_height * y_percent / 100)
            
            # Move to position smoothly
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(0.2)
            # Click
            pyautogui.click()
            print(f"✅ Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    def llm_interpret_command(self, user_command):
        """Enhanced LLM interpretation with better reasoning"""
        
        # Get installed apps list for context
        installed_apps = self.get_installed_apps()
        apps_context = ", ".join(installed_apps[:30]) if installed_apps else "None detected"
        
        system_prompt = f"""You are Jarvis, an intelligent AI assistant with screen vision capabilities.

CRITICAL: Respond ONLY with valid JSON. No markdown, no extra text.

Available actions:
1. OPEN_APP - Open an application
2. OPEN_FOLDER - Open a folder/directory
3. SEARCH_WEB - Google search
4. SEARCH_YOUTUBE - YouTube search
5. OPEN_WEBSITE - Open specific website
6. SCREEN_CLICK - Click something on screen
7. SCREEN_ANALYZE - Analyze what's on screen
8. CONVERSATION - General conversation
9. SYSTEM_COMMAND - Execute system command

Operating System: {self.os_type}
Detected Apps: {apps_context}

For OPEN_APP:
- Provide FULL app names and ALL possible executables
- Windows: chrome.exe, Code.exe, notepad.exe, explorer.exe
- Be exhaustive with executable hints

For OPEN_FOLDER:
- Common folders: Documents, Downloads, Desktop, Pictures, Music
- Can open specific paths

For SCREEN_CLICK/ANALYZE:
- These require screen vision
- Will trigger secondary analysis

JSON Format:
{{
    "action": "ACTION_TYPE",
    "target": "specific target",
    "reasoning": "your thinking process",
    "executable_hints": ["all", "possible", "executables", "paths"],
    "folder_paths": ["possible/folder/paths"],
    "response": "what to tell user"
}}

Examples:

User: "open chrome"
{{
    "action": "OPEN_APP",
    "target": "Google Chrome",
    "reasoning": "User wants Chrome browser",
    "executable_hints": ["chrome", "chrome.exe", "google-chrome", "Chrome.exe", "GoogleChromePortable.exe"],
    "folder_paths": [],
    "response": "Opening Google Chrome browser"
}}

User: "open downloads folder"
{{
    "action": "OPEN_FOLDER",
    "target": "Downloads",
    "reasoning": "User wants to access Downloads folder",
    "executable_hints": [],
    "folder_paths": ["~/Downloads", "%USERPROFILE%\\Downloads", "C:\\Users\\%USERNAME%\\Downloads"],
    "response": "Opening Downloads folder"
}}

User: "open vs code"
{{
    "action": "OPEN_APP",
    "target": "Visual Studio Code",
    "reasoning": "VS Code is a popular code editor",
    "executable_hints": ["code", "code.exe", "Code.exe", "vscode", "code-insiders"],
    "folder_paths": [],
    "response": "Launching Visual Studio Code"
}}

User: "click the first link"
{{
    "action": "SCREEN_CLICK",
    "target": "first link on screen",
    "reasoning": "User wants to click first visible link",
    "executable_hints": [],
    "folder_paths": [],
    "response": "Let me click the first link for you"
}}

User: "what's on my screen"
{{
    "action": "SCREEN_ANALYZE",
    "target": "",
    "reasoning": "User wants screen content description",
    "executable_hints": [],
    "folder_paths": [],
    "response": "Let me analyze your screen"
}}

User: "open documents"
{{
    "action": "OPEN_FOLDER",
    "target": "Documents",
    "reasoning": "User wants Documents folder",
    "executable_hints": [],
    "folder_paths": ["~/Documents", "%USERPROFILE%\\Documents", "C:\\Users\\%USERNAME%\\Documents"],
    "response": "Opening your Documents folder"
}}

Now interpret: {user_command}"""

        try:
            model = genai.GenerativeModel(self.llm_config['gemini_model'])
            response = model.generate_content(system_prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            response_text = re.sub(r'```json\s*|\s*```', '', response_text)
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return {
                "action": "CONVERSATION",
                "target": "",
                "reasoning": "Could not parse command",
                "executable_hints": [],
                "folder_paths": [],
                "response": response_text
            }
                
        except Exception as e:
            print(f"LLM Error: {e}")
            return None
    
    def get_installed_apps(self):
        """Enhanced app detection"""
        apps = set()
        try:
            if self.os_type == "Windows":
                # Check multiple locations
                paths = [
                    os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                    os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
                    os.path.join(os.environ.get('APPDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
                ]
                
                for path in paths:
                    if os.path.exists(path):
                        try:
                            for item in os.listdir(path):
                                apps.add(item.replace('.lnk', '').replace('.exe', ''))
                        except:
                            continue
                            
        except Exception as e:
            print(f"App detection error: {e}")
        
        return list(apps)
    
    def open_folder(self, folder_name, folder_paths):
        """Open folder with enhanced path detection"""
        print(f"📁 Opening folder: {folder_name}")
        
        if self.os_type == "Windows":
            # Common Windows folders
            user_profile = os.environ.get('USERPROFILE', '')
            common_folders = {
                'downloads': os.path.join(user_profile, 'Downloads'),
                'documents': os.path.join(user_profile, 'Documents'),
                'desktop': os.path.join(user_profile, 'Desktop'),
                'pictures': os.path.join(user_profile, 'Pictures'),
                'music': os.path.join(user_profile, 'Music'),
                'videos': os.path.join(user_profile, 'Videos'),
            }
            
            folder_lower = folder_name.lower()
            
            # Try common folders first
            if folder_lower in common_folders:
                path = common_folders[folder_lower]
                if os.path.exists(path):
                    os.startfile(path)
                    print(f"✅ Opened: {path}")
                    return True
            
            # Try provided paths
            for path_template in folder_paths:
                path = os.path.expandvars(path_template)
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    os.startfile(path)
                    print(f"✅ Opened: {path}")
                    return True
            
            # Try direct path
            if os.path.exists(folder_name):
                os.startfile(folder_name)
                return True
                
        elif self.os_type == "Darwin":  # macOS
            folder_paths_mac = [
                os.path.expanduser(f"~/{folder_name}"),
                f"/Users/{os.getenv('USER')}/{folder_name}"
            ]
            for path in folder_paths_mac:
                if os.path.exists(path):
                    subprocess.run(['open', path])
                    return True
                    
        elif self.os_type == "Linux":
            folder_paths_linux = [
                os.path.expanduser(f"~/{folder_name}"),
                f"/home/{os.getenv('USER')}/{folder_name}"
            ]
            for path in folder_paths_linux:
                if os.path.exists(path):
                    subprocess.run(['xdg-open', path])
                    return True
        
        return False
    
    def smart_find_and_open_app(self, app_name, executable_hints):
        """Enhanced app opening with better search"""
        print(f"🔍 Searching for: {app_name}")
        print(f"💡 Hints: {executable_hints}")
        
        if self.os_type == "Windows":
            # Try direct execution first
            for hint in executable_hints:
                try:
                    # Try as direct command
                    subprocess.Popen(hint, shell=True)
                    time.sleep(1)
                    print(f"✅ Opened via command: {hint}")
                    return True
                except:
                    pass
            
            # Try with 'start' command
            for hint in executable_hints:
                try:
                    os.system(f'start "" "{hint}"')
                    time.sleep(1)
                    print(f"✅ Opened via start: {hint}")
                    return True
                except:
                    pass
            
            # Deep search in Program Files
            search_paths = [
                os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
            ]
            
            search_terms = [app_name.lower()] + [h.lower().replace('.exe', '') for h in executable_hints]
            
            for base_path in search_paths:
                if not os.path.exists(base_path):
                    continue
                
                try:
                    for root, dirs, files in os.walk(base_path):
                        depth = root[len(base_path):].count(os.sep)
                        if depth > 4:  # Increased depth
                            continue
                        
                        for file in files:
                            if file.endswith('.exe'):
                                file_lower = file.lower()
                                for term in search_terms:
                                    if term in file_lower or file_lower in term:
                                        exe_path = os.path.join(root, file)
                                        try:
                                            os.startfile(exe_path)
                                            print(f"✅ Found and opened: {exe_path}")
                                            return True
                                        except:
                                            pass
                except:
                    continue
            
            # Try PowerShell Get-Command
            try:
                for hint in executable_hints[:3]:
                    cmd = f'powershell -Command "Start-Process {hint}"'
                    subprocess.run(cmd, shell=True, capture_output=True)
                    time.sleep(1)
                    print(f"✅ Opened via PowerShell: {hint}")
                    return True
            except:
                pass
                    
        elif self.os_type == "Darwin":  # macOS
            for hint in [app_name] + executable_hints:
                try:
                    subprocess.run(['open', '-a', hint], check=True)
                    return True
                except:
                    continue
                    
        elif self.os_type == "Linux":
            for hint in [app_name] + executable_hints:
                try:
                    subprocess.Popen([hint])
                    return True
                except:
                    continue
        
        return False
    
    def search_web(self, query):
        """Search the web"""
        search_url = f"https://www.google.com/search?q={quote(query)}"
        webbrowser.open(search_url)
        self.context['last_browser_tab'] = 'search'
    
    def youtube_search(self, query):
        """Search YouTube"""
        search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
        webbrowser.open(search_url)
        self.context['last_browser_tab'] = 'youtube'
    
    def open_website(self, site_name):
        """Open specific websites"""
        websites = {
            'youtube': 'https://www.youtube.com',
            'gmail': 'https://mail.google.com',
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://www.twitter.com',
            'instagram': 'https://www.instagram.com',
            'reddit': 'https://www.reddit.com',
            'github': 'https://www.github.com',
        }
        
        url = websites.get(site_name.lower(), f"https://www.{site_name}.com")
        webbrowser.open(url)
        self.context['last_browser_tab'] = site_name
        return url
    
    def process_command(self, command):
        """Enhanced command processing with vision support"""
        if not command:
            return {'success': False, 'response': 'No command received'}
        
        command_lower = command.lower()
        
        # Quick exit
        if any(word in command_lower for word in ['exit', 'quit', 'goodbye']):
            response = self.speak("Goodbye! Shutting down.")
            return {'success': True, 'response': response, 'action': 'exit'}
        
        # AI interpretation
        print("🧠 Analyzing command with enhanced AI...")
        interpretation = self.llm_interpret_command(command)
        
        if not interpretation:
            response = self.speak("I'm having trouble understanding that command.")
            return {'success': False, 'response': response}
        
        print(f"💭 AI Reasoning: {interpretation.get('reasoning', 'N/A')}")
        
        action = interpretation.get('action', 'CONVERSATION')
        target = interpretation.get('target', '')
        ai_response = interpretation.get('response', '')
        executable_hints = interpretation.get('executable_hints', [])
        folder_paths = interpretation.get('folder_paths', [])
        
        # Execute based on action
        if action == "OPEN_APP":
            success = self.smart_find_and_open_app(target, executable_hints)
            if success:
                response = self.speak(ai_response)
                return {'success': True, 'response': response, 'action': 'open_app'}
            else:
                response = self.speak(f"I couldn't find {target}. Please ensure it's installed.")
                return {'success': False, 'response': response}
        
        elif action == "OPEN_FOLDER":
            success = self.open_folder(target, folder_paths)
            if success:
                response = self.speak(ai_response)
                return {'success': True, 'response': response, 'action': 'open_folder'}
            else:
                response = self.speak(f"I couldn't find the {target} folder.")
                return {'success': False, 'response': response}
        
        elif action == "SCREEN_CLICK":
            self.speak("Let me analyze your screen...")
            vision_result = self.analyze_screen_with_vision(command)
            
            if vision_result and vision_result.get('action') == 'CLICK':
                pos = vision_result.get('approximate_position', {})
                if pos:
                    success = self.click_screen_position(pos['x'], pos['y'])
                    if success:
                        response = self.speak(vision_result.get('response', 'Clicked'))
                        return {'success': True, 'response': response, 'action': 'click'}
            
            response = self.speak("I couldn't identify what to click on the screen.")
            return {'success': False, 'response': response}
        
        elif action == "SCREEN_ANALYZE":
            self.speak("Analyzing your screen...")
            vision_result = self.analyze_screen_with_vision(command)
            
            if vision_result:
                response = self.speak(vision_result.get('response', 'Screen analyzed'))
                return {'success': True, 'response': response, 'action': 'analyze'}
            else:
                response = self.speak("I couldn't analyze the screen.")
                return {'success': False, 'response': response}
        
        elif action == "SEARCH_WEB":
            self.search_web(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'search'}
        
        elif action == "SEARCH_YOUTUBE":
            self.youtube_search(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'youtube'}
        
        elif action == "OPEN_WEBSITE":
            self.open_website(target)
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'website'}
        
        elif action == "CONVERSATION":
            response = self.speak(ai_response)
            return {'success': True, 'response': response, 'action': 'conversation'}
        
        elif action == "SYSTEM_COMMAND":
            try:
                if self.os_type == "Windows":
                    os.system(target)
                else:
                    subprocess.run(target, shell=True)
                response = self.speak(ai_response)
                return {'success': True, 'response': response, 'action': 'system'}
            except Exception as e:
                response = self.speak(f"Error executing command: {str(e)}")
                return {'success': False, 'response': response}
        
        else:
            response = self.speak("I'm not sure how to handle that.")
            return {'success': False, 'response': response}

# Initialize Jarvis
jarvis = JarvisAI(use_voice=False)

# API Routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/command', methods=['POST'])
def handle_command():
    data = request.json
    command = data.get('command', '')
    result = jarvis.process_command(command)
    return jsonify(result)

@app.route('/api/screen', methods=['GET'])
def get_screen():
    """Get current screen analysis"""
    screenshot = jarvis.capture_screen()
    if screenshot:
        img_base64 = jarvis.image_to_base64(screenshot)
        return jsonify({'success': True, 'image': img_base64})
    return jsonify({'success': False})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'context': jarvis.context,
        'llm_provider': jarvis.llm_config['provider'],
        'vision_enabled': True
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🤖 JARVIS AI - ENHANCED INTELLIGENT Backend with VISION")
    print("="*70)
    print("\n✅ All systems online!")
    print("\n🧠 ENHANCED FEATURES:")
    print("   ✓ Better AI reasoning for app detection")
    print("   ✓ Folder opening support")
    print("   ✓ Screen vision with Gemini")
    print("   ✓ Click commands (e.g., 'click 1st website')")
    print("   ✓ Screen analysis ('what's on my screen')")
    print("\n💡 Examples:")
    print("   'open chrome'           → Opens Google Chrome")
    print("   'open downloads folder' → Opens Downloads")
    print("   'click first link'      → Uses vision to click")
    print("   'what's on my screen'   → Describes screen content")
    print("   'open vs code'          → Opens Visual Studio Code")
    print("\n🌐 Server running at: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)
