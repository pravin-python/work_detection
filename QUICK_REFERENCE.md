# 📋 Quick Reference Card

## 🚀 Essential Commands (Copy-Paste Ready)

### First Time Setup

```bash
# 1. Virtual environment बनाएं
python -m venv venv

# 2. Activate करें (Windows)
venv\Scripts\activate

# 3. Dependencies install करें
pip install -r requirements.txt

# 4. Models train करें
python -m src.models.train
```

---

### Daily Use

```bash
# Real-time monitor चलाएं
python monitor.py

# Stop करने के लिए
Ctrl+C
```

---

### Testing

```bash
# Quick demo (30 seconds)
python quick_start.py

# Model evaluation
python -m src.models.evaluate
```

---

### Troubleshooting

```bash
# Dependencies re-install
pip install -r requirements.txt --force-reinstall

# Check Tesseract
tesseract --version

# View logs
type work_detection.log

# Check models
dir data\models\*.joblib
```

---

## 📁 Important Files

| File | Purpose |
|------|---------|
| `monitor.py` | Real-time continuous monitoring |
| `quick_start.py` | 30-second demo |
| `SETUP.md` | Complete setup guide |
| `MONITOR_GUIDE.md` | Monitor usage guide |
| `requirements.txt` | Dependencies list |

---

## 🎯 Quick Workflow

```
1. Setup (one time)
   ↓
2. Train models (one time)
   ↓
3. Run monitor (daily)
   ↓
4. Check reports (as needed)
```

---

## ⚙️ Configuration Files

| File | What to Edit |
|------|--------------|
| `src/utils/config.py` | Thresholds, intervals, paths |
| `monitor.py` | Analysis interval, user ID |

---

## 📊 Output Locations

| Type | Location |
|------|----------|
| Models | `data/models/*.joblib` |
| Reports | `data/reports/*.json` |
| Logs | `work_detection.log` |
| Training Data | `data/processed/training_data.csv` |

---

## 🔧 Common Settings

### Change Analysis Interval

Edit `monitor.py`:

```python
monitor = RealtimeMonitor(
    analysis_interval=30,  # 60 से 30 seconds
)
```

### Change Detection Sensitivity

Edit `src/utils/config.py`:

```python
RULE_THRESHOLDS = {
    'repeat_key_ratio': 0.8,  # Higher = less sensitive
}
```

### Disable Screenshots

Edit `src/utils/config.py`:

```python
ENABLE_SCREENSHOTS = False
```

---

## ✅ Verification Commands

```bash
# Check Python
python --version

# Check dependencies
python -c "import pynput, pandas, sklearn; print('OK')"

# Check Tesseract
tesseract --version

# Check models
python -c "from pathlib import Path; print('Models:', list(Path('data/models').glob('*.joblib')))"
```

---

## 🆘 Emergency Fixes

### System not working?

```bash
# 1. Re-activate virtual environment
venv\Scripts\activate

# 2. Re-install everything
pip install -r requirements.txt --force-reinstall

# 3. Re-train models
python -m src.models.train

# 4. Test
python quick_start.py
```

### Models not found?

```bash
python -m src.models.train
```

### Tesseract errors?

```python
# Edit src/utils/config.py:
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
OCR_ENABLED = False  # Disable temporarily
```

---

## 📞 Support Files

- `SETUP.md` - Complete setup guide
- `MONITOR_GUIDE.md` - Monitor usage (Hindi/English)
- `README.md` - Project overview
- `ARCHITECTURE.md` - System design

---

**Print this card and keep it handy! 📌**
