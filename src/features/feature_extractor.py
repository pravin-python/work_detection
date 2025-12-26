"""
Unified feature extractor that combines all feature types
"""

import pandas as pd
from typing import Dict, List, Any

from .keyboard_features import KeyboardFeatureExtractor
from .mouse_features import MouseFeatureExtractor
from .temporal_features import TemporalFeatureExtractor
from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE, FEATURE_NAMES

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class FeatureExtractor:
    """Unified feature extractor combining all feature types"""
    
    def __init__(self):
        self.keyboard_extractor = KeyboardFeatureExtractor()
        self.mouse_extractor = MouseFeatureExtractor()
        self.temporal_extractor = TemporalFeatureExtractor()
        
        logger.info("FeatureExtractor initialized")
    
    def extract_features(self, events: Dict[str, List[Dict[str, Any]]], window_seconds: int = 60) -> Dict[str, float]:
        """
        Extract all features from collected events
        
        Args:
            events: Dictionary with 'keyboard', 'mouse', 'window' event lists
            window_seconds: Time window for analysis
        
        Returns:
            Dictionary of all features
        """
        features = {}
        
        # Extract keyboard features
        keyboard_events = events.get('keyboard', [])
        keyboard_features = self.keyboard_extractor.extract(keyboard_events, window_seconds)
        features.update(keyboard_features)
        
        # Extract mouse features
        mouse_events = events.get('mouse', [])
        mouse_features = self.mouse_extractor.extract(mouse_events, window_seconds)
        features.update(mouse_features)
        
        # Extract temporal features
        temporal_features = self.temporal_extractor.extract(events, window_seconds)
        features.update(temporal_features)
        
        logger.debug(f"Extracted {len(features)} features")
        
        return features
    
    def extract_features_to_dataframe(self, events: Dict[str, List[Dict[str, Any]]], window_seconds: int = 60) -> pd.DataFrame:
        """
        Extract features and return as a pandas DataFrame
        
        Args:
            events: Dictionary with event lists
            window_seconds: Time window
        
        Returns:
            DataFrame with one row of features
        """
        features = self.extract_features(events, window_seconds)
        df = pd.DataFrame([features])
        
        return df
    
    def get_feature_names(self) -> List[str]:
        """Get list of all feature names"""
        return FEATURE_NAMES
    
    def validate_features(self, features: Dict[str, float]) -> bool:
        """
        Validate that all required features are present
        
        Args:
            features: Feature dictionary
        
        Returns:
            True if valid, False otherwise
        """
        expected_features = set(FEATURE_NAMES)
        actual_features = set(features.keys())
        
        missing = expected_features - actual_features
        extra = actual_features - expected_features
        
        if missing:
            logger.warning(f"Missing features: {missing}")
        
        if extra:
            logger.warning(f"Extra features: {extra}")
        
        return len(missing) == 0


# Standalone test
if __name__ == "__main__":
    from datetime import datetime
    
    # Sample events
    sample_events = {
        'keyboard': [
            {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'a'},
            {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'b'},
            {'timestamp': datetime.now(), 'event_type': 'key_press', 'key': 'c'},
        ],
        'mouse': [
            {'timestamp': datetime.now(), 'event_type': 'mouse_move', 'x': 100, 'y': 100, 'distance': 0},
            {'timestamp': datetime.now(), 'event_type': 'mouse_move', 'x': 110, 'y': 105, 'distance': 11.2},
            {'timestamp': datetime.now(), 'event_type': 'mouse_click', 'x': 110, 'y': 105, 'button': 'left', 'pressed': True},
        ],
        'window': [
            {'timestamp': datetime.now(), 'event_type': 'window_change', 'process_name': 'chrome.exe'},
        ]
    }
    
    extractor = FeatureExtractor()
    features = extractor.extract_features(sample_events, window_seconds=60)
    
    print(f"\nExtracted {len(features)} features:")
    for key, value in sorted(features.items()):
        print(f"  {key}: {value:.4f}")
    
    # Test DataFrame conversion
    df = extractor.extract_features_to_dataframe(sample_events)
    print(f"\nDataFrame shape: {df.shape}")
    print(df.head())
