# SystemMonitor

A modern Windows system monitoring application with AI-powered analysis capabilities. Built with Python and CustomTkinter.

## Overview

SystemMonitor is a comprehensive desktop application that provides real-time system monitoring, hardware information, and AI-powered analysis through local LLM models (Ollama). It features a clean, modular architecture and supports dark/light themes.

## Features

### 📊 Dashboard
- Real-time CPU and RAM usage graphs
- Historical data visualization (last 60 seconds)
- Quick system status overview

### 💻 System Information
- **General Info**: Computer name, OS, architecture, uptime
- **Motherboard**: Manufacturer, product, version, serial number
- **BIOS**: Version, date, manufacturer
- **CPU**: Model, cores (physical/logical), frequencies, usage per core, CPU times
- **GPU**: Memory, driver, resolution, usage
- **Battery**: Charge level, status, time remaining

### 🧠 Memory
- RAM usage with detailed breakdown
- Swap/Virtual memory information

### ⚡ Processes
- Running processes list
- Sort by CPU/Memory usage
- Kill process capability

### 🌐 Network
- Network interfaces overview
- Connection statistics
- Bytes sent/received

### 🔌 Ports
- Active network connections
- Protocol information (TCP/UDP)
- Process association

### 📦 Software
- Installed programs list
- Windows features

### 🗑️ Caches & Cookies
- Browser cache management (Chrome, Edge, Firefox)
- Cookies viewer with search
- Clear cache/cookies for individual browsers

### 🤖 AI Analysis
- **General Analysis**: System health assessment via Ollama
- **Security Analysis**: Vulnerability detection and recommendations
- Requires Ollama running locally

### ⚙️ Configuration
- LLM provider selection (Ollama, OpenAI, DeepSeek, Anthropic, etc.)
- API key management
- Theme switching (Dark/Light)

### 💬 AI Chat
- Conversational AI assistant
- Text-to-speech with voice output
- Context-aware responses using system data

## Requirements

- Windows 10/11
- Python 3.10+
- [Ollama](https://ollama.ai/) (for AI features)

### Python Dependencies

```
customtkinter>=5.2.0
psutil>=5.9.0
requests>=2.31.0
pygame>=2.5.0
edge-tts>=6.1.0
```

Install with:
```bash
pip install -r requirements.txt
```

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JaumarasProyects/SystemMonitor.git
cd SystemMonitor
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. (Optional) Install Ollama for AI features:
```bash
# Download from https://ollama.ai
# Then pull a model:
ollama pull llama3.2
```

4. Run the application:
```bash
python src/main.py
```

Or use the provided batch file:
```bash
SystemMonitor.bat
```

## Project Structure

```
src/
├── config/
│   ├── settings.py      # Application settings
│   └── themes.py        # Theme management (dark/light)
├── models/
│   └── system_info.py   # System information gathering
├── services/
│   ├── llm_providers.py # LLM service integration
│   └── tts_service.py   # Text-to-speech service
├── ui/
│   ├── app.py           # Main application window
│   ├── components.py    # Reusable UI components
│   └── panels/
│       ├── dashboard.py     # Main dashboard
│       ├── chat.py          # AI chat panel
│       ├── system.py        # System information
│       ├── memory.py        # Memory info
│       ├── processes.py    # Process manager
│       ├── network.py       # Network overview
│       ├── ports.py         # Port monitor
│       ├── software.py      # Software list
│       ├── caches.py        # Cache/cookies manager
│       ├── analysis.py      # AI analysis
│       └── settings.py      # Configuration
└── main.py              # Entry point
```

## Usage

### Navigation
Use the sidebar to navigate between different panels:
- Click any panel button in the left sidebar
- Current panel is highlighted

### Dashboard
The dashboard shows real-time CPU and RAM graphs that update every second.

### System Information
All hardware information is displayed in organized cards. Data includes:
- General system info and uptime
- Motherboard details
- BIOS information
- CPU specifications and per-core usage
- GPU information
- Battery status (if available)

### Browser Cache Management
1. Go to "Cachés y Cookies" panel
2. View cache sizes for Chrome, Edge, and Firefox
3. Click "Ver Cookies" to browse cookies with search
4. Use "Limpiar" buttons to clear cache or cookies

### AI Analysis
1. Ensure Ollama is running (`ollama serve`)
2. Go to "Análisis IA" panel
3. Select a model from the dropdown
4. Click "Análisis General" or "Seguridad"
5. Wait for the AI analysis to complete

### AI Chat
1. Click the "Chat IA" button in the footer
2. Type your question
3. Enable voice output with the speaker button
4. Chat context includes current system data

### Theme Switching
1. Go to "Configuración" panel
2. Select theme from dropdown
3. Click "Aplicar"

## Configuration

### API Keys
Set API keys in the Settings panel for cloud LLM providers:
- OpenAI (GPT models)
- DeepSeek
- Anthropic (Claude)
- Google Gemini
- Groq
- Grok (xAI)
- Mistral
- Azure OpenAI

### Voice Settings
Configure TTS voice, rate, and volume in the chat panel.

## Troubleshooting

### Ollama Connection Issues
- Ensure Ollama is running: `ollama serve`
- Check if models are installed: `ollama list`
- Pull a model if needed: `ollama pull llama3.2`

### Permission Errors
Some features require administrator privileges:
- Process termination
- Service management

### Theme Not Applying
Click the panel button again after changing themes to refresh the UI.

## Development

The project follows a modular architecture pattern:
- `config/` - Configuration management
- `models/` - Data models and business logic
- `services/` - External service integrations
- `ui/panels/` - Individual panel implementations

## License

MIT License

## Contributing

Contributions welcome! Please open an issue or submit a pull request.
