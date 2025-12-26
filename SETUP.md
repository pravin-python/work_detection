# 🚀 Complete Setup Guide - Starting से शुरू करें

## 📋 Table of Contents

1. [System Requirements](#system-requirements)
2. [Installation Steps](#installation-steps)
3. [Tesseract OCR Setup](#tesseract-ocr-setup)
4. [First Time Model Training](#first-time-model-training)
5. [Running the System](#running-the-system)
6. [Troubleshooting](#troubleshooting)

---

## 1️⃣ System Requirements

### Minimum Requirements

- **OS**: Windows 10/11, Ubuntu 20.04+, macOS 11+
- **Python**: 3.8 या higher (3.9/3.10 recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk Space**: 500MB free space
- **Internet**: Dependencies download के लिए

### Check Python Version

```bash
python --version
# या
python3 --version
```

Expected output: `Python 3.8.x` या higher

---

## 2️⃣ Installation Steps

### Step 1: Project Download करें

```bash
# अगर Git है तो:
git clone <repository-url>
cd work_detection

# या ZIP download करके extract करें
cd work_detection
```

### Step 2: Virtual Environment बनाएं

**Windows:**

```powershell
# Virtual environment बनाएं
python -m venv venv

# Activate करें
venv\Scripts\activate

# Verify (prompt में (venv) दिखना चाहिए)
```

**Linux/macOS:**

```bash
# Virtual environment बनाएं
python3 -m venv venv

# Activate करें
source venv/bin/activate

# Verify
```

### Step 3: Dependencies Install करें

```bash
# Pip को update करें
python -m pip install --upgrade pip

# सभी dependencies install करें
pip install -r requirements.txt
```

**यह install होगा:**

- Core libraries (pynput, psutil)
- Data processing (pandas, numpy)
- Machine Learning (scikit-learn, xgboost)
- Visual Intelligence (mss, Pillow, opencv, pytesseract, scikit-image)
- Platform-specific libraries (automatic)

**Installation time:** 5-10 minutes (internet speed पर depend करता है)

### Step 4: Verify Installation

```bash
# Test करें कि सब install हुआ या नहीं
python -c "import pynput, pandas, sklearn, cv2, PIL; print('✅ All dependencies installed successfully!')"
```

---

## 3️⃣ Tesseract OCR Setup

### Windows

**Step 1: Download Tesseract**

1. यहाँ जाएं: <https://github.com/UB-Mannheim/tesseract/wiki>
2. Download करें: `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (या latest)

**Step 2: Install करें**

1. Installer run करें
2. Installation path note करें (default: `C:\Program Files\Tesseract-OCR`)
3. "Add to PATH" option check करें

**Step 3: PATH Configure करें**

अगर auto-add नहीं हुआ:

```powershell
# System PATH में add करें
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR"

# Terminal restart करें
```

**Step 4: Config File Update करें**

`src/utils/config.py` खोलें और update करें:

```python
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Step 5: Verify करें**

```bash
tesseract --version
```

Expected output:

```
tesseract v5.3.3
```

### Ubuntu/Linux

```bash
# Install करें
sudo apt-get update
sudo apt-get install tesseract-ocr

# Verify करें
tesseract --version
which tesseract
```

### macOS

```bash
# Homebrew से install करें
brew install tesseract

# Verify करें
tesseract --version
which tesseract
```

---

## 4️⃣ First Time Model Training

### Step 1: Directories बनाएं

```bash
# Data directories automatically बन जाएंगी, लेकिन verify करें:
python -c "from src.utils.config import DATA_DIR, MODELS_DIR; print(f'Data: {DATA_DIR}'); print(f'Models: {MODELS_DIR}')"
```

### Step 2: पहली बार Model Train करें

```bash
python -m src.models.train
```

**क्या होगा:**

1. ✅ 1000 training samples generate होंगे (500 genuine + 500 fake)
2. ✅ 30 behavioral features extract होंगे
3. ✅ 3 models train होंगे:
   - Random Forest (primary)
   - XGBoost (alternative)
   - Isolation Forest (anomaly detection)
4. ✅ Models evaluate होंगे
5. ✅ Models save होंगे (`data/models/`)

**Expected Output:**

```
🧠 Work Detection System - Model Training
======================================================================

Generating 500 genuine + 500 fake samples...
✅ Generated 1000 samples

Training Random Forest model...
✅ Accuracy: 100.00%

Training XGBoost model...
✅ Accuracy: 99.50%

💾 Models saved to: data\models
```

**Time:** 2-5 minutes

### Step 3: Models Verify करें

```bash
# Models की location check करें
dir data\models\*.joblib

# या Linux/macOS:
ls -lh data/models/*.joblib
```

**आपको दिखना चाहिए:**

```
random_forest_model.joblib
xgboost_model.joblib
isolation_forest_model.joblib
feature_scaler.joblib
```

### Step 4: Model Evaluation करें

```bash
python -m src.models.evaluate
```

**Expected Output:**

```
📊 Random Forest Performance:
   Accuracy:  100.00%
   Precision: 100.00%
   Recall:    100.00%

📊 XGBoost Performance:
   Accuracy:  99.50%
   Precision: 99.01%
   Recall:    100.00%
```

---

## 5️⃣ Running the System

### Option 1: Quick Demo (30 seconds)

```bash
python quick_start.py
```

**यह करेगा:**

- 30 seconds activity collect करेगा
- Features extract करेगा
- Fake work detect करेगा
- Report generate करेगा

**Use Case:** Testing, demonstration

### Option 2: Real-Time Monitor (Continuous)

```bash
python monitor.py
```

**यह करेगा:**

- Background में continuously चलेगा
- हर 60 seconds में analyze करेगा
- Fake work detect करेगा
- Reports save करेगा (`data/reports/`)
- Ctrl+C से stop होगा

**Use Case:** Production, daily monitoring

---

## 6️⃣ Troubleshooting

### Issue 1: "Module not found" errors

**Solution:**

```bash
# Virtual environment activate है या नहीं check करें
# Prompt में (venv) दिखना चाहिए

# अगर नहीं है तो activate करें:
# Windows:
venv\Scripts\activate

# Linux/macOS:
source venv/bin/activate

# Dependencies फिर से install करें:
pip install -r requirements.txt --force-reinstall
```

### Issue 2: "tesseract is not recognized"

**Windows Solution:**

```powershell
# Check if Tesseract installed है
dir "C:\Program Files\Tesseract-OCR\tesseract.exe"

# अगर है तो PATH में add करें या config.py update करें:
# src/utils/config.py में:
TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/macOS Solution:**

```bash
# Check installation
which tesseract

# अगर नहीं है तो install करें:
# Ubuntu:
sudo apt-get install tesseract-ocr

# macOS:
brew install tesseract
```

### Issue 3: "Access Denied" during data collection

**Solution:**

```bash
# Administrator/sudo के साथ run करें:
# Windows (PowerShell as Admin):
python monitor.py

# Linux/macOS:
sudo python monitor.py
```

### Issue 4: Models train नहीं हो रहे

**Solution:**

```bash
# Check Python version
python --version  # 3.8+ होना चाहिए

# Check dependencies
pip list | grep -E "scikit-learn|xgboost|pandas"

# Re-install ML libraries
pip install scikit-learn==1.3.2 xgboost==2.0.3 --force-reinstall

# Try training again
python -m src.models.train
```

### Issue 5: Screenshot capture नहीं हो रहा

**Solution:**

```bash
# Check mss installation
pip install mss Pillow --force-reinstall

# Disable screenshots temporarily (config.py में):
ENABLE_SCREENSHOTS = False

# System फिर भी work करेगा (without visual features)
```

---

## ✅ Verification Checklist

Setup complete होने के बाद verify करें:

- [ ] Python 3.8+ installed
- [ ] Virtual environment activated
- [ ] All dependencies installed
- [ ] Tesseract OCR installed and configured
- [ ] Models trained successfully
- [ ] `quick_start.py` runs without errors
- [ ] `monitor.py` starts successfully

### Quick Verification Commands

```bash
# 1. Python version
python --version

# 2. Dependencies
python -c "import pynput, pandas, sklearn; print('✅ Core OK')"

# 3. Tesseract
tesseract --version

# 4. Models exist
dir data\models\*.joblib

# 5. Quick test
python quick_start.py
```

---

## 📚 Next Steps

Setup complete होने के बाद:

1. **Documentation पढ़ें:**
   - `README.md` - Project overview
   - `MONITOR_GUIDE.md` - Monitor usage
   - `ARCHITECTURE.md` - System design

2. **System Test करें:**

   ```bash
   python quick_start.py
   ```

3. **Real-time monitoring शुरू करें:**

   ```bash
   python monitor.py
   ```

4. **Reports check करें:**

   ```bash
   dir data\reports
   ```

---

## 🆘 Getting Help

अगर कोई problem आए:

1. **Logs check करें:**

   ```bash
   type work_detection.log
   ```

2. **Error message ध्यान से पढ़ें**

3. **Troubleshooting section देखें** (ऊपर)

4. **Dependencies re-install करें:**

   ```bash
   pip install -r requirements.txt --force-reinstall
   ```

---

## 📊 Summary

**Complete Setup में Steps:**

1. ✅ Python 3.8+ install करें
2. ✅ Virtual environment बनाएं और activate करें
3. ✅ Dependencies install करें (`pip install -r requirements.txt`)
4. ✅ Tesseract OCR install और configure करें
5. ✅ Models train करें (`python -m src.models.train`)
6. ✅ System test करें (`python quick_start.py`)
7. ✅ Monitor चलाएं (`python monitor.py`)

**Total Time:** 15-30 minutes (first time)

**आपका system ready है! 🎉**

---

**Version:** 2.0  
**Last Updated:** 2025-12-26  
**Status:** Production Ready
