"""
Cross-platform window/application tracker
Automatically selects the appropriate platform-specific implementation
"""

import platform
from typing import List, Dict, Any

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class WindowCollector:
    """
    Cross-platform window tracking with automatic platform detection
    
    Supports:
    - Windows (pywin32 + psutil)
    - Linux/X11 (python-xlib + psutil)
    - macOS (pyobjc + psutil)
    - Fallback (disabled window tracking)
    """
    
    def __init__(self, poll_interval: float = 1.0, buffer_size: int = 1000):
        """
        Initialize window collector with platform-specific implementation
        
        Args:
            poll_interval: How often to check active window (seconds)
            buffer_size: Maximum number of events to store
        """
        self.platform = platform.system()
        self._impl = None
        
        logger.info(f"Detected platform: {self.platform}")
        
        # Try to load platform-specific implementation
        if self.platform == "Windows":
            self._impl = self._load_windows_collector(poll_interval, buffer_size)
        elif self.platform == "Linux":
            self._impl = self._load_linux_collector(poll_interval, buffer_size)
        elif self.platform == "Darwin":  # macOS
            self._impl = self._load_macos_collector(poll_interval, buffer_size)
        else:
            logger.warning(f"Unsupported platform: {self.platform}")
            self._impl = self._load_fallback_collector(poll_interval, buffer_size)
        
        # If platform-specific implementation failed, use fallback
        if self._impl is None:
            self._impl = self._load_fallback_collector(poll_interval, buffer_size)
    
    def _load_windows_collector(self, poll_interval, buffer_size):
        """Load Windows-specific collector"""
        try:
            from .window_collector_windows import WindowsWindowCollector
            logger.info("Using Windows window collector")
            return WindowsWindowCollector(poll_interval, buffer_size)
        except ImportError as e:
            logger.warning(f"Failed to load Windows collector: {e}")
            logger.warning("Install: pip install pywin32")
            return None
        except Exception as e:
            logger.error(f"Error initializing Windows collector: {e}")
            return None
    
    def _load_linux_collector(self, poll_interval, buffer_size):
        """Load Linux-specific collector"""
        try:
            from .window_collector_linux import LinuxWindowCollector
            logger.info("Using Linux/X11 window collector")
            return LinuxWindowCollector(poll_interval, buffer_size)
        except ImportError as e:
            logger.warning(f"Failed to load Linux collector: {e}")
            logger.warning("Install: pip install python-xlib")
            return None
        except Exception as e:
            logger.error(f"Error initializing Linux collector: {e}")
            logger.error("Note: Window tracking requires X11 (not supported on Wayland)")
            return None
    
    def _load_macos_collector(self, poll_interval, buffer_size):
        """Load macOS-specific collector"""
        try:
            from .window_collector_macos import MacOSWindowCollector
            logger.info("Using macOS window collector")
            return MacOSWindowCollector(poll_interval, buffer_size)
        except ImportError as e:
            logger.warning(f"Failed to load macOS collector: {e}")
            logger.warning("Install: pip install pyobjc-framework-Cocoa pyobjc-framework-Quartz")
            return None
        except Exception as e:
            logger.error(f"Error initializing macOS collector: {e}")
            logger.error("Note: You may need to grant accessibility permissions")
            return None
    
    def _load_fallback_collector(self, poll_interval, buffer_size):
        """Load fallback collector (window tracking disabled)"""
        from .window_collector_fallback import FallbackWindowCollector
        logger.info("Using fallback collector (window tracking disabled)")
        return FallbackWindowCollector(poll_interval, buffer_size)
    
    # Delegate all methods to the implementation
    
    def start(self):
        """Start tracking window changes"""
        return self._impl.start()
    
    def stop(self):
        """Stop tracking window changes"""
        return self._impl.stop()
    
    def get_events(self, clear: bool = False) -> List[Dict[str, Any]]:
        """Get collected events"""
        return self._impl.get_events(clear)
    
    def get_events_in_window(self, window_seconds: int) -> List[Dict[str, Any]]:
        """Get events within a time window"""
        return self._impl.get_events_in_window(window_seconds)
    
    def clear_buffer(self):
        """Clear the event buffer"""
        return self._impl.clear_buffer()
    
    @property
    def is_running(self):
        """Check if collector is running"""
        return self._impl.is_running
    
    @property
    def platform_name(self):
        """Get platform name"""
        return self.platform
    
    @property
    def is_fallback(self):
        """Check if using fallback (window tracking disabled)"""
        from .window_collector_fallback import FallbackWindowCollector
        return isinstance(self._impl, FallbackWindowCollector)


# Standalone test
if __name__ == "__main__":
    import time
    
    print(f"Testing WindowCollector on {platform.system()}...")
    print("Switch between windows (Ctrl+C to stop)")
    
    collector = WindowCollector(poll_interval=0.5)
    
    if collector.is_fallback:
        print("\n⚠️  WARNING: Window tracking is disabled (fallback mode)")
        print("Install platform-specific libraries to enable window tracking")
    else:
        print(f"\n✅ Using platform-specific collector for {collector.platform_name}")
    
    collector.start()
    
    try:
        while True:
            time.sleep(5)
            events = collector.get_events()
            print(f"\nCollected {len(events)} window changes")
            if events:
                print(f"Last window: {events[-1].get('window_title', 'N/A')}")
    except KeyboardInterrupt:
        print("\nStopping collector...")
        collector.stop()
        print(f"Total window changes: {len(collector.get_events())}")
