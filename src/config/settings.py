"""
Settings persistence for SystemMonitor.
"""
import json
import os


class Settings:
    """Manages application settings persistence."""
    
    DEFAULT_SETTINGS = {
        'theme': 'dark',
        'llm_provider': 'ollama',
        'api_keys': {},
        'tts_enabled': False,
        'tts_voice': 'es-ES-AlvaroNeural',
        'tts_rate': '+0%',
        'tts_volume': '+0%',
    }
    
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_dir = os.path.join(os.path.expanduser('~'), '.systemmonitor')
            os.makedirs(config_dir, exist_ok=True)
            config_path = os.path.join(config_dir, 'settings.json')
        
        self.config_path = config_path
        self._settings = None
        self.load()
    
    def load(self):
        """Load settings from file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    self._settings = {**self.DEFAULT_SETTINGS, **json.load(f)}
            except (json.JSONDecodeError, IOError):
                self._settings = self.DEFAULT_SETTINGS.copy()
        else:
            self._settings = self.DEFAULT_SETTINGS.copy()
    
    def save(self):
        """Save settings to file."""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
        except IOError as e:
            print(f"Error saving settings: {e}")
    
    def get(self, key: str, default=None):
        """Get a setting value."""
        return self._settings.get(key, default)
    
    def set(self, key: str, value):
        """Set a setting value and persist."""
        self._settings[key] = value
        self.save()
    
    def get_api_key(self, provider: str) -> str:
        """Get API key for a specific provider."""
        return self._settings.get('api_keys', {}).get(provider, '')
    
    def set_api_key(self, provider: str, key: str):
        """Set API key for a specific provider."""
        if 'api_keys' not in self._settings:
            self._settings['api_keys'] = {}
        self._settings['api_keys'][provider] = key
        self.save()
