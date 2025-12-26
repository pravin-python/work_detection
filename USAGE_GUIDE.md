# 📖 Usage Guide - Fake vs Real Work Detection System

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Training Models](#training-models)
4. [Real-Time Detection](#real-time-detection)
5. [Understanding Results](#understanding-results)
6. [Configuration](#configuration)
7. [Troubleshooting](#troubleshooting)

---

## 🚀 Installation

### Prerequisites

- **Python 3.8+** (3.9 or 3.10 recommended)
- **Windows OS** (primary support)
- **Administrator privileges** (for keyboard/mouse monitoring)

### Step 1: Clone or Download

```bash
cd e:\local_models\work_detection
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Verify Installation

```bash
python -c "import pynput, pandas, sklearn; print('✅ All dependencies installed')"
```

---

## ⚡ Quick Start

### Run the Demo (Recommended First Step)

```bash
python quick_start.py
```

**What it does**:

1. Collects your activity for 30 seconds
2. Extracts behavioral features
3. Detects if activity appears genuine or fake
4. Generates a detailed report

**Expected Output**:

```
╔══════════════════════════════════════════════════════════════╗
║        🧠 FAKE vs REAL WORK DETECTION SYSTEM 🧠             ║
╚══════════════════════════════════════════════════════════════╝

📊 PHASE 1: Data Collection
...
✅ Collection complete!
   Total events: 245
   Keyboard: 87
   Mouse: 152
   Window: 6

🔬 PHASE 2: Feature Extraction
...
✅ Extracted 30 features

🎯 PHASE 3: Fake Work Detection
...
Decision: GENUINE_WORK
Confidence: HIGH
```

---

## 🎓 Training Models

### Generate Training Data & Train Models

```bash
python -m src.models.train
```

**What it does**:

1. Generates 500 genuine + 500 fake work samples
2. Extracts features from all samples
3. Trains Random Forest, XGBoost, and Isolation Forest
4. Evaluates models on test set
5. Saves models to `data/models/`

**Expected Output**:

```
🧠 Work Detection System - Model Training
======================================================================

Generating 500 genuine + 500 fake samples...
Generated 500/500 genuine samples
Generated 500/500 fake samples

Training Random Forest model...
Random Forest Metrics:
  Accuracy:  0.9550
  Precision: 0.9423
  Recall:    0.9680
  F1 Score:  0.9550

Training XGBoost model...
XGBoost Metrics:
  Accuracy:  0.9650
  Precision: 0.9545
  Recall:    0.9760
  F1 Score:  0.9651

💾 Models saved to: data\models
```

### Custom Training Parameters

Edit `src/utils/config.py`:

```python
# Random Forest Hyperparameters
RF_PARAMS = {
    'n_estimators': 200,  # Increase trees
    'max_depth': 20,      # Deeper trees
    'min_samples_split': 5,
    'random_state': 42,
}
```

---

## 🔍 Real-Time Detection

### Option 1: Using Quick Start

```bash
python quick_start.py
```

- Collects for 30 seconds
- Provides immediate feedback
- Best for testing

### Option 2: Continuous Monitoring (Custom Script)

Create `monitor.py`:

```python
import time
from src.collectors.unified_collector import UnifiedCollector
from src.features.feature_extractor import FeatureExtractor
from src.detection.rule_based import RuleBasedDetector

collector = UnifiedCollector()
extractor = FeatureExtractor()
detector = RuleBasedDetector()

collector.start()

try:
    while True:
        time.sleep(60)  # Every 60 seconds
        
        events = collector.get_all_events(window_seconds=60)
        features = extractor.extract_features(events)
        report = detector.generate_report(features)
        
        print(f"[{report['timestamp']}] {report['decision']}")
        
        if "FAKE" in report['decision']:
            print(f"⚠️  WARNING: {report['reasons']}")
            
except KeyboardInterrupt:
    collector.stop()
```

Run:

```bash
python monitor.py
```

---

## 📊 Understanding Results

### Detection Report Structure

```json
{
  "user_id": "USER_001",
  "timestamp": "2025-12-26T17:00:00",
  "fake_probability": 0.87,
  "decision": "FAKE_WORK (HIGH CONFIDENCE)",
  "confidence": "HIGH",
  "reasons": [
    "Excessive key repetition (0.92)",
    "Linear mouse movement detected (curvature: 0.03)",
    "Shortcut abuse detected (0.75)"
  ],
  "feature_scores": {
    "keystroke_entropy": 0.23,
    "mouse_curvature": 0.03,
    "shortcut_abuse_score": 0.75,
    "activity_spike_score": 0.15,
    "periodic_behavior_score": 0.82
  }
}
```

### Decision Labels

- **GENUINE_WORK**: No suspicious patterns detected
- **SUSPICIOUS**: 1 rule violation, low confidence
- **FAKE_WORK (MEDIUM CONFIDENCE)**: 2+ violations, 50-80% confidence
- **FAKE_WORK (HIGH CONFIDENCE)**: 2+ violations, >80% confidence

### Key Feature Interpretations

| Feature | Genuine Range | Fake Range | Meaning |
|---------|---------------|------------|---------|
| `keystroke_entropy` | 0.6-1.0 | 0.0-0.3 | Key diversity |
| `mouse_curvature` | 0.4-1.0 | 0.0-0.2 | Path naturalness |
| `shortcut_abuse_score` | 0.0-0.3 | 0.5-1.0 | Ctrl+Z/C/V ratio |
| `activity_spike_score` | 0.0-0.4 | 0.7-1.0 | Idle timeout gaming |
| `periodic_behavior_score` | 0.0-0.4 | 0.7-1.0 | Bot-like timing |
| `mouse_jitter_score` | 0.0-0.3 | 0.6-1.0 | Mouse mover bot |

---

## ⚙️ Configuration

### Edit `src/utils/config.py`

#### Data Collection Settings

```python
COLLECTION_WINDOW_SECONDS = 60  # Analysis window
KEYBOARD_BUFFER_SIZE = 1000     # Max events to store
MOUSE_BUFFER_SIZE = 1000
```

#### Detection Thresholds

```python
RULE_THRESHOLDS = {
    'repeat_key_ratio': 0.7,        # Lower = stricter
    'mouse_linearity': 0.95,        # Higher = stricter
    'shortcut_abuse_ratio': 0.5,
    'idle_spike_threshold': 0.8,
    'zero_entropy_threshold': 0.1,
}
```

#### Logging

```python
LOG_LEVEL = 'INFO'  # Options: DEBUG, INFO, WARNING, ERROR
LOG_FILE = PROJECT_ROOT / "work_detection.log"
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" errors

**Solution**:

```bash
# Ensure virtual environment is activated
venv\Scripts\activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: "Access Denied" when collecting keyboard/mouse

**Solution**:

- Run terminal as **Administrator**
- Check antivirus isn't blocking `pynput`

### Issue: WindowCollector not working

**Solution**:

```bash
# Install Windows-specific dependencies
pip install pywin32 psutil
```

### Issue: Very low event counts

**Possible Causes**:

1. **Not enough activity**: Perform more actions during collection
2. **Buffer overflow**: Increase `KEYBOARD_BUFFER_SIZE` in config
3. **Collection too short**: Increase collection duration

### Issue: All activity flagged as fake

**Solution**:

1. **Adjust thresholds**: Lower sensitivity in `RULE_THRESHOLDS`
2. **Retrain models**: Generate more diverse training data
3. **Check feature extraction**: Verify features are in expected ranges

### Issue: Models not loading

**Solution**:

```bash
# Retrain models
python -m src.models.train

# Verify model files exist
dir data\models\*.joblib
```

---

## 📈 Advanced Usage

### Custom Feature Extraction

```python
from src.collectors.unified_collector import UnifiedCollector
from src.features.feature_extractor import FeatureExtractor

collector = UnifiedCollector()
collector.start()

# ... collect for some time ...

events = collector.get_all_events(window_seconds=60)
extractor = FeatureExtractor()
features = extractor.extract_features(events)

# Access individual features
print(f"Keys per minute: {features['keys_per_minute']}")
print(f"Mouse entropy: {features['mouse_entropy']}")
```

### Using ML Models (After Training)

```python
import joblib
from src.utils.config import MODELS_DIR

# Load model
model = joblib.load(MODELS_DIR / "random_forest_model.joblib")
scaler = joblib.load(MODELS_DIR / "feature_scaler.joblib")

# Prepare features
import pandas as pd
features_df = pd.DataFrame([features])
features_scaled = scaler.transform(features_df)

# Predict
prediction = model.predict(features_scaled)[0]
probability = model.predict_proba(features_scaled)[0][1]

print(f"Prediction: {'FAKE' if prediction == 1 else 'GENUINE'}")
print(f"Fake probability: {probability:.2%}")
```

### Batch Processing

```python
import json
from pathlib import Path

# Process multiple saved event files
for event_file in Path("data/raw").glob("events_*.json"):
    with open(event_file) as f:
        events = json.load(f)
    
    features = extractor.extract_features(events)
    report = detector.generate_report(features)
    
    print(f"{event_file.name}: {report['decision']}")
```

---

## 📚 Next Steps

1. **Read Architecture**: See `ARCHITECTURE.md` for system design
2. **Explore Code**: Browse `src/` for implementation details
3. **Customize**: Modify thresholds and features for your use case
4. **Integrate**: Add webhooks, alerts, or database logging
5. **Contribute**: Improve models, add features, fix bugs

---

## 🆘 Getting Help

- **Documentation**: `README.md`, `ARCHITECTURE.md`
- **Logs**: Check `work_detection.log` for detailed errors
- **Issues**: Review error messages and stack traces
- **Community**: (Add your support channels here)

---

**Last Updated**: 2025-12-26
**Version**: 1.0.0
