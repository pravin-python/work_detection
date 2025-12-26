"""
Mouse event collector using pynput
Captures mouse movements, clicks, and scrolls with timestamps
"""

from pynput import mouse
from datetime import datetime
from collections import deque
from typing import List, Dict, Any
import threading
import time
import math

from ..utils.logger import setup_logger
from ..utils.config import MOUSE_BUFFER_SIZE, LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class MouseCollector:
    """Collects mouse events in real-time"""
    
    def __init__(self, buffer_size: int = MOUSE_BUFFER_SIZE):
        """
        Initialize mouse collector
        
        Args:
            buffer_size: Maximum number of events to store in buffer
        """
        self.buffer_size = buffer_size
        self.events = deque(maxlen=buffer_size)
        self.listener = None
        self.is_running = False
        self.lock = threading.Lock()
        self.last_position = None
        
        logger.info(f"MouseCollector initialized with buffer size: {buffer_size}")
    
    def _on_move(self, x, y):
        """Callback for mouse move events"""
        try:
            # Calculate distance from last position
            distance = 0
            if self.last_position:
                dx = x - self.last_position[0]
                dy = y - self.last_position[1]
                distance = math.sqrt(dx**2 + dy**2)
            
            event = {
                'timestamp': datetime.now(),
                'event_type': 'mouse_move',
                'x': x,
                'y': y,
                'distance': distance,
            }
            
            with self.lock:
                self.events.append(event)
            
            self.last_position = (x, y)
                
        except Exception as e:
            logger.error(f"Error in mouse move handler: {e}")
    
    def _on_click(self, x, y, button, pressed):
        """Callback for mouse click events"""
        try:
            event = {
                'timestamp': datetime.now(),
                'event_type': 'mouse_click',
                'x': x,
                'y': y,
                'button': str(button),
                'pressed': pressed,
            }
            
            with self.lock:
                self.events.append(event)
                
        except Exception as e:
            logger.error(f"Error in mouse click handler: {e}")
    
    def _on_scroll(self, x, y, dx, dy):
        """Callback for mouse scroll events"""
        try:
            event = {
                'timestamp': datetime.now(),
                'event_type': 'mouse_scroll',
                'x': x,
                'y': y,
                'dx': dx,
                'dy': dy,
            }
            
            with self.lock:
                self.events.append(event)
                
        except Exception as e:
            logger.error(f"Error in mouse scroll handler: {e}")
    
    def start(self):
        """Start collecting mouse events"""
        if self.is_running:
            logger.warning("MouseCollector is already running")
            return
        
        self.is_running = True
        self.listener = mouse.Listener(
            on_move=self._on_move,
            on_click=self._on_click,
            on_scroll=self._on_scroll
        )
        self.listener.start()
        logger.info("MouseCollector started")
    
    def stop(self):
        """Stop collecting mouse events"""
        if not self.is_running:
            logger.warning("MouseCollector is not running")
            return
        
        self.is_running = False
        if self.listener:
            self.listener.stop()
        logger.info("MouseCollector stopped")
    
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
        logger.debug("Mouse event buffer cleared")


# Standalone test
if __name__ == "__main__":
    print("Testing MouseCollector...")
    print("Move your mouse and click (Ctrl+C to stop)")
    
    collector = MouseCollector()
    collector.start()
    
    try:
        while True:
            time.sleep(5)
            events = collector.get_events()
            print(f"\nCollected {len(events)} events in last 5 seconds")
            if events:
                move_events = [e for e in events if e['event_type'] == 'mouse_move']
                click_events = [e for e in events if e['event_type'] == 'mouse_click']
                print(f"Moves: {len(move_events)}, Clicks: {len(click_events)}")
    except KeyboardInterrupt:
        print("\nStopping collector...")
        collector.stop()
        print(f"Total events collected: {len(collector.get_events())}")
