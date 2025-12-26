"""
Keyboard event collector using pynput
Captures all keyboard events with timestamps and metadata
"""

from pynput import keyboard
from datetime import datetime
from collections import deque
from typing import List, Dict, Any
import threading
import time

from ..utils.logger import setup_logger
from ..utils.config import KEYBOARD_BUFFER_SIZE, LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class KeyboardCollector:
    """Collects keyboard events in real-time"""
    
    def __init__(self, buffer_size: int = KEYBOARD_BUFFER_SIZE):
        """
        Initialize keyboard collector
        
        Args:
            buffer_size: Maximum number of events to store in buffer
        """
        self.buffer_size = buffer_size
        self.events = deque(maxlen=buffer_size)
        self.listener = None
        self.is_running = False
        self.lock = threading.Lock()
        
        logger.info(f"KeyboardCollector initialized with buffer size: {buffer_size}")
    
    def _on_press(self, key):
        """Callback for key press events"""
        try:
            # Get key name
            try:
                key_name = key.char
            except AttributeError:
                key_name = str(key)
            
            event = {
                'timestamp': datetime.now(),
                'event_type': 'key_press',
                'key': key_name,
                'is_special': hasattr(key, 'name'),  # Special keys like Ctrl, Alt, etc.
            }
            
            with self.lock:
                self.events.append(event)
                
        except Exception as e:
            logger.error(f"Error in key press handler: {e}")
    
    def _on_release(self, key):
        """Callback for key release events"""
        try:
            # Get key name
            try:
                key_name = key.char
            except AttributeError:
                key_name = str(key)
            
            event = {
                'timestamp': datetime.now(),
                'event_type': 'key_release',
                'key': key_name,
                'is_special': hasattr(key, 'name'),
            }
            
            with self.lock:
                self.events.append(event)
                
        except Exception as e:
            logger.error(f"Error in key release handler: {e}")
    
    def start(self):
        """Start collecting keyboard events"""
        if self.is_running:
            logger.warning("KeyboardCollector is already running")
            return
        
        self.is_running = True
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release
        )
        self.listener.start()
        logger.info("KeyboardCollector started")
    
    def stop(self):
        """Stop collecting keyboard events"""
        if not self.is_running:
            logger.warning("KeyboardCollector is not running")
            return
        
        self.is_running = False
        if self.listener:
            self.listener.stop()
        logger.info("KeyboardCollector stopped")
    
    def get_events(self, clear: bool = False) -> List[Dict[str, Any]]:
        """
        Get collected events
        
        Args:
            clear: If True, clear the buffer after retrieving events
        
        Returns:
            List of event dictionaries
        """
        with self.lock:
            events = list(self.events)
            if clear:
                self.events.clear()
        
        return events
    
    def get_events_in_window(self, window_seconds: int) -> List[Dict[str, Any]]:
        """
        Get events within a time window
        
        Args:
            window_seconds: Time window in seconds
        
        Returns:
            List of events within the time window
        """
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
        logger.debug("Keyboard event buffer cleared")


# Standalone test
if __name__ == "__main__":
    print("Testing KeyboardCollector...")
    print("Press some keys (Ctrl+C to stop)")
    
    collector = KeyboardCollector()
    collector.start()
    
    try:
        while True:
            time.sleep(5)
            events = collector.get_events()
            print(f"\nCollected {len(events)} events in last 5 seconds")
            if events:
                print(f"Last event: {events[-1]}")
    except KeyboardInterrupt:
        print("\nStopping collector...")
        collector.stop()
        print(f"Total events collected: {len(collector.get_events())}")
