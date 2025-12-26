"""
Linux-specific window collector implementation
Uses python-xlib for X11 window tracking
"""

import time
from datetime import datetime
from collections import deque
from typing import List, Dict, Any
import threading

try:
    from Xlib import display, X, error
    import psutil
    LINUX_LIBS_AVAILABLE = True
except ImportError:
    LINUX_LIBS_AVAILABLE = False

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class LinuxWindowCollector:
    """Linux-specific window tracking implementation (X11)"""
    
    def __init__(self, poll_interval: float = 1.0, buffer_size: int = 1000):
        """
        Initialize Linux window collector
        
        Args:
            poll_interval: How often to check active window (seconds)
            buffer_size: Maximum number of events to store
        """
        if not LINUX_LIBS_AVAILABLE:
            raise ImportError("Linux-specific libraries (python-xlib, psutil) not available")
        
        self.poll_interval = poll_interval
        self.buffer_size = buffer_size
        self.events = deque(maxlen=buffer_size)
        self.is_running = False
        self.lock = threading.Lock()
        self.thread = None
        self.last_window = None
        
        try:
            self.display = display.Display()
            logger.info(f"LinuxWindowCollector initialized (poll interval: {poll_interval}s)")
        except Exception as e:
            logger.error(f"Failed to connect to X11 display: {e}")
            raise
    
    def _get_active_window_info(self) -> Dict[str, Any]:
        """Get information about the currently active window"""
        try:
            # Get the root window
            root = self.display.screen().root
            
            # Get the active window
            NET_ACTIVE_WINDOW = self.display.intern_atom('_NET_ACTIVE_WINDOW')
            active_window_id = root.get_full_property(NET_ACTIVE_WINDOW, X.AnyPropertyType)
            
            if not active_window_id:
                return None
            
            window_id = active_window_id.value[0]
            window = self.display.create_resource_object('window', window_id)
            
            # Get window title
            try:
                window_name = window.get_wm_name() or "Unknown"
            except:
                window_name = "Unknown"
            
            # Get window class (application name)
            try:
                wm_class = window.get_wm_class()
                if wm_class:
                    process_name = wm_class[1] if len(wm_class) > 1 else wm_class[0]
                else:
                    process_name = "Unknown"
            except:
                process_name = "Unknown"
            
            # Get PID
            try:
                NET_WM_PID = self.display.intern_atom('_NET_WM_PID')
                pid_property = window.get_full_property(NET_WM_PID, X.AnyPropertyType)
                if pid_property:
                    pid = pid_property.value[0]
                    
                    # Get process executable using psutil
                    try:
                        process = psutil.Process(pid)
                        process_exe = process.exe()
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        process_exe = "Unknown"
                else:
                    pid = 0
                    process_exe = "Unknown"
            except:
                pid = 0
                process_exe = "Unknown"
            
            return {
                'window_title': window_name,
                'process_name': process_name,
                'process_exe': process_exe,
                'pid': pid,
            }
        except error.XError as e:
            logger.debug(f"X11 error getting window info: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting active window info: {e}")
            return None
    
    def _poll_loop(self):
        """Background thread that polls for active window changes"""
        logger.info("Window polling started (Linux/X11)")
        
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
            logger.warning("LinuxWindowCollector is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._poll_loop, daemon=True)
        self.thread.start()
        logger.info("LinuxWindowCollector started")
    
    def stop(self):
        """Stop tracking window changes"""
        if not self.is_running:
            logger.warning("LinuxWindowCollector is not running")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("LinuxWindowCollector stopped")
    
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
