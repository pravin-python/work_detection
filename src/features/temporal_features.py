"""
Temporal and context feature extraction
"""

import numpy as np
from typing import List, Dict, Any
from datetime import datetime
from collections import Counter

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class TemporalFeatureExtractor:
    """Extract temporal and contextual features"""
    
    def __init__(self):
        logger.debug("TemporalFeatureExtractor initialized")
    
    def extract(self, all_events: Dict[str, List[Dict[str, Any]]], window_seconds: int = 60) -> Dict[str, float]:
        """
        Extract temporal features from all event types
        
        Args:
            all_events: Dictionary with 'keyboard', 'mouse', 'window' event lists
            window_seconds: Time window
        
        Returns:
            Dictionary of features
        """
        keyboard_events = all_events.get('keyboard', [])
        mouse_events = all_events.get('mouse', [])
        window_events = all_events.get('window', [])
        
        features = {}
        
        # 1. Idle and active time
        idle_active = self._calculate_idle_active_time(keyboard_events, mouse_events, window_seconds)
        features.update(idle_active)
        
        # 2. Activity spike detection
        features['activity_spike_score'] = self._detect_activity_spikes(keyboard_events, mouse_events, window_seconds)
        
        # 3. Periodic behavior detection
        features['periodic_behavior_score'] = self._detect_periodic_behavior(keyboard_events, mouse_events)
        
        # 4. Time since last activity
        features['time_since_last_activity'] = self._time_since_last_activity(keyboard_events, mouse_events)
        
        # 5. Window switching behavior
        window_features = self._extract_window_features(window_events, window_seconds)
        features.update(window_features)
        
        # 6. Combined input diversity
        features['input_diversity_score'] = self._calculate_input_diversity(keyboard_events, mouse_events)
        
        # 7. Overall entropy score
        features['overall_entropy_score'] = self._calculate_overall_entropy(all_events)
        
        return features
    
    def _calculate_idle_active_time(self, keyboard_events: List, mouse_events: List, window_seconds: int) -> Dict[str, float]:
        """Calculate idle and active time"""
        all_input_events = keyboard_events + [e for e in mouse_events if e['event_type'] != 'mouse_move' or e.get('distance', 0) > 10]
        
        if not all_input_events:
            return {
                'idle_seconds': window_seconds,
                'active_seconds': 0.0,
            }
        
        # Sort by timestamp
        all_input_events.sort(key=lambda x: x['timestamp'])
        
        # Calculate gaps
        idle_threshold = 5.0  # 5 seconds of no input = idle
        total_idle = 0.0
        
        for i in range(1, len(all_input_events)):
            gap = (all_input_events[i]['timestamp'] - all_input_events[i-1]['timestamp']).total_seconds()
            if gap > idle_threshold:
                total_idle += gap
        
        active_seconds = window_seconds - total_idle
        
        return {
            'idle_seconds': max(0.0, total_idle),
            'active_seconds': max(0.0, active_seconds),
        }
    
    def _detect_activity_spikes(self, keyboard_events: List, mouse_events: List, window_seconds: int) -> float:
        """
        Detect sudden activity spikes (common in idle timeout gaming)
        Returns score 0-1 (higher = more suspicious)
        """
        all_events = keyboard_events + mouse_events
        
        if len(all_events) < 10:
            return 0.0
        
        # Divide window into 10-second buckets
        bucket_size = 10
        num_buckets = int(window_seconds / bucket_size)
        
        if num_buckets < 2:
            return 0.0
        
        # Sort events by timestamp
        all_events.sort(key=lambda x: x['timestamp'])
        
        # Count events per bucket
        bucket_counts = [0] * num_buckets
        start_time = all_events[0]['timestamp']
        
        for event in all_events:
            elapsed = (event['timestamp'] - start_time).total_seconds()
            bucket_idx = min(int(elapsed / bucket_size), num_buckets - 1)
            bucket_counts[bucket_idx] += 1
        
        # Calculate coefficient of variation
        if np.mean(bucket_counts) == 0:
            return 0.0
        
        cv = np.std(bucket_counts) / np.mean(bucket_counts)
        
        # High CV indicates spiky behavior
        # Normalize: CV > 2.0 is very suspicious
        spike_score = min(cv / 2.0, 1.0)
        
        return spike_score
    
    def _detect_periodic_behavior(self, keyboard_events: List, mouse_events: List) -> float:
        """
        Detect periodic/repetitive behavior (bot-like)
        Returns score 0-1 (higher = more periodic/suspicious)
        """
        all_events = keyboard_events + mouse_events
        
        if len(all_events) < 10:
            return 0.0
        
        # Calculate inter-event intervals
        all_events.sort(key=lambda x: x['timestamp'])
        intervals = []
        
        for i in range(1, len(all_events)):
            interval = (all_events[i]['timestamp'] - all_events[i-1]['timestamp']).total_seconds()
            intervals.append(interval)
        
        if not intervals:
            return 0.0
        
        # Low standard deviation in intervals = periodic behavior
        mean_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        if mean_interval == 0:
            return 0.0
        
        cv = std_interval / mean_interval
        
        # Low CV = periodic (bot-like)
        # Human CV is typically > 0.5
        # Bot CV is < 0.2
        periodic_score = max(0.0, 1.0 - (cv / 0.5))
        
        return periodic_score
    
    def _time_since_last_activity(self, keyboard_events: List, mouse_events: List) -> float:
        """Calculate time since last significant activity"""
        all_events = keyboard_events + mouse_events
        
        if not all_events:
            return 999.0  # Large value
        
        # Get most recent event
        most_recent = max(all_events, key=lambda x: x['timestamp'])
        time_since = (datetime.now() - most_recent['timestamp']).total_seconds()
        
        return time_since
    
    def _extract_window_features(self, window_events: List, window_seconds: int) -> Dict[str, float]:
        """Extract features from window switching events"""
        if not window_events:
            return {
                'window_switch_count': 0.0,
                'active_app_duration': window_seconds,
                'unique_apps_count': 0.0,
            }
        
        # Count switches
        switch_count = len(window_events)
        
        # Count unique apps
        app_names = [e.get('process_name', 'Unknown') for e in window_events]
        unique_apps = len(set(app_names))
        
        # Average duration per app
        avg_duration = window_seconds / max(switch_count, 1)
        
        return {
            'window_switch_count': float(switch_count),
            'active_app_duration': avg_duration,
            'unique_apps_count': float(unique_apps),
        }
    
    def _calculate_input_diversity(self, keyboard_events: List, mouse_events: List) -> float:
        """
        Calculate diversity of input types
        High diversity = genuine work
        Low diversity = bot (e.g., only keyboard, no mouse)
        """
        has_keyboard = len(keyboard_events) > 0
        has_mouse_move = any(e['event_type'] == 'mouse_move' for e in mouse_events)
        has_mouse_click = any(e['event_type'] == 'mouse_click' for e in mouse_events)
        
        diversity_score = sum([has_keyboard, has_mouse_move, has_mouse_click]) / 3.0
        
        return diversity_score
    
    def _calculate_overall_entropy(self, all_events: Dict[str, List]) -> float:
        """Calculate overall system entropy across all event types"""
        keyboard_events = all_events.get('keyboard', [])
        mouse_events = all_events.get('mouse', [])
        
        if not keyboard_events and not mouse_events:
            return 0.0
        
        # Combine event types
        event_types = []
        event_types.extend(['keyboard'] * len(keyboard_events))
        event_types.extend(['mouse'] * len(mouse_events))
        
        # Calculate entropy of event type distribution
        type_counts = Counter(event_types)
        total = len(event_types)
        
        entropy = 0.0
        for count in type_counts.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        # Normalize (max entropy for 2 types)
        max_entropy = np.log2(2)
        normalized_entropy = entropy / max_entropy
        
        return normalized_entropy


# Standalone test
if __name__ == "__main__":
    sample_data = {
        'keyboard': [
            {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'a'},
            {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'b'},
        ],
        'mouse': [
            {'timestamp': datetime.now(), 'event_type': 'mouse_move', 'x': 100, 'y': 100, 'distance': 10},
            {'timestamp': datetime.now(), 'event_type': 'mouse_click', 'x': 100, 'y': 100, 'button': 'left', 'pressed': True},
        ],
        'window': [
            {'timestamp': datetime.now(), 'event_type': 'window_change', 'process_name': 'chrome.exe'},
        ]
    }
    
    extractor = TemporalFeatureExtractor()
    features = extractor.extract(sample_data, window_seconds=60)
    
    print("Temporal Features:")
    for key, value in features.items():
        print(f"  {key}: {value:.4f}")
