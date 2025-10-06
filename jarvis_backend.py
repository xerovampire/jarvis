"""
JARVIS AI - Backend with Always-On Voice & Sm        # LLM Configuration
        self.llm_config = {
            'provider': 'gemini',
            'gemini_api_key': 'AIzaSyBoL9PJ22_qoJe8iaiY4aO5QcnDZkNO7dM',  # ← PUT YOUR GEMINI API KEY HERE
            'gemini_model': 'models/gemini-pro-latest'
        }p Opening
Run: python jarvis_backend.py
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

app = Flask(__name__)
CORS(app)

class JarvisAI:
    def __init__(self, use_voice=True):
        self.use_voice = use_voice
        self.is_listening = False
        
        if use_voice:
            # Initialize text-to-speech engine
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', 180)
            self.engine.setProperty('volume', 0.9)
            
            # Initialize speech recognizer
            self.recognizer = sr.Recognizer()
            self.recognizer.energy_threshold = 4000
            self.recognizer.dynamic_energy_threshold = True
        
        # Get OS type
        self.os_type = platform.system()
        
        # Conversation context
        self.context = {
            'last_browser_tab': None,
            'last_app': None,
            'conversation_history': []
        }
        
        # LLM Configuration
        self.llm_config = {
            'provider': 'gemini',
            'gemini_api_key': 'AIzaSyBoL9PJ22_qoJe8iaiY4aO5QcnDZkNO7dM',  # ← PUT YOUR GEMINI API KEY HERE
            'gemini_model': 'gemini-pro-latest'
        }
        
        print("🤖 Jarvis AI initialized successfully!")
        
        # Verify API key is set
        if not self.llm_config['gemini_api_key']:
            print("\n⚠️ Warning: Gemini API key not set. Get one at: https://makersuite.google.com/app/apikey")
    
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
                        
                        # Process the command
                        result = self.process_command(text)
                        
                        # Small delay before listening again
                        time.sleep(1)
                        
                    except sr.UnknownValueError:
                        # Couldn't understand, just continue listening
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
    
    def get_llm_response(self, prompt):
        """Get intelligent response from Gemini"""
        
        system_prompt = """You are Jarvis, Tony Stark's AI assistant. You are:
- Highly intelligent, witty, and sophisticated
- Expert in technology, science, and general knowledge
- Helpful and conversational
- Can control applications and system functions

Provide detailed, intelligent responses. Be engaging and slightly witty like the real Jarvis.
Keep responses concise but informative (2-4 sentences for simple questions, more for complex ones)."""

        try:
            if not self.llm_config['gemini_api_key']:
                return "Please set your Gemini API key in the configuration. Get it free at: https://makersuite.google.com/app/apikey"
            
            try:
                # Configure Gemini with the API key
                genai.configure(api_key=self.llm_config['gemini_api_key'])
                
                # Create the model
                model = genai.GenerativeModel('gemini-pro-latest')
                
                # Combine system prompt and user message
                full_prompt = f"{system_prompt}\n\nUser: {prompt}\nJarvis:"
                
                # Generate response
                response = model.generate_content(full_prompt)
                
                # Check if response was blocked
                if response.prompt_feedback.block_reason:
                    return "I apologize, but I cannot provide a response to that query."
                
                return response.text
                
            except Exception as api_error:
                print(f"Gemini API Error: {str(api_error)}")
                return "I'm having trouble connecting to my intelligence module. Please check the API key and server logs for details."
        
        except requests.exceptions.Timeout:
            return "My response is taking longer than expected. Please try again."
        except requests.exceptions.ConnectionError:
            return "Cannot connect to DeepSeek API. Please check your internet connection."
        except Exception as e:
            print(f"LLM Error: {e}")
            return "I encountered an error processing that request."
    
    def smart_open_application(self, app_name):
        """Intelligently open any application - doesn't fail on unknown apps"""
        print(f"🔍 Attempting to open: {app_name}")
        
        # Common app mappings
        common_apps = {
            'notepad': ['notepad.exe'],
            'calculator': ['calc.exe', 'calculator'],
            'paint': ['mspaint.exe', 'paint'],
            'explorer': ['explorer.exe', 'explorer'],
            'chrome': ['chrome.exe', 'chrome', 'google-chrome'],
            'edge': ['msedge.exe', 'microsoft-edge', 'edge'],
            'firefox': ['firefox.exe', 'firefox'],
            'brave': ['brave.exe', 'brave'],
            'opera': ['opera.exe', 'opera'],
            'word': ['winword.exe', 'word', 'microsoft word'],
            'excel': ['excel.exe', 'excel'],
            'powerpoint': ['powerpnt.exe', 'powerpoint'],
            'outlook': ['outlook.exe', 'outlook'],
            'vscode': ['code', 'code.exe', 'visual studio code'],
            'spotify': ['spotify.exe', 'spotify'],
            'discord': ['discord.exe', 'discord'],
            'whatsapp': ['whatsapp.exe', 'whatsapp'],
            'telegram': ['telegram.exe', 'telegram'],
            'steam': ['steam.exe', 'steam'],
            'vlc': ['vlc.exe', 'vlc'],
            'obs': ['obs64.exe', 'obs'],
            'photoshop': ['photoshop.exe', 'photoshop'],
        }
        
        try:
            if self.os_type == "Windows":
                # Try exact match first
                if app_name in common_apps:
                    for cmd in common_apps[app_name]:
                        try:
                            if cmd == 'code':
                                subprocess.Popen([cmd])
                                self.context['last_app'] = app_name
                                return True
                            else:
                                os.startfile(cmd)
                                self.context['last_app'] = app_name
                                return True
                        except FileNotFoundError:
                            continue
                
                # Try multiple methods for unknown apps
                methods = [
                    # Method 1: Direct start
                    lambda: os.startfile(app_name),
                    # Method 2: With .exe
                    lambda: os.startfile(f"{app_name}.exe"),
                    # Method 3: Using start command
                    lambda: os.system(f'start "" "{app_name}"'),
                    # Method 4: With .exe using start
                    lambda: os.system(f'start "" "{app_name}.exe"'),
                    # Method 5: Search in common paths
                    lambda: self._search_and_open(app_name),
                ]
                
                for method in methods:
                    try:
                        method()
                        self.context['last_app'] = app_name
                        print(f"✅ Successfully opened: {app_name}")
                        return True
                    except:
                        continue
                
                # If all methods fail, return False
                print(f"⚠️ Could not find application: {app_name}")
                return False
            
            elif self.os_type == "Darwin":  # macOS
                try:
                    subprocess.run(['open', '-a', app_name])
                    self.context['last_app'] = app_name
                    return True
                except:
                    return False
            
            elif self.os_type == "Linux":
                try:
                    subprocess.Popen([app_name])
                    self.context['last_app'] = app_name
                    return True
                except:
                    return False
                    
        except Exception as e:
            print(f"Error opening {app_name}: {e}")
            return False
    
    def _search_and_open(self, app_name):
        """Search for app in common installation paths"""
        common_paths = [
            os.path.join(os.environ.get('PROGRAMFILES', 'C:\\Program Files')),
            os.path.join(os.environ.get('PROGRAMFILES(X86)', 'C:\\Program Files (x86)')),
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Programs'),
        ]
        
        for base_path in common_paths:
            if os.path.exists(base_path):
                for root, dirs, files in os.walk(base_path):
                    for file in files:
                        if app_name.lower() in file.lower() and file.endswith('.exe'):
                            exe_path = os.path.join(root, file)
                            os.startfile(exe_path)
                            return True
        return False
    
    def extract_app_name(self, command):
        """Extract and normalize app names from command"""
        command = command.lower()
        
        # App name mappings with aliases
        app_mappings = {
            'visual studio code': 'vscode',
            'vs code': 'vscode',
            'vscode': 'vscode',
            'code': 'vscode',
            'google chrome': 'chrome',
            'chrome': 'chrome',
            'microsoft edge': 'edge',
            'edge': 'edge',
            'mozilla firefox': 'firefox',
            'firefox': 'firefox',
            'notepad': 'notepad',
            'calculator': 'calculator',
            'calc': 'calculator',
            'paint': 'paint',
            'file explorer': 'explorer',
            'explorer': 'explorer',
            'word': 'word',
            'microsoft word': 'word',
            'excel': 'excel',
            'microsoft excel': 'excel',
            'powerpoint': 'powerpoint',
            'outlook': 'outlook',
            'spotify': 'spotify',
            'discord': 'discord',
            'whatsapp': 'whatsapp',
            'telegram': 'telegram',
            'brave': 'brave',
            'opera': 'opera',
            'steam': 'steam',
            'obs': 'obs',
            'vlc': 'vlc',
            'photoshop': 'photoshop'
        }
        
        # Try to find app name in command
        for alias, app_name in app_mappings.items():
            if alias in command:
                return app_name
        
        # If no match, extract words after "open"
        if 'open' in command:
            words = command.replace('open', '').strip().split()
            if words:
                # Return the full name if it's multiple words
                return ' '.join(words)
        
        return None
    
    def search_web(self, query):
        """Search the web"""
        search_url = f"https://www.google.com/search?q={quote(query)}"
        webbrowser.open(search_url)
        self.context['last_browser_tab'] = 'search'
    
    def open_website(self, site_name):
        """Open specific websites"""
        websites = {
            'youtube': 'https://www.youtube.com',
            'gmail': 'https://mail.google.com',
            'mail': 'https://mail.google.com',
            'facebook': 'https://www.facebook.com',
            'twitter': 'https://www.twitter.com',
            'x': 'https://www.x.com',
            'instagram': 'https://www.instagram.com',
            'reddit': 'https://www.reddit.com',
            'github': 'https://www.github.com',
            'netflix': 'https://www.netflix.com',
            'spotify': 'https://open.spotify.com',
            'amazon': 'https://www.amazon.com',
            'linkedin': 'https://www.linkedin.com'
        }
        
        url = websites.get(site_name, f"https://www.{site_name}.com")
        webbrowser.open(url)
        self.context['last_browser_tab'] = site_name
        return url
    
    def youtube_search(self, query):
        """Search YouTube"""
        search_url = f"https://www.youtube.com/results?search_query={quote(query)}"
        webbrowser.open(search_url)
    
    def process_command(self, command):
        """Process commands with intelligence"""
        if not command:
            return {'success': False, 'response': 'No command received'}
        
        command_original = command
        command = command.lower()
        
        # Exit commands
        if any(word in command for word in ['exit', 'quit', 'goodbye', 'stop listening']):
            response = self.speak("Goodbye! Shutting down voice recognition.")
            if self.use_voice:
                self.stop_listening()
            return {'success': True, 'response': response, 'action': 'exit'}
        
        # Clear context command
        if 'stop searching' in command or 'clear context' in command or 'reset' in command:
            self.context['last_browser_tab'] = None
            response = self.speak("Context cleared. Ready for new commands.")
            return {'success': True, 'response': response, 'action': 'clear_context', 'continue': True}
        
        # Check for conversation keywords that should NOT be YouTube searches
        conversation_keywords = [
            'tell me', 'what is', 'what are', 'who is', 'who are', 
            'how do', 'how can', 'why', 'when', 'where', 'explain',
            'joke', 'story', 'help me', 'can you', 'do you',
            'should i', 'could you', 'would you', 'define',
            'calculate', 'solve', 'think', 'opinion'
        ]
        
        is_conversation = any(keyword in command for keyword in conversation_keywords)
        
        # Open applications
        if 'open' in command:
            # Clear YouTube context when opening something else
            if 'youtube' not in command:
                self.context['last_browser_tab'] = None
            
            if 'mail' in command or 'gmail' in command:
                self.open_website('gmail')
                response = self.speak("Opening Gmail")
                return {'success': True, 'response': response, 'action': 'open_app', 'continue': True}
            
            elif 'youtube' in command:
                self.open_website('youtube')
                response = self.speak("Opening YouTube")
                return {'success': True, 'response': response, 'action': 'open_website', 'continue': True}
            
            else:
                # Extract app name intelligently
                app_name = self.extract_app_name(command)
                if app_name:
                    success = self.smart_open_application(app_name)
                    if success:
                        response = self.speak(f"Opening {app_name}")
                        return {'success': True, 'response': response, 'action': 'open_app', 'continue': True}
                    else:
                        response = self.speak(f"I couldn't find {app_name}. Please make sure it's installed on your system.")
                        return {'success': False, 'response': response, 'action': 'error', 'continue': True}
        
        # Explicit "don't" or "just" commands - clear context and use LLM
        elif 'don\'t' in command or 'just' in command:
            # Clear any context
            self.context['last_browser_tab'] = None
            llm_response = self.get_llm_response(command_original)
            if llm_response:
                response = self.speak(llm_response)
                return {'success': True, 'response': response, 'action': 'conversation', 'continue': True}
        
        # Search commands (explicit)
        elif command.startswith('search '):
            query = command.replace('search', '').strip()
            
            # Only search YouTube if context AND query makes sense
            if self.context.get('last_browser_tab') == 'youtube' and not is_conversation:
                self.youtube_search(query)
                response = self.speak(f"Searching YouTube for {query}")
            else:
                self.search_web(query)
                response = self.speak(f"Searching for {query}")
            return {'success': True, 'response': response, 'action': 'search', 'continue': True}
        
        # YouTube specific with "play"
        elif 'play' in command and not is_conversation:
            query = command.replace('play', '').strip()
            if query:
                self.youtube_search(query)
                response = self.speak(f"Playing {query} on YouTube")
                return {'success': True, 'response': response, 'action': 'youtube', 'continue': True}
        
        # Context-aware YouTube search (only for SHORT queries without conversation keywords)
        elif (self.context.get('last_browser_tab') == 'youtube' and 
              len(command.split()) <= 4 and 
              not is_conversation and
              not command.startswith(('what', 'how', 'why', 'who', 'when', 'where'))):
            self.youtube_search(command)
            response = self.speak(f"Searching YouTube for {command}")
            return {'success': True, 'response': response, 'action': 'youtube_search', 'continue': True}
        
        # Use LLM for everything else (conversations, questions, etc.)
        else:
            # Clear YouTube context for conversations
            if is_conversation:
                self.context['last_browser_tab'] = None
            
            llm_response = self.get_llm_response(command_original)
            if llm_response:
                response = self.speak(llm_response)
                return {'success': True, 'response': response, 'action': 'conversation', 'continue': True}
            else:
                response = self.speak("I'm here to help! Try commands like 'open app', 'search something', or ask me a question.")
                return {'success': True, 'response': response, 'action': 'help', 'continue': True}

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
    print("🤖 JARVIS AI - Backend Server")
    print("="*60)
    print("\n✅ All systems online!")
    print("\n🧠 LLM Provider: Google Gemini")
    print("   Get API key: https://makersuite.google.com/app/apikey")
    print("\n🎤 Always-On Voice: Use web interface")
    print("\n📱 Smart App Opening: Can open any installed app")
    print("\n🌐 Server running at: http://localhost:5000")
    print("\n💡 Features:")
    print("   • Always-on voice recognition (no repeated clicks)")
    print("   • Opens ANY app - doesn't fail on unknown apps")
    print("   • Intelligent conversation with Google Gemini")
    print("   • Context-aware commands")
    print("="*60 + "\n")
    
    app.run(debug=True, port=5000, use_reloader=False)