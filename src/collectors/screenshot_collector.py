"""
Cross-platform screenshot collector
Captures screenshots at regular intervals with rolling buffer
"""

import time
import threading
from datetime import datetime
from collections import deque
from typing import List, Dict, Any, Optional
from pathlib import Path

try:
    import mss
    from PIL import Image
    MSS_AVAILABLE = True
except ImportError:
    MSS_AVAILABLE = False

from ..utils.logger import setup_logger
from ..utils.config import (
    LOG_LEVEL, LOG_FILE, 
    SCREENSHOT_INTERVAL_SECONDS,
    SCREENSHOT_BUFFER_SIZE,
    SCREENSHOT_QUALITY,
    ENABLE_SCREENSHOTS
)

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class ScreenshotCollector:
    """
    Cross-platform screenshot collector with rolling buffer
    
    Features:
    - Captures screenshots at regular intervals (default: 60 seconds)
    - Maintains rolling buffer of last N screenshots
    - Cross-platform support (Windows/Linux/macOS)
    - Automatic cleanup of old screenshots
    - Privacy-safe (can be disabled)
    """
    
    def __init__(
        self, 
        interval: int = SCREENSHOT_INTERVAL_SECONDS,
        buffer_size: int = SCREENSHOT_BUFFER_SIZE,
        quality: int = SCREENSHOT_QUALITY,
        enabled: bool = ENABLE_SCREENSHOTS,
        random_interval: bool = True,
        min_interval: int = 30,
        max_interval: int = 90
    ):
        """
        Initialize screenshot collector
        
        Args:
            interval: Base seconds between screenshots (default: 60)
            buffer_size: Number of screenshots to keep in buffer (default: 10)
            quality: JPEG quality for compression (1-100, default: 85)
            enabled: Whether screenshot capture is enabled
            random_interval: Use random intervals instead of fixed (default: True)
            min_interval: Minimum seconds between screenshots (default: 30)
            max_interval: Maximum seconds between screenshots (default: 90)
        """
        self.interval = interval
        self.buffer_size = buffer_size
        self.quality = quality
        self.enabled = enabled
        self.random_interval = random_interval
        self.min_interval = min_interval
        self.max_interval = max_interval
        
        self.screenshots = deque(maxlen=buffer_size)
        self.is_running = False
        self.lock = threading.Lock()
        self.thread = None
        
        if not MSS_AVAILABLE:
            logger.warning("mss library not available - screenshot capture disabled")
            logger.warning("Install: pip install mss Pillow")
            self.enabled = False
        
        if not self.enabled:
            logger.info("Screenshot capture is DISABLED")
        else:
            # Don't create mss instance here - create it in the thread to avoid threading issues
            logger.info(f"ScreenshotCollector initialized (interval: {interval}s, buffer: {buffer_size})")
    
    def capture_screenshot(self, sct_instance=None) -> Optional[Dict[str, Any]]:
        """
        Capture current screen
        
        Args:
            sct_instance: Optional mss instance (creates new one if None)
        
        Returns:
            Dictionary with timestamp, image, and metadata
            None if capture fails or disabled
        """
        if not self.enabled:
            return None
        
        try:
            # Create mss instance if not provided (for thread safety)
            if sct_instance is None:
                sct_instance = mss.mss()
            
            # Capture primary monitor
            monitor = sct_instance.monitors[1]  # Monitor 1 is primary
            screenshot = sct_instance.grab(monitor)
            
            # Convert to PIL Image
            img = Image.frombytes('RGB', screenshot.size, screenshot.rgb)
            
            return {
                'timestamp': datetime.now(),
                'image': img,
                'width': screenshot.width,
                'height': screenshot.height,
                'monitor': 1
            }
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None
    
    def _capture_loop(self):
        """Background thread that captures screenshots periodically"""
        if self.random_interval:
            logger.info(f"Screenshot capture started (random interval: {self.min_interval}-{self.max_interval}s)")
        else:
            logger.info(f"Screenshot capture started (interval: {self.interval}s)")
        
        import random
        
        # Create mss instance in this thread to avoid threading issues
        try:
            sct = mss.mss()
        except Exception as e:
            logger.error(f"Failed to create mss instance in thread: {e}")
            self.enabled = False
            return
        
        while self.is_running:
            try:
                # Pass the thread-local mss instance
                screenshot = self.capture_screenshot(sct_instance=sct)
                
                if screenshot:
                    with self.lock:
                        self.screenshots.append(screenshot)
                    logger.debug(f"Screenshot captured ({len(self.screenshots)}/{self.buffer_size} in buffer)")
                
                # Calculate next interval (random or fixed)
                if self.random_interval:
                    next_interval = random.uniform(self.min_interval, self.max_interval)
                    logger.debug(f"Next screenshot in {next_interval:.1f}s (random)")
                else:
                    next_interval = self.interval
                
                # Wait for next interval
                time.sleep(next_interval)
                
            except Exception as e:
                logger.error(f"Error in screenshot capture loop: {e}")
                # Use fixed interval on error
                time.sleep(self.interval)
    
    def start(self):
        """Start periodic screenshot capture"""
        if not self.enabled:
            logger.info("Screenshot capture is disabled - not starting")
            return
        
        if self.is_running:
            logger.warning("ScreenshotCollector is already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        logger.info("ScreenshotCollector started")
    
    def stop(self):
        """Stop screenshot capture"""
        if not self.is_running:
            logger.warning("ScreenshotCollector is not running")
            return
        
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=2.0)
        logger.info("ScreenshotCollector stopped")
    
    def get_screenshots(self, count: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get screenshots from buffer
        
        Args:
            count: Number of recent screenshots to return (None = all)
        
        Returns:
            List of screenshot dictionaries
        """
        with self.lock:
            if count is None:
                return list(self.screenshots)
            else:
                return list(self.screenshots)[-count:]
    
    def get_latest_screenshot(self) -> Optional[Dict[str, Any]]:
        """Get most recent screenshot"""
        with self.lock:
            if self.screenshots:
                return self.screenshots[-1]
            return None
    
    def get_screenshot_pair(self, index1: int = -2, index2: int = -1) -> tuple:
        """
        Get a pair of screenshots for comparison
        
        Args:
            index1: Index of first screenshot (default: -2, second-to-last)
            index2: Index of second screenshot (default: -1, last)
        
        Returns:
            Tuple of (screenshot1, screenshot2) or (None, None) if not available
        """
        with self.lock:
            if len(self.screenshots) < 2:
                return (None, None)
            
            try:
                return (self.screenshots[index1], self.screenshots[index2])
            except IndexError:
                return (None, None)
    
    def clear_buffer(self):
        """Clear all screenshots from buffer"""
        with self.lock:
            self.screenshots.clear()
        logger.debug("Screenshot buffer cleared")
    
    def save_screenshot(self, screenshot: Dict[str, Any], filepath: Path):
        """
        Save screenshot to file
        
        Args:
            screenshot: Screenshot dictionary
            filepath: Path to save image
        """
        try:
            img = screenshot['image']
            img.save(filepath, 'JPEG', quality=self.quality)
            logger.debug(f"Screenshot saved to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save screenshot: {e}")
    
    @property
    def buffer_count(self) -> int:
        """Get current number of screenshots in buffer"""
        with self.lock:
            return len(self.screenshots)
    
    @property
    def is_enabled(self) -> bool:
        """Check if screenshot capture is enabled"""
        return self.enabled


# Standalone test
if __name__ == "__main__":
    import sys
    
    print("Testing ScreenshotCollector...")
    print("Press Ctrl+C to stop\n")
    
    collector = ScreenshotCollector(interval=5, buffer_size=5)  # 5 seconds for testing
    
    if not collector.is_enabled:
        print("❌ Screenshot capture is disabled")
        print("Install dependencies: pip install mss Pillow")
        sys.exit(1)
    
    collector.start()
    
    try:
        while True:
            time.sleep(10)
            count = collector.buffer_count
            print(f"Screenshots in buffer: {count}/5")
            
            if count > 0:
                latest = collector.get_latest_screenshot()
                print(f"Latest: {latest['timestamp']} ({latest['width']}x{latest['height']})")
    
    except KeyboardInterrupt:
        print("\nStopping collector...")
        collector.stop()
        print(f"Total screenshots captured: {collector.buffer_count}")
