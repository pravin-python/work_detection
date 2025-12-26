"""
Unified collector that combines keyboard, mouse, and window tracking
Provides a single interface for all data collection
"""

import time
from datetime import datetime
from typing import Dict, Any, List
import json
from pathlib import Path

from .keyboard_collector import KeyboardCollector
from .mouse_collector import MouseCollector
from .window_collector import WindowCollector
from ..utils.logger import setup_logger
from ..utils.config import (
    LOG_LEVEL, LOG_FILE, COLLECTION_WINDOW_SECONDS,
    RAW_DATA_DIR
)

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class UnifiedCollector:
    """Unified interface for all data collection"""
    
    def __init__(self):
        """Initialize all collectors"""
        self.keyboard_collector = KeyboardCollector()
        self.mouse_collector = MouseCollector()
        self.window_collector = WindowCollector()
        self.start_time = None
        
        logger.info("UnifiedCollector initialized")
    
    def start(self):
        """Start all collectors"""
        logger.info("Starting all collectors...")
        self.keyboard_collector.start()
        self.mouse_collector.start()
        self.window_collector.start()
        self.start_time = datetime.now()
        logger.info("All collectors started successfully")
    
    def stop(self):
        """Stop all collectors"""
        logger.info("Stopping all collectors...")
        self.keyboard_collector.stop()
        self.mouse_collector.stop()
        self.window_collector.stop()
        logger.info("All collectors stopped successfully")
    
    def get_all_events(self, window_seconds: int = None, clear: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get events from all collectors
        
        Args:
            window_seconds: Time window in seconds (None = all events)
            clear: If True, clear buffers after retrieving
        
        Returns:
            Dictionary with events from each collector
        """
        if window_seconds:
            keyboard_events = self.keyboard_collector.get_events_in_window(window_seconds)
            mouse_events = self.mouse_collector.get_events_in_window(window_seconds)
            window_events = self.window_collector.get_events_in_window(window_seconds)
        else:
            keyboard_events = self.keyboard_collector.get_events(clear=clear)
            mouse_events = self.mouse_collector.get_events(clear=clear)
            window_events = self.window_collector.get_events(clear=clear)
        
        return {
            'keyboard': keyboard_events,
            'mouse': mouse_events,
            'window': window_events,
            'metadata': {
                'collection_start': self.start_time.isoformat() if self.start_time else None,
                'retrieval_time': datetime.now().isoformat(),
                'window_seconds': window_seconds,
            }
        }
    
    def save_events_to_file(self, filepath: Path = None, window_seconds: int = None):
        """
        Save collected events to a JSON file
        
        Args:
            filepath: Path to save file (auto-generated if None)
            window_seconds: Time window in seconds (None = all events)
        """
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = RAW_DATA_DIR / f"events_{timestamp}.json"
        
        events = self.get_all_events(window_seconds=window_seconds)
        
        # Convert datetime objects to strings for JSON serialization
        def datetime_converter(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
        
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(events, f, indent=2, default=datetime_converter)
        
        logger.info(f"Events saved to {filepath}")
        return filepath
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of collected events
        
        Returns:
            Summary statistics
        """
        keyboard_events = self.keyboard_collector.get_events()
        mouse_events = self.mouse_collector.get_events()
        window_events = self.window_collector.get_events()
        
        runtime = (datetime.now() - self.start_time).total_seconds() if self.start_time else 0
        
        return {
            'runtime_seconds': runtime,
            'keyboard_events': len(keyboard_events),
            'mouse_events': len(mouse_events),
            'window_events': len(window_events),
            'total_events': len(keyboard_events) + len(mouse_events) + len(window_events),
            'events_per_second': (len(keyboard_events) + len(mouse_events) + len(window_events)) / max(runtime, 1),
        }
    
    def clear_all_buffers(self):
        """Clear all event buffers"""
        self.keyboard_collector.clear_buffer()
        self.mouse_collector.clear_buffer()
        self.window_collector.clear_buffer()
        logger.info("All buffers cleared")


# Standalone test
if __name__ == "__main__":
    print("Testing UnifiedCollector...")
    print("Perform various actions (keyboard, mouse, window switching)")
    print("Collection will run for 30 seconds...")
    
    collector = UnifiedCollector()
    collector.start()
    
    try:
        # Collect for 30 seconds
        for i in range(6):
            time.sleep(5)
            summary = collector.get_summary()
            print(f"\n[{i*5+5}s] Summary: {summary['total_events']} total events")
            print(f"  Keyboard: {summary['keyboard_events']}, Mouse: {summary['mouse_events']}, Window: {summary['window_events']}")
        
        # Save to file
        print("\nSaving events to file...")
        filepath = collector.save_events_to_file()
        print(f"Saved to: {filepath}")
        
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    finally:
        collector.stop()
        final_summary = collector.get_summary()
        print(f"\nFinal Summary:")
        print(f"  Runtime: {final_summary['runtime_seconds']:.1f}s")
        print(f"  Total Events: {final_summary['total_events']}")
        print(f"  Events/sec: {final_summary['events_per_second']:.2f}")
