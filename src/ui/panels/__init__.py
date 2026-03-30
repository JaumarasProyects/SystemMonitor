"""
UI Panels module.
Exports all panel classes for the SystemMonitor application.
"""
from ui.panels.dashboard import DashboardPanel
from ui.panels.chat import ChatPanel
from ui.panels.system import SystemPanel
from ui.panels.memory import MemoryPanel
from ui.panels.processes import ProcessesPanel
from ui.panels.network import NetworkPanel
from ui.panels.ports import PortsPanel
from ui.panels.software import SoftwarePanel
from ui.panels.caches import CachesPanel
from ui.panels.security import SecurityPanel
from ui.panels.analysis import AnalysisPanel
from ui.panels.settings import SettingsPanel

__all__ = [
    'DashboardPanel',
    'ChatPanel',
    'SystemPanel',
    'MemoryPanel',
    'ProcessesPanel',
    'NetworkPanel',
    'PortsPanel',
    'SoftwarePanel',
    'CachesPanel',
    'SecurityPanel',
    'AnalysisPanel',
    'SettingsPanel',
]
