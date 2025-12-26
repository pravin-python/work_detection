"""
Fallback window collector for unsupported platforms or when libs unavailable
Returns empty events gracefully
"""

import time
from datetime import datetime
from collections import deque
from typing import List, Dict, Any

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class FallbackWindowCollector:
    """Fallback window collector when platform-specific libs unavailable"""
    
    def __init__(self, poll_interval: float = 1.0, buffer_size: int = 1000):
        """
        Initialize fallback window collector
        
        Args:
            poll_interval: Ignored (for API compatibility)
            buffer_size: Ignored (for API compatibility)
        """
        self.events = deque(maxlen=0)  # Empty buffer
        self.is_running = False
        
        logger.warning("FallbackWindowCollector initialized - window tracking disabled")
        logger.warning("Install platform-specific libraries to enable window tracking:")
        logger.warning("  Windows: pip install pywin32")
        logger.warning("  Linux:   pip install python-xlib")
        logger.warning("  macOS:   pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz")
    
    def _get_active_window_info(self) -> Dict[str, Any]:
        """Always returns None (no window tracking)"""
        return None
    
    def start(self):
        """No-op start (window tracking disabled)"""
        self.is_running = True
        logger.info("FallbackWindowCollector started (window tracking disabled)")
    
    def stop(self):
        """No-op stop"""
        self.is_running = False
        logger.info("FallbackWindowCollector stopped")
    
    def get_events(self, clear: bool = False) -> List[Dict[str, Any]]:
        """Always returns empty list"""
        return []
    
    def get_events_in_window(self, window_seconds: int) -> List[Dict[str, Any]]:
        """Always returns empty list"""
        return []
    
    def clear_buffer(self):
        """No-op clear"""
        pass
