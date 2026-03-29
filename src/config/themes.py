"""
Theme configuration and management for SystemMonitor.
"""
import customtkinter as ctk


class ThemeManager:
    """Manages application themes and color schemes."""
    
    COLORS = {
        'dark': {
            'bg_main': '#1a1a2e',
            'bg_sec': '#16213e',
            'bg_card': '#0f3460',
            'primary': '#00d9ff',
            'secondary': '#e94560',
            'success': '#00ff88',
            'warning': '#ffaa00',
            'text': '#ffffff',
            'text_sec': '#a0a0a0',
            'border': '#2a2a4a',
            'hover': '#1a4a7a'
        },
        'light': {
            'bg_main': '#f0f2f5',
            'bg_sec': '#ffffff',
            'bg_card': '#ffffff',
            'primary': '#0066cc',
            'secondary': '#cc3366',
            'success': '#00aa55',
            'warning': '#ff8800',
            'text': '#1a1a1a',
            'text_sec': '#666666',
            'border': '#dde0e4',
            'hover': '#e6e9ed'
        }
    }
    
    def __init__(self, theme_name: str = "dark"):
        self.theme_name = theme_name
        self.theme = self.COLORS[self.theme_name]
    
    @property
    def available_themes(self) -> list:
        """Return list of available theme names."""
        return list(self.COLORS.keys())
    
    def apply(self):
        """Apply current theme to the application."""
        ctk.set_appearance_mode(self.theme_name)
    
    def switch_theme(self, theme_name: str):
        """Switch to a different theme."""
        if theme_name in self.COLORS:
            self.theme_name = theme_name
            self.theme = self.COLORS[theme_name]
            self.apply()
            return True
        return False
    
    def get_color(self, key: str) -> str:
        """Get a specific color from current theme."""
        return self.theme.get(key, '#ffffff')
