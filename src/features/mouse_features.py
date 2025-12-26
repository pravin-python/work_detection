"""
Mouse feature extraction
Extracts behavioral features from mouse events
"""

import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import math

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class MouseFeatureExtractor:
    """Extract features from mouse events"""
    
    def __init__(self):
        logger.debug("MouseFeatureExtractor initialized")
    
    def extract(self, events: List[Dict[str, Any]], window_seconds: int = 60) -> Dict[str, float]:
        """
        Extract mouse features from events
        
        Args:
            events: List of mouse events
            window_seconds: Time window for rate calculations
        
        Returns:
            Dictionary of features
        """
        if not events:
            return self._get_empty_features()
        
        # Separate event types
        move_events = [e for e in events if e['event_type'] == 'mouse_move']
        click_events = [e for e in events if e['event_type'] == 'mouse_click' and e.get('pressed', False)]
        
        features = {}
        
        # 1. Mouse distance
        if move_events:
            total_distance = sum(e.get('distance', 0) for e in move_events)
            features['mouse_distance'] = total_distance
        else:
            features['mouse_distance'] = 0.0
        
        # 2. Velocity statistics
        velocities = self._calculate_velocities(move_events)
        if velocities:
            features['mouse_velocity_avg'] = np.mean(velocities)
            features['mouse_velocity_std'] = np.std(velocities)
        else:
            features['mouse_velocity_avg'] = 0.0
            features['mouse_velocity_std'] = 0.0
        
        # 3. Acceleration statistics
        accelerations = self._calculate_accelerations(velocities)
        if accelerations:
            features['mouse_acceleration_avg'] = np.mean(accelerations)
            features['mouse_acceleration_std'] = np.std(accelerations)
        else:
            features['mouse_acceleration_avg'] = 0.0
            features['mouse_acceleration_std'] = 0.0
        
        # 4. Mouse curvature (path naturalness)
        features['mouse_curvature'] = self._calculate_curvature(move_events)
        
        # 5. Mouse jitter score
        features['mouse_jitter_score'] = self._calculate_jitter(move_events)
        
        # 6. Mouse entropy
        features['mouse_entropy'] = self._calculate_movement_entropy(move_events)
        
        # 7. Click frequency
        features['click_frequency'] = len(click_events) / (window_seconds / 60.0)
        
        # 8. Mouse idle ratio
        features['mouse_idle_ratio'] = self._calculate_idle_ratio(move_events, window_seconds)
        
        return features
    
    def _get_empty_features(self) -> Dict[str, float]:
        """Return zero features when no events"""
        return {
            'mouse_distance': 0.0,
            'mouse_velocity_avg': 0.0,
            'mouse_velocity_std': 0.0,
            'mouse_acceleration_avg': 0.0,
            'mouse_acceleration_std': 0.0,
            'mouse_curvature': 0.0,
            'mouse_jitter_score': 0.0,
            'mouse_entropy': 0.0,
            'click_frequency': 0.0,
            'mouse_idle_ratio': 1.0,  # 100% idle if no events
        }
    
    def _calculate_velocities(self, move_events: List[Dict[str, Any]]) -> List[float]:
        """Calculate velocities between consecutive mouse movements"""
        if len(move_events) < 2:
            return []
        
        velocities = []
        for i in range(1, len(move_events)):
            distance = move_events[i].get('distance', 0)
            time_delta = (move_events[i]['timestamp'] - move_events[i-1]['timestamp']).total_seconds()
            
            if time_delta > 0:
                velocity = distance / time_delta
                velocities.append(velocity)
        
        return velocities
    
    def _calculate_accelerations(self, velocities: List[float]) -> List[float]:
        """Calculate accelerations from velocities"""
        if len(velocities) < 2:
            return []
        
        accelerations = []
        for i in range(1, len(velocities)):
            acceleration = abs(velocities[i] - velocities[i-1])
            accelerations.append(acceleration)
        
        return accelerations
    
    def _calculate_curvature(self, move_events: List[Dict[str, Any]]) -> float:
        """
        Calculate path curvature
        Low curvature (close to 0) = straight line (bot-like)
        High curvature (close to 1) = curved path (human-like)
        """
        if len(move_events) < 3:
            return 0.5  # Neutral
        
        # Calculate total path length vs direct distance
        total_path_length = sum(e.get('distance', 0) for e in move_events)
        
        if total_path_length == 0:
            return 0.0
        
        # Direct distance from start to end
        start_x, start_y = move_events[0]['x'], move_events[0]['y']
        end_x, end_y = move_events[-1]['x'], move_events[-1]['y']
        direct_distance = math.sqrt((end_x - start_x)**2 + (end_y - start_y)**2)
        
        if direct_distance == 0:
            return 0.0
        
        # Curvature ratio: 1 = straight line, >1 = curved
        curvature_ratio = total_path_length / direct_distance
        
        # Normalize to 0-1 (typical human curvature is 1.1-1.5)
        # Bot curvature is very close to 1.0
        normalized_curvature = min((curvature_ratio - 1.0) / 0.5, 1.0)
        
        return max(0.0, normalized_curvature)
    
    def _calculate_jitter(self, move_events: List[Dict[str, Any]]) -> float:
        """
        Calculate jitter score (micro-vibrations)
        High jitter = mouse mover bot
        Low jitter = natural movement
        """
        if len(move_events) < 10:
            return 0.0
        
        # Count very small movements (< 5 pixels)
        small_movements = sum(1 for e in move_events if e.get('distance', 0) < 5)
        jitter_ratio = small_movements / len(move_events)
        
        # High jitter ratio indicates bot
        return jitter_ratio
    
    def _calculate_movement_entropy(self, move_events: List[Dict[str, Any]]) -> float:
        """Calculate entropy of movement directions"""
        if len(move_events) < 3:
            return 0.0
        
        # Calculate movement directions (8 cardinal directions)
        directions = []
        for i in range(1, len(move_events)):
            dx = move_events[i]['x'] - move_events[i-1]['x']
            dy = move_events[i]['y'] - move_events[i-1]['y']
            
            if dx == 0 and dy == 0:
                continue
            
            # Calculate angle (0-360 degrees)
            angle = math.atan2(dy, dx) * 180 / math.pi
            
            # Bin into 8 directions
            direction_bin = int((angle + 180) / 45) % 8
            directions.append(direction_bin)
        
        if not directions:
            return 0.0
        
        # Calculate Shannon entropy
        from collections import Counter
        direction_counts = Counter(directions)
        total = len(directions)
        
        entropy = 0.0
        for count in direction_counts.values():
            probability = count / total
            if probability > 0:
                entropy -= probability * np.log2(probability)
        
        # Normalize (max entropy for 8 directions)
        max_entropy = np.log2(8)
        normalized_entropy = entropy / max_entropy
        
        return normalized_entropy
    
    def _calculate_idle_ratio(self, move_events: List[Dict[str, Any]], window_seconds: int) -> float:
        """Calculate ratio of time with no mouse movement"""
        if not move_events:
            return 1.0
        
        # Calculate time spans with movement
        if len(move_events) < 2:
            return 0.9
        
        first_event_time = move_events[0]['timestamp']
        last_event_time = move_events[-1]['timestamp']
        active_duration = (last_event_time - first_event_time).total_seconds()
        
        idle_duration = window_seconds - active_duration
        idle_ratio = max(0.0, min(1.0, idle_duration / window_seconds))
        
        return idle_ratio


# Standalone test
if __name__ == "__main__":
    # Test with sample events
    import time
    now = datetime.now()
    
    sample_events = [
        {'timestamp': now, 'event_type': 'mouse_move', 'x': 100, 'y': 100, 'distance': 0},
        {'timestamp': now, 'event_type': 'mouse_move', 'x': 110, 'y': 105, 'distance': 11.2},
        {'timestamp': now, 'event_type': 'mouse_move', 'x': 120, 'y': 110, 'distance': 11.2},
        {'timestamp': now, 'event_type': 'mouse_click', 'x': 120, 'y': 110, 'button': 'left', 'pressed': True},
    ]
    
    extractor = MouseFeatureExtractor()
    features = extractor.extract(sample_events, window_seconds=60)
    
    print("Mouse Features:")
    for key, value in features.items():
        print(f"  {key}: {value:.4f}")
