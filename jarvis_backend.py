"""
JARVIS AI - Intelligent Backend with LLM-Powered Command Execution
The AI thinks and executes commands, not just pattern matching!
Run: python jarvis_backend_intelligent.py
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
        
        self.context = {
            'last_browser_tab': None,
            'last_app': None,
            'conversation_history': []
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
        
        print("🤖 Jarvis AI initialized with INTELLIGENT command execution!")
        print("💡 I can now understand and execute ANY command through reasoning!")
    
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
    
    def listen_continuous(self):
        """Always-on listening mode"""
        with sr.Microphone() as source:
            print("\n🎤 Jarvis is listening (Always On)...")
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            
            while self.is_listening:
                try:
                    print("👂 Waiting for command...")
                    audio = self.recognizer.listen(source, timeout=None, phrase_time_limit=10)
                    
                    try:
                        text = self.recognizer.recognize_google(audio)
                        print(f"\n🗣️ You said: {text}")
                        result = self.process_command(text)
                        time.sleep(1)
                        
                    except sr.UnknownValueError:
                        continue
                    except sr.RequestError as e:
                        print(f"Speech recognition error: {e}")
                        time.sleep(2)
                        
                except Exception as e:
                    print(f"Listening error: {e}")
                    time.sleep(1)
    
    def start_listening(self):
        """Start the always-on listening in background"""
        self.is_listening = True
        listener_thread = threading.Thread(target=self.listen_continuous, daemon=True)
        listener_thread.start()
        print("✅ Always-on voice listening started!")
    
    def stop_listening(self):
        """Stop listening"""
        self.is_listening = False
        print("🛑 Voice listening stopped")
    
    def get_installed_apps(self):
        """Get list of commonly installed applications on the system"""
        apps = []
        try:
            if self.os_type == "Windows":
                paths = [
                    os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                    os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
                    os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
                ]
                
                for path in paths:
                    if os.path.exists(path):
                        for item in os.listdir(path):
                            apps.append(item)
        except:
            pass
        return apps[:50]  # Return first 50 to avoid too much data
    
    def llm_interpret_command(self, user_command):
        """
        LLM interprets the command and decides what action to take
        This is the BRAIN of intelligent execution
        """
        
        system_prompt = f"""You are Jarvis, an intelligent AI assistant that can execute system commands.

IMPORTANT: Analyze the user's command and respond with a JSON object that describes the action.

Available actions:
1. OPEN_APP - Open an application
2. SEARCH_WEB - Search on Google
3. SEARCH_YOUTUBE - Search on YouTube
4. OPEN_WEBSITE - Open a specific website
5. CONVERSATION - General conversation/question
6. SYSTEM_COMMAND - Execute a system command

Operating System: {self.os_type}

Instructions:
- Think intelligently about what the user wants
- "open vs" should map to "Visual Studio Code" or "vscode"
- "open chrome" should open "Google Chrome"
- Be smart about abbreviations and common names
- For app names, provide the FULL proper name and common executable names

Respond ONLY with a JSON object in this format:
{{
    "action": "OPEN_APP" | "SEARCH_WEB" | "SEARCH_YOUTUBE" | "OPEN_WEBSITE" | "CONVERSATION" | "SYSTEM_COMMAND",
    "target": "the app name, search query, website, or command",
    "reasoning": "brief explanation of your interpretation",
    "executable_hints": ["possible.exe", "names", "to", "try"],
    "response": "what to say to the user"
}}

Examples:
User: "open vs"
{{
    "action": "OPEN_APP",
    "target": "Visual Studio Code",
    "reasoning": "VS commonly refers to Visual Studio Code",
    "executable_hints": ["code", "code.exe", "vscode"],
    "response": "Opening Visual Studio Code"
}}

User: "search python tutorials"
{{
    "action": "SEARCH_WEB",
    "target": "python tutorials",
    "reasoning": "User wants to search for information",
    "executable_hints": [],
    "response": "Searching for python tutorials"
}}

User: "what is quantum computing"
{{
    "action": "CONVERSATION",
    "target": "",
    "reasoning": "This is a knowledge question",
    "executable_hints": [],
    "response": "Quantum computing is a type of computation that harnesses quantum mechanical phenomena like superposition and entanglement to process information in ways classical computers cannot. It uses quantum bits or 'qubits' that can exist in multiple states simultaneously, enabling parallel processing of vast amounts of data."
}}

Now interpret this command:
User: {user_command}
"""

        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            response = model.generate_content(system_prompt)
            
            # Extract JSON from response
            response_text = response.text.strip()
            
            # Try to find JSON in the response
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                interpretation = json.loads(json_str)
                return interpretation
            else:
                # Fallback if no JSON found
                return {
                    "action": "CONVERSATION",
                    "target": "",
                    "reasoning": "Could not parse command",
                    "executable_hints": [],
                    "response": response_text
                }
                
        except Exception as e:
            print(f"LLM Interpretation Error: {e}")
            return None
    
    def smart_find_and_open_app(self, app_name, executable_hints):
        """
        Intelligently find and open any application
        Uses LLM hints and system search
        """
        print(f"🔍 Searching for: {app_name}")
        print(f"💡 Hints: {executable_hints}")
        
        if self.os_type == "Windows":
            # Try executable hints first
            for hint in executable_hints:
                try:
                    if hint.endswith('.exe'):
                        os.startfile(hint)
                        print(f"✅ Opened via hint: {hint}")
                        return True
                    else:
                        # Try as command
                        subprocess.Popen([hint], shell=True)
                        print(f"✅ Opened via command: {hint}")
                        return True
                except:
                    continue
            
            # Search in common paths
            search_paths = [
                os.environ.get('PROGRAMFILES', 'C:\\Program Files'),
                os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)'),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
                os.path.join(os.environ.get('APPDATA', ''), 'Microsoft\\Windows\\Start Menu\\Programs'),
            ]
            
            # Search terms based on app name and hints
            search_terms = [app_name.lower()] + [h.lower().replace('.exe', '') for h in executable_hints]
            
            for base_path in search_paths:
                if not os.path.exists(base_path):
                    continue
                    
                try:
                    for root, dirs, files in os.walk(base_path):
                        # Check depth to avoid too deep searches
                        depth = root[len(base_path):].count(os.sep)
                        if depth > 3:
                            continue
                        
                        for file in files:
                            if file.endswith('.exe'):
                                file_lower = file.lower()
                                # Check if any search term matches
                                for term in search_terms:
                                    if term in file_lower:
                                        exe_path = os.path.join(root, file)
                                        print(f"✅ Found: {exe_path}")
                                        try:
                                            os.startfile(exe_path)
                                            return True
                                        except:
                                            continue
                except Exception as e:
                    continue
            
            # Try Windows start command
            for hint in [app_name] + executable_hints:
                try:
                    os.system(f'start "" "{hint}"')
                    time.sleep(1)  # Give it time to start
                    print(f"✅ Attempted via start command: {hint}")
                    return True
                except:
                    continue
                    
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
    
    def get_llm_response(self, prompt):
        """Get intelligent response from Gemini for conversations"""
        system_prompt = """You are Jarvis, Tony Stark's AI assistant. You are:
- Highly intelligent, witty, and sophisticated
- Expert in technology, science, and general knowledge
- Helpful and conversational
- Slightly humorous but professional

Provide detailed, intelligent responses. Keep responses concise but informative (2-4 sentences for simple questions, more for complex ones)."""

        try:
            model = genai.GenerativeModel('models/gemini-2.5-flash')
            full_prompt = f"{system_prompt}\n\nUser: {prompt}\nJarvis:"
            response = model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I encountered an error processing that request."
    
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
        """
        INTELLIGENT command processing using LLM
        The AI thinks about what you want and executes it
        """
        if not command:
            return {'success': False, 'response': 'No command received'}
        
        command_lower = command.lower()
        
        # Quick exit commands
        if any(word in command_lower for word in ['exit', 'quit', 'goodbye', 'stop listening']):
            response = self.speak("Goodbye! Shutting down.")
            if self.use_voice:
                self.stop_listening()
            return {'success': True, 'response': response, 'action': 'exit'}
        
        # Let the LLM interpret the command
        print("🧠 Analyzing command with AI...")
        interpretation = self.llm_interpret_command(command)
        
        if not interpretation:
            response = self.speak("I'm having trouble understanding that command.")
            return {'success': False, 'response': response}
        
        print(f"💭 AI Reasoning: {interpretation.get('reasoning', 'N/A')}")
        
        action = interpretation.get('action', 'CONVERSATION')
        target = interpretation.get('target', '')
        ai_response = interpretation.get('response', '')
        executable_hints = interpretation.get('executable_hints', [])
        
        # Execute based on AI's decision
        if action == "OPEN_APP":
            success = self.smart_find_and_open_app(target, executable_hints)
            if success:
                response = self.speak(ai_response)
                return {'success': True, 'response': response, 'action': 'open_app'}
            else:
                response = self.speak(f"I couldn't find {target} on your system. Please make sure it's installed.")
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

@app.route('/api/status', methods=['GET'])
def status():
    return jsonify({
        'status': 'online',
        'context': jarvis.context,
        'llm_provider': jarvis.llm_config['provider']
    })

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 JARVIS AI - INTELLIGENT Backend Server")
    print("="*60)
    print("\n✅ All systems online!")
    print("\n🧠 INTELLIGENT MODE ACTIVATED!")
    print("   - AI thinks about your commands")
    print("   - Can open ANY installed application")
    print("   - Understands abbreviations and context")
    print("   - No pre-feeding required!")
    print("\n💡 Examples:")
    print("   'open vs' → Opens Visual Studio Code")
    print("   'open chrome' → Opens Google Chrome")
    print("   'search python tutorials' → Google search")
    print("   'what is AI' → Intelligent conversation")
    print("\n🌐 Server running at: http://localhost:5000")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)
