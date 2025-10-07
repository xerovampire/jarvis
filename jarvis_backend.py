"""
JARVIS AI - Complete System Control with Vision
Features: Scroll, Type, Search Files, Full System Control
Run: pip install pyautogui pillow
Then: python jarvis_backend_complete.py
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
from pathlib import Path
import glob

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
        pyautogui.PAUSE = 0.5  # Small pause between actions
        
        self.context = {
            'last_browser_tab': None,
            'last_app': None,
            'conversation_history': [],
            'screen_elements': [],
            'last_search_results': []
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
        
        # Common search locations
        self.search_locations = self.get_search_locations()
        
        print("🤖 Jarvis AI initialized with COMPLETE SYSTEM CONTROL!")
        print("👁️ Vision | ⌨️ Typing | 🔍 File Search | 🖱️ Mouse Control")
    
    def get_search_locations(self):
        """Get common file search locations"""
        locations = []
        if self.os_type == "Windows":
            user_profile = os.environ.get('USERPROFILE', '')
            locations = [
                os.path.join(user_profile, 'Desktop'),
                os.path.join(user_profile, 'Documents'),
                os.path.join(user_profile, 'Downloads'),
                os.path.join(user_profile, 'Pictures'),
                os.path.join(user_profile, 'Videos'),
                os.path.join(user_profile, 'Music'),
                'C:\\Program Files',
                'C:\\Program Files (x86)',
            ]
        elif self.os_type == "Darwin":  # macOS
            home = os.path.expanduser('~')
            locations = [
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
                '/Applications',
            ]
        else:  # Linux
            home = os.path.expanduser('~')
            locations = [
                os.path.join(home, 'Desktop'),
                os.path.join(home, 'Documents'),
                os.path.join(home, 'Downloads'),
                os.path.join(home, 'Pictures'),
            ]
        
        return [loc for loc in locations if os.path.exists(loc)]
    
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
    
    def scroll_action(self, direction, amount=3):
        """Scroll up or down"""
        try:
            if direction.lower() in ['up', 'top']:
                pyautogui.scroll(amount * 100)  # Positive = up
                print(f"✅ Scrolled up")
            elif direction.lower() in ['down', 'bottom']:
                pyautogui.scroll(-amount * 100)  # Negative = down
                print(f"✅ Scrolled down")
            return True
        except Exception as e:
            print(f"Scroll error: {e}")
            return False
    
    def type_text(self, text, interval=0.05):
        """Type text on keyboard"""
        try:
            pyautogui.write(text, interval=interval)
            print(f"✅ Typed: {text}")
            return True
        except Exception as e:
            print(f"Typing error: {e}")
            return False
    
    def press_key(self, key):
        """Press a specific key or key combination"""
        try:
            # Handle key combinations like 'ctrl+c', 'alt+tab'
            if '+' in key:
                keys = key.split('+')
                pyautogui.hotkey(*keys)
                print(f"✅ Pressed: {key}")
            else:
                pyautogui.press(key)
                print(f"✅ Pressed: {key}")
            return True
        except Exception as e:
            print(f"Key press error: {e}")
            return False
    
    def search_files(self, query, file_type=None, max_results=20):
        """Search for files in system"""
        results = []
        search_pattern = f"*{query}*"
        
        print(f"🔍 Searching for: {query}")
        
        try:
            for location in self.search_locations:
                if not os.path.exists(location):
                    continue
                
                # Search with glob
                if file_type:
                    pattern = os.path.join(location, '**', f"*{query}*.{file_type}")
                else:
                    pattern = os.path.join(location, '**', f"*{query}*")
                
                try:
                    matches = glob.glob(pattern, recursive=True)
                    for match in matches[:max_results]:
                        if os.path.isfile(match):
                            results.append({
                                'path': match,
                                'name': os.path.basename(match),
                                'size': os.path.getsize(match),
                                'type': 'file'
                            })
                        elif os.path.isdir(match):
                            results.append({
                                'path': match,
                                'name': os.path.basename(match),
                                'type': 'folder'
                            })
                        
                        if len(results) >= max_results:
                            break
                except Exception as e:
                    continue
                
                if len(results) >= max_results:
                    break
            
            self.context['last_search_results'] = results
            print(f"✅ Found {len(results)} results")
            return results
            
        except Exception as e:
            print(f"File search error: {e}")
            return []
    
    def open_file(self, file_path):
        """Open a file with default application"""
        try:
            if self.os_type == "Windows":
                os.startfile(file_path)
            elif self.os_type == "Darwin":
                subprocess.run(['open', file_path])
            else:  # Linux
                subprocess.run(['xdg-open', file_path])
            print(f"✅ Opened: {file_path}")
            return True
        except Exception as e:
            print(f"Open file error: {e}")
            return False
    
    def analyze_screen_with_vision(self, user_query):
        """Use Gemini Vision to analyze screen"""
        try:
            screenshot = self.capture_screen()
            if not screenshot:
                return None
            
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            
            prompt = f"""Analyze this screenshot and help with: "{user_query}"

Respond with JSON ONLY:
{{
    "action": "CLICK" | "INFORMATION" | "NOT_FOUND",
    "target_description": "what to interact with",
    "approximate_position": {{"x": percent_x, "y": percent_y}},
    "confidence": "high" | "medium" | "low",
    "reasoning": "what you found",
    "response": "user message"
}}

For clicks: provide x,y as percentages (0-100) of screen size.
For information: describe what you see."""

            response = model.generate_content([prompt, screenshot])
            response_text = response.text.strip()
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return {"action": "INFORMATION", "response": response_text}
            
        except Exception as e:
            print(f"Vision analysis error: {e}")
            return None
    
    def click_screen_position(self, x_percent, y_percent):
        """Click at screen position given as percentages"""
        try:
            screen_width, screen_height = pyautogui.size()
            x = int(screen_width * x_percent / 100)
            y = int(screen_height * y_percent / 100)
            
            pyautogui.moveTo(x, y, duration=0.5)
            time.sleep(0.2)
            pyautogui.click()
            print(f"✅ Clicked at ({x}, {y})")
            return True
        except Exception as e:
            print(f"Click error: {e}")
            return False
    
    def llm_interpret_command(self, user_command):
        """Enhanced LLM interpretation with all system controls"""
        
        installed_apps = self.get_installed_apps()
        apps_context = ", ".join(installed_apps[:30]) if installed_apps else "None"
        
        system_prompt = f"""You are Jarvis with COMPLETE system control capabilities.

CRITICAL: Respond with VALID JSON only. No markdown, no extra text.

Available Actions:
1. OPEN_APP - Open application
2. OPEN_FOLDER - Open folder
3. SEARCH_WEB - Google search
4. SEARCH_YOUTUBE - YouTube search
5. OPEN_WEBSITE - Open website
6. SCREEN_CLICK - Click on screen
7. SCREEN_ANALYZE - Analyze screen
8. TYPE_TEXT - Type text
9. PRESS_KEY - Press key/combination
10. SCROLL - Scroll up/down
11. SEARCH_FILES - Search files in system
12. OPEN_FILE - Open specific file
13. CONVERSATION - General chat
14. SYSTEM_COMMAND - Execute command

System: {self.os_type}
Apps: {apps_context}

JSON Format:
{{
    "action": "ACTION_TYPE",
    "target": "target/query",
    "reasoning": "why this action",
    "executable_hints": ["possible", "executables"],
    "folder_paths": ["possible/paths"],
    "params": {{"direction": "up/down", "amount": 3, "key": "enter"}},
    "response": "user message"
}}

Examples:

"scroll down"
{{
    "action": "SCROLL",
    "target": "down",
    "reasoning": "User wants to scroll down",
    "executable_hints": [],
    "folder_paths": [],
    "params": {{"direction": "down", "amount": 3}},
    "response": "Scrolling down"
}}

"type hello world"
{{
    "action": "TYPE_TEXT",
    "target": "hello world",
    "reasoning": "User wants to type text",
    "executable_hints": [],
    "folder_paths": [],
    "params": {{}},
    "response": "Typing 'hello world'"
}}

"press enter"
{{
    "action": "PRESS_KEY",
    "target": "enter",
    "reasoning": "User wants to press Enter key",
    "executable_hints": [],
    "folder_paths": [],
    "params": {{"key": "enter"}},
    "response": "Pressing Enter"
}}

"search for python files"
{{
    "action": "SEARCH_FILES",
    "target": "python",
    "reasoning": "Search for files with 'python' in name",
    "executable_hints": [],
    "folder_paths": [],
    "params": {{"file_type": "py"}},
    "response": "Searching for Python files"
}}

"find my resume"
{{
    "action": "SEARCH_FILES",
    "target": "resume",
    "reasoning": "Search for resume file",
    "executable_hints": [],
    "folder_paths": [],
    "params": {{}},
    "response": "Searching for resume files"
}}

"open chrome"
{{
    "action": "OPEN_APP",
    "target": "Google Chrome",
    "reasoning": "Open Chrome browser",
    "executable_hints": ["chrome", "chrome.exe", "Chrome.exe"],
    "folder_paths": [],
    "params": {{}},
    "response": "Opening Google Chrome"
}}

"press ctrl+c"
{{
    "action": "PRESS_KEY",
    "target": "ctrl+c",
    "reasoning": "Copy selected content",
    "executable_hints": [],
    "folder_paths": [],
    "params": {{"key": "ctrl+c"}},
    "response": "Copying"
}}

"click first result"
{{
    "action": "SCREEN_CLICK",
    "target": "first result",
    "reasoning": "Click first search result",
    "executable_hints": [],
    "folder_paths": [],
    "params": {{}},
    "response": "Let me click the first result"
}}

Now interpret: {user_command}"""

        try:
            model = genai.GenerativeModel(self.llm_config['gemini_model'])
            response = model.generate_content(system_prompt)
            response_text = response.text.strip()
            
            # Remove markdown
            response_text = re.sub(r'```json\s*|\s*```', '', response_text)
            
            # Extract JSON
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            
            return {
                "action": "CONVERSATION",
                "target": "",
                "reasoning": "Parse error",
                "executable_hints": [],
                "folder_paths": [],
                "params": {},
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
            
            if folder_lower in common_folders:
                path = common_folders[folder_lower]
                if os.path.exists(path):
                    os.startfile(path)
                    return True
            
            for path_template in folder_paths:
                path = os.path.expandvars(path_template)
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    os.startfile(path)
                    return True
            
            if os.path.exists(folder_name):
                os.startfile(folder_name)
                return True
                
        elif self.os_type == "Darwin":
            for path in folder_paths:
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    subprocess.run(['open', path])
                    return True
                    
        elif self.os_type == "Linux":
            for path in folder_paths:
                path = os.path.expanduser(path)
                if os.path.exists(path):
                    subprocess.run(['xdg-open', path])
                    return True
        
        return False
    
    def smart_find_and_open_app(self, app_name, executable_hints):
        """Enhanced app opening"""
        print(f"🔍 Searching for: {app_name}")
        
        if self.os_type == "Windows":
            # Direct execution
            for hint in executable_hints:
                try:
                    subprocess.Popen(hint, shell=True)
                    time.sleep(1)
                    return True
                except:
                    pass
            
            # Start command
            for hint in executable_hints:
                try:
                    os.system(f'start "" "{hint}"')
                    time.sleep(1)
                    return True
                except:
                    pass
            
            # Deep search
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
                        if depth > 4:
                            continue
                        
                        for file in files:
                            if file.endswith('.exe'):
                                file_lower = file.lower()
                                for term in search_terms:
                                    if term in file_lower:
                                        try:
                                            os.startfile(os.path.join(root, file))
                                            return True
                                        except:
                                            pass
                except:
                    continue
                    
        elif self.os_type == "Darwin":
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
        """Complete command processing with all features"""
        if not command:
            return {'success': False, 'response': 'No command received'}
        
        command_lower = command.lower()
        
        # Quick exit
        if any(word in command_lower for word in ['exit', 'quit', 'goodbye']):
            response = self.speak("Goodbye!")
            return {'success': True, 'response': response, 'action': 'exit'}
        
        # AI interpretation
        print("🧠 Analyzing command...")
        interpretation = self.llm_interpret_command(command)
        
        if not interpretation:
            response = self.speak("I couldn't understand that.")
            return {'success': False, 'response': response}
        
        print(f"💭 Reasoning: {interpretation.get('reasoning', 'N/A')}")
        
        action = interpretation.get('action', 'CONVERSATION')
        target = interpretation.get('target', '')
        ai_response = interpretation.get('response', '')
        executable_hints = interpretation.get('executable_hints', [])
        folder_paths = interpretation.get('folder_paths', [])
        params = interpretation.get('params', {})
        
        # Execute action
        if action == "SCROLL":
            direction = params.get('direction', target)
            amount = params.get('amount', 3)
            success = self.scroll_action(direction, amount)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'scroll'}
        
        elif action == "TYPE_TEXT":
            success = self.type_text(target)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'type'}
        
        elif action == "PRESS_KEY":
            key = params.get('key', target)
            success = self.press_key(key)
            response = self.speak(ai_response)
            return {'success': success, 'response': response, 'action': 'keypress'}
        
        elif action == "SEARCH_FILES":
            file_type = params.get('file_type', None)
            results = self.search_files(target, file_type)
            
            if results:
                result_text = f"Found {len(results)} results:\n"
                for i, res in enumerate(results[:5], 1):
                    result_text += f"{i}. {res['name']}\n"
                response = self.speak(f"Found {len(results)} files. Top results displayed.")
                return {
                    'success': True, 
                    'response': response, 
                    'action': 'search_files',
                    'results': results
                }
            else:
                response = self.speak("No files found.")
                return {'success': False, 'response': response}
        
        elif action == "OPEN_FILE":
            # If target is a number, open from last search results
            if target.isdigit() and self.context['last_search_results']:
                idx = int(target) - 1
                if 0 <= idx < len(self.context['last_search_results']):
                    file_path = self.context['last_search_results'][idx]['path']
                    success = self.open_file(file_path)
                    response = self.speak(f"Opening {os.path.basename(file_path)}")
                    return {'success': success, 'response': response, 'action': 'open_file'}
            else:
                # Search and open first result
                results = self.search_files(target)
                if results:
                    success = self.open_file(results[0]['path'])
                    response = self.speak(f"Opening {results[0]['name']}")
                    return {'success': success, 'response': response, 'action': 'open_file'}
            
            response = self.speak("File not found.")
            return {'success': False, 'response': response}
        
        elif action == "OPEN_APP":
            success = self.smart_find_and_open_app(target, executable_hints)
            response = self.speak(ai_response if success else f"Couldn't find {target}")
            return {'success': success, 'response': response, 'action': 'open_app'}
        
        elif action == "OPEN_FOLDER":
            success = self.open_folder(target, folder_paths)
            response = self.speak(ai_response if success else f"Couldn't find {target}")
            return {'success': success, 'response': response, 'action': 'open_folder'}
        
        elif action == "SCREEN_CLICK":
            self.speak("Analyzing screen...")
            vision_result = self.analyze_screen_with_vision(command)
            
            if vision_result and vision_result.get('action') == 'CLICK':
                pos = vision_result.get('approximate_position', {})
                if pos:
                    success = self.click_screen_position(pos['x'], pos['y'])
                    response = self.speak(vision_result.get('response', 'Clicked'))
                    return {'success': success, 'response': response, 'action': 'click'}
            
            response = self.speak("Couldn't identify click target.")
            return {'success': False, 'response': response}
        
        elif action == "SCREEN_ANALYZE":
            self.speak("Analyzing screen...")
            vision_result = self.analyze_screen_with_vision(command)
            
            if vision_result:
                response = self.speak(vision_result.get('response', 'Screen analyzed'))
                return {'success': True, 'response': response, 'action': 'analyze'}
            
            response = self.speak("Couldn't analyze screen.")
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
                response = self.speak(f"Error: {str(e)}")
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
    """Get current screen"""
    screenshot = jarvis.capture_screen()
    if screenshot:
        img_base64 = jarvis.image_to_base64(screenshot)
        return jsonify({'success': True, 'image': img_base64})
    return jsonify({'success': False})

@app.route('/api/search-files', methods=['POST'])
def search_files_api():
    """Search files endpoint"""
    data = request.json
    query = data.get('query', '')
    file_type = data.get('file_type', None)
    results = jarvis.search_files(query, file_type)
    return jsonify({'success': True, 'results': results})

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'context': jarvis.context,
        'llm_provider': jarvis.llm_config['provider'],
        'features': {
            'vision': True,
            'typing': True,
            'file_search': True,
            'scroll': True,
            'keyboard': True
        }
    })

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🤖 JARVIS - COMPLETE SYSTEM CONTROL")
    print("="*70)
    print("\n✅ Features Active:")
    print("   • Screen Vision & Click")
    print("   • Scroll (up/down)")
    print("   • Type Text")
    print("   • Press Keys")
    print("   • File Search")
    print("   • App/Folder Opening")
    print("\n💡 Examples:")
    print("   'scroll down'")
    print("   'type hello world'")
    print("   'press enter'")
    print("   'search for python files'")
    print("   'find my resume'")
    print("   'click first link'")
    print("\n🌐 Server: http://localhost:5000")
    print("="*70 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)
