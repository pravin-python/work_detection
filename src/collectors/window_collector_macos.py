"""
macOS-specific window collector implementation
Uses pyobjc for macOS window tracking
"""

import time
from datetime import datetime
from collections import deque
from typing import List, Dict, Any
import threading

try:
    from AppKit import NSWorkspace
    from Quartz import (
        CGWindowListCopyWindowInfo,
        kCGWindowListOptionOnScreenOnly,
        kCGNullWindowID
    )
    import psutil
    MACOS_LIBS_AVAILABLE = True
except ImportError:
    MACOS_LIBS_AVAILABLE = False

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class MacOSWindowCollector:
    """macOS-specific window tracking implementation"""
    
    def __init__(self, poll_interval: float = 1.0, buffer_size: int = 1000):
        """
        Initialize macOS window collector
        
        Args:
            poll_interval: How often to check active window (seconds)
            buffer_size: Maximum number of events to store
        """
        if not MACOS_LIBS_AVAILABLE:
            raise ImportError("macOS-specific libraries (pyobjc) not available")
        
        self.poll_interval = poll_interval
        self.buffer_size = buffer_size
        self.events = deque(maxlen=buffer_size)
        self.is_running = False
        self.lock = threading.Lock()
        self.thread = None
        self.last_window = None
        self.workspace = NSWorkspace.sharedWorkspace()
        
        logger.info(f"MacOSWindowCollector initialized (poll interval: {poll_interval}s)")
    
    def _get_active_window_info(self) -> Dict[str, Any]:
        """Get information about the currently active window"""
        try:
            # Get active application
            active_app = self.workspace.activeApplication()
            
            if not active_app:
                return None
            
            # Get application name
            app_name = active_app.get('NSApplicationName', 'Unknown')
            
            # Get process ID
            pid = active_app.get('NSApplicationProcessIdentifier', 0)
            
            # Get process executable using psutil
            try:
                process = psutil.Process(pid)
                process_exe = process.exe()
                process_name = process.name()
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                process_exe = "Unknown"
                process_name = app_name
            
            # Try to get window title from window list
            window_title = app_name  # Default to app name
            try:
                window_list = CGWindowListCopyWindowInfo(
                    kCGWindowListOptionOnScreenOnly,
                    kCGNullWindowID
                )
                
                for window in window_list:
                    if window.get('kCGWindowOwnerPID') == pid:
                        title = window.get('kCGWindowName', '')
                        if title:
                            window_title = title
                            break
            except:
                pass  # Use app name as fallback
            
            return {
                'window_title': window_title,
                'process_name': process_name,
                'process_exe': process_exe,
                'pid': pid,
            }
        except Exception as e:
            logger.error(f"Error getting active window info: {e}")
            return None
    
    def _poll_loop(self):
        """Background thread that polls for active window changes"""
        logger.info("Window polling started (macOS)")
        
        while self.is_running:
            try:
                window_info = self._get_active_window_info()
                
                if window_info:
                    # Check if window changed
                    current_window = (
                        window_info['window_title'],
                        window_info['process_name']
                    )
                    
                    if current_window != self.last_window:
                        event = {
                            'timestamp': datetime.now(),
                            'event_type': 'window_change',
                            **window_info
                        }
                        
                        with self.lock:
                            self.events.append(event)
                        
                        self.last_window = current_window
                        logger.debug(f"Window changed to: {window_info['window_title']}")
                
                time.sleep(self.poll_interval)
                
            except Exception as e:
                logger.error(f"Error in window poll loop: {e}")
                time.sleep(self.poll_interval)
    
    def start(self):
        """Start tracking window changes"""
        if self.is_running:
            logger.warning("MacOSWindowCollector is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info("MacOSWindowCollector started")
    
    def stop(self):
        """Stop tracking window changes"""
        if not self.is_running:
            logger.warning("MacOSWindowCollector is not running")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("MacOSWindowCollector stopped")
    
    def get_events(self, clear: bool = False) -> List[Dict[str, Any]]:
        """Get collected events"""
        with self.lock:
            events = list(self.events)
            if clear:
                self.events.clear()
        return events
    
    def get_events_in_window(self, window_seconds: int) -> List[Dict[str, Any]]:
        """Get events within a time window"""
        now = datetime.now()
        with self.lock:
            events = [
                event for event in self.events
                if (now - event['timestamp']).total_seconds() <= window_seconds
            ]
        return events
    
    def clear_buffer(self):
        """Clear the event buffer"""
        with self.lock:
            self.events.clear()
        logger.debug("Window event buffer cleared")
