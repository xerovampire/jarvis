# 🤖 JARVIS AI Assistant

A sophisticated AI-powered desktop assistant with complete system control capabilities, featuring a futuristic web interface and advanced voice recognition.

![JARVIS AI](https://img.shields.io/badge/JARVIS-AI%20Assistant-00ffff?style=for-the-badge&logo=robot)
![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Web%20Framework-green?style=for-the-badge&logo=flask)
![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge)

## ✨ Features

### 🎯 Core Capabilities
- **Natural Language Processing** - Understands complex commands in plain English
- **Voice Recognition** - Always-on voice control with continuous listening
- **Screen Vision** - AI-powered screen analysis and interaction
- **System Control** - Complete desktop automation and control
- **File Management** - Advanced file and folder search capabilities
- **Application Control** - Smart app detection and launching

### 🎵 Media & Entertainment
- **YouTube Integration** - Direct video playback using yt-dlp
- **Web Search** - Intelligent web browsing and search
- **Music Control** - Play songs, videos, and audio content
- **Website Navigation** - Smart URL construction and opening

### 🖥️ System Integration
- **Windows Registry** - Deep system integration for Windows
- **File System** - Comprehensive file and folder operations
- **Process Management** - Application launching and control
- **Keyboard & Mouse** - Full input automation
- **Screen Interaction** - Click, scroll, and type automation

### 🎨 User Interface
- **Futuristic Design** - Cyberpunk-inspired web interface
- **Real-time Monitoring** - Live system diagnostics and metrics
- **Activity Logging** - Comprehensive command and response tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Windows 10/11 (for full system integration)
- Modern web browser (Chrome/Edge recommended for voice features)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/xerovampire/jarvis.git
   cd jarvis-ai
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Or install manually:
   ```bash
   pip install flask flask-cors pyttsx3 speechrecognition pyautogui pillow pywin32 youtube-search-python yt-dlp google-generativeai requests
   ```

3. **Configure API Keys**
   - Get a Gemini API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Update the API key in `jarvis_backend.py`:
   ```python
   'gemini_api_key': 'YOUR_GEMINI_API_KEY_HERE'
   ```

4. **Run the application**
   ```bash
   python jarvis_backend.py
   ```

5. **Access the interface**
   - Open your browser and go to `http://localhost:5000`
   - Start giving commands!

## 📋 Requirements

### Core Dependencies
```
flask==2.3.3
flask-cors==4.0.0
pyttsx3==2.90
speechrecognition==3.10.0
pyautogui==0.9.54
pillow==10.0.1
pywin32==306
youtube-search-python==1.6.6
yt-dlp==2023.10.13
google-generativeai==0.3.2
requests==2.31.0
```

### System Requirements
- **OS**: Windows 10/11 (recommended), macOS, Linux
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 500MB free space
- **Network**: Internet connection for AI features

## 🎮 Usage Examples

### Voice Commands
```
"Open Visual Studio Code"
"Play despacito"
"Search for Python tutorials"
"Open downloads folder"
"Scroll down"
"Type hello world"
"Press enter"
"Find my resume"
"Open YouTube"
"Watch lofi music"
```

### System Control
```
"Open Chrome browser"
"Search the web for latest news"
"Open documents folder"
"Find all PDF files"
"Click on the search button"
"Analyze the screen"
"Take a screenshot"
```

### Media & Entertainment
```
"Play shape of you"
"Watch Python tutorial"
"Listen to jazz music"
"Put on some lofi beats"
"Search YouTube for cats"
"Open Netflix"
"Play for a reason"
```

## 🏗️ Architecture

### Backend (`jarvis_backend.py`)
- **JarvisAI Class**: Core AI assistant with system integration
- **Flask API**: RESTful endpoints for web interface
- **LLM Integration**: Google Gemini for natural language processing
- **System Modules**: File management, app control, screen interaction

### Frontend (`templates/index.html`)
- **Responsive Design**: Cyberpunk-themed interface
- **Real-time Updates**: Live system monitoring and diagnostics
- **Voice Integration**: Web Speech API for voice commands
- **Interactive Elements**: Command input, status displays, activity logs

### Key Components
```
jarvis_backend.py          # Main application server
templates/
  └── index.html          # Web interface
requirements.txt          # Python dependencies
README.md                 # This file
```

## 🔧 Configuration

### API Keys
```python
# In jarvis_backend.py
self.llm_config = {
    'provider': 'gemini',
    'gemini_api_key': 'YOUR_API_KEY',
    'gemini_model': 'models/gemini-2.5-flash'
}
```

### Voice Settings
```python
# Voice recognition settings
self.recognizer.energy_threshold = 4000
self.recognizer.dynamic_energy_threshold = True

# Text-to-speech settings
self.engine.setProperty('rate', 180)
self.engine.setProperty('volume', 0.9)
```

### System Integration
```python
# Search locations (customizable)
self.search_locations = [
    user_profile,
    os.path.join(user_profile, 'Desktop'),
    os.path.join(user_profile, 'Documents'),
    # Add more locations as needed
]
```

## 🎯 Command Categories

### 1. Application Control
- **OPEN_APP**: Launch applications by name
- **OPEN_FOLDER**: Open system folders
- **OPEN_FILE**: Open specific files

### 2. Web & Media
- **SEARCH_WEB**: Google search
- **PLAY_YOUTUBE**: Direct video playback
- **SEARCH_YOUTUBE**: YouTube search results
- **OPEN_WEBSITE**: Navigate to websites

### 3. System Interaction
- **SCREEN_CLICK**: Click on screen elements
- **SCREEN_ANALYZE**: Analyze screen content
- **TYPE_TEXT**: Type text input
- **PRESS_KEY**: Press keyboard keys
- **SCROLL**: Scroll up/down

### 4. File Management
- **SEARCH_FILES**: Find files and folders
- **OPEN_FILE**: Open specific files

### 5. General
- **CONVERSATION**: Chat with AI
- **SYSTEM_COMMAND**: Execute system commands

## 🔍 Advanced Features

### Screen Vision
- AI-powered screen analysis using Gemini Vision
- Automatic element detection and interaction
- Smart click positioning based on screen content

### File Search
- Recursive directory scanning
- Multiple file type support
- Intelligent path detection
- Cached results for performance

### Voice Control
- Continuous listening mode
- Automatic restart on errors
- Multiple language support
- Noise filtering and recognition

### System Integration
- Windows Registry access
- Process management
- Application detection
- System metrics monitoring

## 🛠️ Development

### Adding New Commands
1. Add command interpretation in `llm_interpret_command()`
2. Implement action handler in `process_command()`
3. Add corresponding method in `JarvisAI` class
4. Update frontend if needed

### Customizing the Interface
- Modify CSS in `templates/index.html`
- Add new panels or components
- Update JavaScript for new features
- Customize animations and effects

### Extending System Integration
- Add new OS-specific modules
- Implement additional file system operations
- Create custom application launchers
- Add new automation capabilities

## 🐛 Troubleshooting

### Common Issues

**Voice recognition not working**
- Ensure you're using Chrome or Edge
- Check microphone permissions
- Verify internet connection

**Backend connection failed**
- Make sure Python server is running
- Check if port 5000 is available
- Verify firewall settings

**YouTube playback issues**
- Install yt-dlp: `pip install yt-dlp`
- Check internet connection
- Verify YouTube accessibility

**System control not working**
- Run as administrator (Windows)
- Check antivirus software
- Verify Python permissions

### Debug Mode
```bash
# Enable debug logging
python jarvis_backend.py --debug
```

## 📊 Performance

### System Requirements
- **CPU**: Modern multi-core processor
- **Memory**: 4GB RAM minimum
- **Storage**: 500MB for application + cache
- **Network**: Stable internet for AI features

### Optimization Tips
- Close unnecessary applications
- Use SSD storage for better performance
- Ensure stable internet connection
- Regular system maintenance

## 🔒 Security

### Data Privacy
- No data is stored permanently
- Commands are processed locally
- API keys are kept secure
- No personal information is transmitted

### System Safety
- Fail-safe mechanisms for automation
- User confirmation for critical operations
- Sandboxed execution environment
- Regular security updates

## 🤝 Contributing

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Setup
```bash
git clone https://github.com/xerovampire/jarvis.git
cd jarvis
pip install -r requirements.txt
python jarvis_backend.py
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini** - AI language model
- **Flask** - Web framework
- **yt-dlp** - YouTube integration
- **PyAutoGUI** - System automation
- **SpeechRecognition** - Voice control

## 📞 Support

### Getting Help
- Check the [Issues](https://github.com/xeroinsane/jarvis/issues) page

*"Sometimes you gotta run before you can walk."* - Tony Stark

