"""
Data simulator for generating fake and genuine work patterns
Used for training ML models
"""

import random
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
import pandas as pd

from ..features.feature_extractor import FeatureExtractor
from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE, FAKE_DATA_PATTERNS

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class DataSimulator:
    """Simulate fake and genuine work patterns for training"""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        logger.info("DataSimulator initialized")
    
    def generate_training_data(self, num_genuine: int = 100, num_fake: int = 100) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Generate training data with labels
        
        Args:
            num_genuine: Number of genuine work samples
            num_fake: Number of fake work samples
        
        Returns:
            Tuple of (features_df, labels_series)
        """
        logger.info(f"Generating {num_genuine} genuine + {num_fake} fake samples...")
        
        all_features = []
        all_labels = []
        
        # Generate genuine work samples
        for i in range(num_genuine):
            events = self._simulate_genuine_work()
            features = self.feature_extractor.extract_features(events, window_seconds=60)
            all_features.append(features)
            all_labels.append(0)  # 0 = Genuine
            
            if (i + 1) % 20 == 0:
                logger.info(f"Generated {i+1}/{num_genuine} genuine samples")
        
        # Generate fake work samples (various patterns)
        fake_patterns = ['auto_key_press', 'mouse_mover', 'shortcut_spammer', 'idle_gamer']
        
        for i in range(num_fake):
            pattern = random.choice(fake_patterns)
            events = self._simulate_fake_work(pattern)
            features = self.feature_extractor.extract_features(events, window_seconds=60)
            all_features.append(features)
            all_labels.append(1)  # 1 = Fake
            
            if (i + 1) % 20 == 0:
                logger.info(f"Generated {i+1}/{num_fake} fake samples")
        
        # Convert to DataFrame
        features_df = pd.DataFrame(all_features)
        labels_series = pd.Series(all_labels, name='label')
        
        logger.info(f"Training data generated: {features_df.shape}")
        
        return features_df, labels_series
    
    def _simulate_genuine_work(self) -> Dict[str, List[Dict[str, Any]]]:
        """Simulate genuine work activity"""
        base_time = datetime.now()
        
        keyboard_events = []
        mouse_events = []
        window_events = []
        
        # Simulate natural typing (bursts and pauses)
        num_typing_bursts = random.randint(3, 8)
        current_time = base_time
        
        for burst in range(num_typing_bursts):
            # Typing burst
            burst_length = random.randint(5, 20)
            for i in range(burst_length):
                key = random.choice('abcdefghijklmnopqrstuvwxyz ')
                keyboard_events.append({
                    'timestamp': current_time,
                    'event_type': 'key_press',
                    'key': key,
                    'is_special': False
                })
                # Natural inter-key delay (100-300ms with variation)
                delay = random.gauss(0.2, 0.08)
                current_time += timedelta(seconds=max(0.05, delay))
            
            # Pause between bursts
            pause = random.uniform(1.0, 5.0)
            current_time += timedelta(seconds=pause)
        
        # Simulate natural mouse movement
        current_time = base_time
        x, y = 500, 500
        
        for i in range(random.randint(20, 50)):
            # Natural curved movement
            dx = random.gauss(0, 50)
            dy = random.gauss(0, 50)
            x += dx
            y += dy
            
            distance = np.sqrt(dx**2 + dy**2)
            
            mouse_events.append({
                'timestamp': current_time,
                'event_type': 'mouse_move',
                'x': int(x),
                'y': int(y),
                'distance': distance
            })
            
            current_time += timedelta(seconds=random.uniform(0.05, 0.3))
        
        # Add some clicks
        for i in range(random.randint(2, 8)):
            mouse_events.append({
                'timestamp': base_time + timedelta(seconds=random.uniform(0, 60)),
                'event_type': 'mouse_click',
                'x': int(x),
                'y': int(y),
                'button': 'left',
                'pressed': True
            })
        
        # Simulate window switches
        apps = ['chrome.exe', 'code.exe', 'slack.exe', 'outlook.exe']
        for i in range(random.randint(1, 4)):
            window_events.append({
                'timestamp': base_time + timedelta(seconds=random.uniform(0, 60)),
                'event_type': 'window_change',
                'process_name': random.choice(apps)
            })
        
        return {
            'keyboard': keyboard_events,
            'mouse': mouse_events,
            'window': window_events
        }
    
    def _simulate_fake_work(self, pattern: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Simulate fake work activity
        
        Args:
            pattern: Type of fake pattern ('auto_key_press', 'mouse_mover', etc.)
        """
        base_time = datetime.now()
        
        if pattern == 'auto_key_press':
            return self._simulate_auto_key_press(base_time)
        elif pattern == 'mouse_mover':
            return self._simulate_mouse_mover(base_time)
        elif pattern == 'shortcut_spammer':
            return self._simulate_shortcut_spammer(base_time)
        elif pattern == 'idle_gamer':
            return self._simulate_idle_gamer(base_time)
        else:
            return self._simulate_auto_key_press(base_time)
    
    def _simulate_auto_key_press(self, base_time: datetime) -> Dict:
        """Simulate auto key press tool"""
        keyboard_events = []
        
        # Repetitive key presses with very consistent timing
        key = random.choice(['a', 'space', 'Key.ctrl_l'])
        
        for i in range(random.randint(50, 150)):
            keyboard_events.append({
                'timestamp': base_time + timedelta(seconds=i * 0.5),  # Very consistent
                'event_type': 'key_press',
                'key': key,
                'is_special': False
            })
        
        return {
            'keyboard': keyboard_events,
            'mouse': [],
            'window': []
        }
    
    def _simulate_mouse_mover(self, base_time: datetime) -> Dict:
        """Simulate mouse mover bot"""
        mouse_events = []
        
        # Linear or circular movement with jitter
        x, y = 500, 500
        
        for i in range(random.randint(100, 300)):
            # Small jittery movements
            dx = random.uniform(-3, 3)
            dy = random.uniform(-3, 3)
            x += dx
            y += dy
            
            distance = np.sqrt(dx**2 + dy**2)
            
            mouse_events.append({
                'timestamp': base_time + timedelta(seconds=i * 0.1),
                'event_type': 'mouse_move',
                'x': int(x),
                'y': int(y),
                'distance': distance
            })
        
        return {
            'keyboard': [],
            'mouse': mouse_events,
            'window': []
        }
    
    def _simulate_shortcut_spammer(self, base_time: datetime) -> Dict:
        """Simulate shortcut spamming"""
        keyboard_events = []
        
        shortcuts = ['Key.ctrl_l', 'z', 'Key.ctrl_l', 'c', 'Key.ctrl_l', 'v']
        
        for i in range(random.randint(30, 80)):
            key = shortcuts[i % len(shortcuts)]
            keyboard_events.append({
                'timestamp': base_time + timedelta(seconds=i * 0.3),
                'event_type': 'key_press',
                'key': key,
                'is_special': 'Key.' in key
            })
        
        return {
            'keyboard': keyboard_events,
            'mouse': [],
            'window': []
        }
    
    def _simulate_idle_gamer(self, base_time: datetime) -> Dict:
        """Simulate activity spike near idle timeout"""
        keyboard_events = []
        mouse_events = []
        
        # Very little activity for most of the window
        for i in range(5):
            keyboard_events.append({
                'timestamp': base_time + timedelta(seconds=random.uniform(0, 40)),
                'event_type': 'key_press',
                'key': random.choice('abc'),
                'is_special': False
            })
        
        # Sudden spike near end (simulating idle timeout gaming)
        spike_start = base_time + timedelta(seconds=50)
        for i in range(30):
            keyboard_events.append({
                'timestamp': spike_start + timedelta(seconds=i * 0.1),
                'event_type': 'key_press',
                'key': random.choice('abcdefgh'),
                'is_special': False
            })
            
            mouse_events.append({
                'timestamp': spike_start + timedelta(seconds=i * 0.1),
                'event_type': 'mouse_move',
                'x': 500 + i * 5,
                'y': 500 + i * 5,
                'distance': 7.07
            })
        
        return {
            'keyboard': keyboard_events,
            'mouse': mouse_events,
            'window': []
        }


# Standalone test
if __name__ == "__main__":
    simulator = DataSimulator()
    
    print("Generating sample training data...")
    features_df, labels = simulator.generate_training_data(num_genuine=10, num_fake=10)
    
    print(f"\nGenerated data shape: {features_df.shape}")
    print(f"Labels distribution:\n{labels.value_counts()}")
    print(f"\nSample features:\n{features_df.head()}")
