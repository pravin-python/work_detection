"""
Configuration settings for the Work Detection System
"""

import os
import platform
from pathlib import Path

# Platform Detection
PLATFORM = platform.system()  # 'Windows', 'Linux', 'Darwin' (macOS)

# Project Root
PROJECT_ROOT = Path(__file__).parent.parent.parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
MODELS_DIR = DATA_DIR / "models"

# Create directories if they don't exist
for directory in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, MODELS_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# Data Collection Settings
COLLECTION_WINDOW_SECONDS = 60  # 1-minute windows
KEYBOARD_BUFFER_SIZE = 1000
MOUSE_BUFFER_SIZE = 1000

# Screenshot Settings (v2.1 Enhancement)
ENABLE_SCREENSHOTS = True  # Enable screenshot intelligence
SCREENSHOT_INTERVAL_SECONDS = 60  # Capture 1 screenshot per minute
SCREENSHOT_BUFFER_SIZE = 10  # Keep last 10 screenshots in memory
SCREENSHOT_QUALITY = 85  # JPEG quality (1-100)
SCREENSHOT_PRIVACY_MODE = False  # Blur sensitive areas (future feature)

# Visual Analysis Settings
SSIM_THRESHOLD = 0.95  # Screen similarity threshold (same screen detection)
OCR_TEXT_CHANGE_THRESHOLD = 0.05  # Minimal text change threshold
VISUAL_ENTROPY_THRESHOLD = 2.0  # Low visual complexity threshold
NO_PROGRESS_DURATION_THRESHOLD = 600  # 10 minutes in seconds
SCROLL_ONLY_THRESHOLD = 0.8  # Scroll-only behavior threshold
KEYBOARD_SCREEN_MISMATCH_THRESHOLD = 0.7  # Keyboard-screen mismatch threshold

# OCR Settings
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Auto-detect or specify path (e.g., r'C:\Program Files\Tesseract-OCR\tesseract.exe')
OCR_LANGUAGE = 'eng'  # Tesseract language code
OCR_ENABLED = True  # Enable OCR text extraction

# Feature Engineering Settings
MIN_EVENTS_FOR_ANALYSIS = 5  # Minimum events needed to compute features

# Detection Thresholds (Rule-Based)
RULE_THRESHOLDS = {
    'repeat_key_ratio': 0.7,  # >70% same key = suspicious
    'mouse_linearity': 0.95,  # >95% linear movement = bot
    'shortcut_abuse_ratio': 0.5,  # >50% shortcuts = suspicious
    'idle_spike_threshold': 0.8,  # Activity spike near idle timeout
    'zero_entropy_threshold': 0.1,  # Very low entropy = bot
}

# ML Model Settings
ML_MODEL_TYPE = 'random_forest'  # Options: 'random_forest', 'xgboost', 'isolation_forest'
MODEL_PATH = MODELS_DIR / f"{ML_MODEL_TYPE}_model.joblib"
SCALER_PATH = MODELS_DIR / "feature_scaler.joblib"

# Random Forest Hyperparameters
RF_PARAMS = {
    'n_estimators': 100,
    'max_depth': 15,
    'min_samples_split': 10,
    'min_samples_leaf': 5,
    'random_state': 42,
    'n_jobs': -1
}

# XGBoost Hyperparameters
XGB_PARAMS = {
    'n_estimators': 100,
    'max_depth': 10,
    'learning_rate': 0.1,
    'random_state': 42,
    'n_jobs': -1
}

# Isolation Forest Hyperparameters
IFOREST_PARAMS = {
    'n_estimators': 100,
    'contamination': 0.1,  # Expected proportion of outliers
    'random_state': 42,
    'n_jobs': -1
}

# Real-time Detection Settings
REALTIME_WINDOW_SECONDS = 60  # Analyze every 60 seconds
CONFIDENCE_THRESHOLDS = {
    'HIGH': 0.8,  # >80% probability
    'MEDIUM': 0.5,  # 50-80% probability
    'LOW': 0.0  # <50% probability
}

# Decision Labels
DECISION_LABELS = {
    0: 'GENUINE_WORK',
    1: 'FAKE_WORK'
}

# Logging Settings
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = PROJECT_ROOT / "work_detection.log"

# Training Data Settings
TRAIN_TEST_SPLIT = 0.2  # 80% train, 20% test
VALIDATION_SPLIT = 0.2  # 20% of training for validation
RANDOM_SEED = 42

# Fake Data Simulation Settings
FAKE_DATA_PATTERNS = {
    'auto_key_press': {
        'key_repeat_ratio': 0.9,
        'inter_key_delay_std': 0.01,  # Very consistent timing
        'entropy': 0.1
    },
    'mouse_mover': {
        'movement_linearity': 0.98,
        'jitter_frequency': 10,  # Hz
        'entropy': 0.15
    },
    'shortcut_spammer': {
        'shortcut_ratio': 0.8,
        'unique_key_ratio': 0.1
    },
    'idle_gamer': {
        'activity_spike_timing': [540, 550, 560],  # Seconds (near 10-min timeout)
        'spike_intensity': 5.0  # 5x normal activity
    }
}

# Feature Names (for reference)
FEATURE_NAMES = [
    # Keyboard features
    'keys_per_minute',
    'unique_key_ratio',
    'repeat_key_ratio',
    'avg_inter_key_delay',
    'std_inter_key_delay',
    'keystroke_entropy',
    'shortcut_abuse_score',
    'burst_typing_score',
    'max_consecutive_repeats',
    
    # Mouse features
    'mouse_distance',
    'mouse_velocity_avg',
    'mouse_velocity_std',
    'mouse_acceleration_avg',
    'mouse_acceleration_std',
    'mouse_curvature',
    'mouse_jitter_score',
    'mouse_entropy',
    'click_frequency',
    'mouse_idle_ratio',
    
    # Temporal features
    'idle_seconds',
    'active_seconds',
    'activity_spike_score',
    'periodic_behavior_score',
    'time_since_last_activity',
    
    # Context features
    'window_switch_count',
    'active_app_duration',
    'unique_apps_count',
    
    # Combined features
    'input_diversity_score',
    'overall_entropy_score',
]

# User Identification (for multi-user scenarios)
DEFAULT_USER_ID = "USER_001"
