"""
Keyboard feature extraction
Extracts behavioral features from keyboard events
"""

import numpy as np
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class KeyboardFeatureExtractor:
    """Extract features from keyboard events"""
    
    # Common shortcuts to detect
    SHORTCUTS = {
        'Key.ctrl_l+z', 'Key.ctrl_r+z',  # Undo
        'Key.ctrl_l+c', 'Key.ctrl_r+c',  # Copy
        'Key.ctrl_l+v', 'Key.ctrl_r+v',  # Paste
        'Key.ctrl_l+x', 'Key.ctrl_r+x',  # Cut
        'Key.ctrl_l+a', 'Key.ctrl_r+a',  # Select all
        'Key.alt_l+Key.tab', 'Key.alt_r+Key.tab',  # Alt+Tab
    }
    
    def __init__(self):
        logger.debug("KeyboardFeatureExtractor initialized")
    
    def extract(self, events: List[Dict[str, Any]], window_seconds: int = 60) -> Dict[str, float]:
        """
        Extract keyboard features from events
        
        Args:
            events: List of keyboard events
            window_seconds: Time window for rate calculations
        
        Returns:
            Dictionary of features
        """
        if not events:
            return self._get_empty_features()
        
        # Filter only key press events
        press_events = [e for e in events if e['event_type'] == 'key_press']
        
        if not press_events:
            return self._get_empty_features()
        
        # Extract features
        features = {}
        
        # 1. Keys per minute
        features['keys_per_minute'] = len(press_events) / (window_seconds / 60.0)
        
        # 2. Unique key ratio
        keys = [e['key'] for e in press_events]
        unique_keys = len(set(keys))
        features['unique_key_ratio'] = unique_keys / max(len(keys), 1)
        
        # 3. Repeat key ratio
        key_counts = Counter(keys)
        max_repeats = max(key_counts.values()) if key_counts else 0
        features['repeat_key_ratio'] = max_repeats / max(len(keys), 1)
        
        # 4. Max consecutive repeats
        features['max_consecutive_repeats'] = self._max_consecutive_repeats(keys)
        
        # 5. Inter-key delay statistics
        inter_key_delays = self._calculate_inter_key_delays(press_events)
        if inter_key_delays:
            features['avg_inter_key_delay'] = np.mean(inter_key_delays)
            features['std_inter_key_delay'] = np.std(inter_key_delays)
        else:
            features['avg_inter_key_delay'] = 0.0
            features['std_inter_key_delay'] = 0.0
        
        # 6. Keystroke entropy
        features['keystroke_entropy'] = self._calculate_entropy(keys)
        
        # 7. Shortcut abuse score
        features['shortcut_abuse_score'] = self._calculate_shortcut_abuse(press_events)
        
        # 8. Burst typing score
        features['burst_typing_score'] = self._calculate_burst_score(inter_key_delays)
        
        return features
    
    def _get_empty_features(self) -> Dict[str, float]:
        """Return zero features when no events"""
        return {
            'keys_per_minute': 0.0,
            'unique_key_ratio': 0.0,
            'repeat_key_ratio': 0.0,
            'max_consecutive_repeats': 0.0,
            'avg_inter_key_delay': 0.0,
            'std_inter_key_delay': 0.0,
            'keystroke_entropy': 0.0,
            'shortcut_abuse_score': 0.0,
            'burst_typing_score': 0.0,
        }
    
    def _max_consecutive_repeats(self, keys: List[str]) -> int:
        """Calculate maximum consecutive repeats of the same key"""
        if not keys:
            return 0
        
        max_count = 1
        current_count = 1
        
        for i in range(1, len(keys)):
            if keys[i] == keys[i-1]:
                current_count += 1
                max_count = max(max_count, current_count)
            else:
                current_count = 1
        
        return max_count
    
    def _calculate_inter_key_delays(self, events: List[Dict[str, Any]]) -> List[float]:
        """Calculate time delays between consecutive key presses"""
        if len(events) < 2:
            return []
        
        delays = []
        for i in range(1, len(events)):
            delay = (events[i]['timestamp'] - events[i-1]['timestamp']).total_seconds()
            delays.append(delay)
        
        return delays
    
    def _calculate_entropy(self, keys: List[str]) -> float:
        """Calculate Shannon entropy of key distribution"""
        if not keys:
            return 0.0
        
        key_counts = Counter(keys)
        total = len(keys)
        
        entropy = 0.0
        for count in key_counts.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        # Normalize to 0-1 range (max entropy for uniform distribution)
        max_entropy = np.log2(len(key_counts)) if len(key_counts) > 1 else 1.0
        normalized_entropy = entropy / max(max_entropy, 1.0)
        
        return normalized_entropy
    
    def _calculate_shortcut_abuse(self, events: List[Dict[str, Any]]) -> float:
        """Calculate shortcut abuse score (0-1)"""
        if not events:
            return 0.0
        
        # Simple heuristic: count Ctrl, Alt, and common shortcuts
        shortcut_indicators = ['Key.ctrl_l', 'Key.ctrl_r', 'Key.alt_l', 'Key.alt_r']
        shortcut_count = sum(1 for e in events if any(ind in str(e['key']) for ind in shortcut_indicators))
        
        return min(shortcut_count / max(len(events), 1), 1.0)
    
    def _calculate_burst_score(self, delays: List[float]) -> float:
        """
        Calculate burst typing score
        High score = natural typing with bursts
        Low score = constant mechanical typing
        """
        if not delays or len(delays) < 3:
            return 0.5  # Neutral score
        
        # Calculate coefficient of variation (CV)
        mean_delay = np.mean(delays)
        std_delay = np.std(delays)
        
        if mean_delay == 0:
            return 0.0
        
        cv = std_delay / mean_delay
        
        # Normalize: higher CV = more natural (bursts and pauses)
        # Typical human CV is around 0.3-0.8
        # Bot CV is very low (< 0.1)
        normalized_score = min(cv / 0.8, 1.0)
        
        return normalized_score


# Standalone test
if __name__ == "__main__":
    # Test with sample events
    sample_events = [
        {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'a'},
        {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'b'},
        {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'c'},
        {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'a'},
        {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'a'},
    ]
    
    extractor = KeyboardFeatureExtractor()
    features = extractor.extract(sample_events, window_seconds=60)
    
    print("Keyboard Features:")
    for key, value in features.items():
        print(f"  {key}: {value:.4f}")
