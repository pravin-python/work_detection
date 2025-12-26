# 🚀 Real-Time Monitor - Usage Guide

## क्या है यह?

यह एक **continuous background monitor** है जो:

- ✅ एक बार start करने के बाद चलता रहता है
- ✅ हर 1 minute में आपके work को analyze करता है
- ✅ Fake work detect करता है automatically
- ✅ जब तक आप work करते हैं, तब तक चलता रहता है
- ✅ Ctrl+C से stop हो जाता है

---

## 🎯 कैसे चलाएं?

### सबसे आसान तरीका

```bash
python monitor.py
```

**बस इतना ही!** Monitor start हो जाएगा और background में चलता रहेगा।

---

## 📊 क्या होगा?

### जब Monitor चालू होगा

```
🧠 REAL-TIME WORK DETECTION MONITOR
======================================================================

✅ Monitor started at 2025-12-26 19:15:00
📊 Analysis interval: 60 seconds
👤 User ID: USER_001
📁 Reports saved to: data\reports

💡 The monitor is now running in the background...
   It will analyze your work patterns every minute.
   Press Ctrl+C to stop.

======================================================================
```

### हर 1 Minute में

**अगर Genuine Work है:**

```
[19:16:00] ✅ Genuine work detected
[19:17:00] ✅ Genuine work detected
[19:18:00] ✅ Genuine work detected
```

**अगर Fake Work है:**

```
[19:19:00] ⚠️  FAKE WORK DETECTED!
           Confidence: HIGH
           Probability: 87.5%
           Reasons: Excessive key repetition, Activity spike
```

---

## 🛑 कैसे बंद करें?

बस **Ctrl+C** दबाएं। Monitor gracefully बंद हो जाएगा और summary दिखाएगा:

```
📊 MONITORING SUMMARY
======================================================================

Total analyses: 45
✅ Genuine work: 38 (84.4%)
⚠️  Fake work: 7 (15.6%)

📁 Reports saved to: data\reports

======================================================================
✅ Monitor stopped successfully
======================================================================
```

---

## 📁 Reports कहाँ Save होती हैं?

सभी detection reports यहाँ save होती हैं:

```
data/reports/report_20251226_191500.json
data/reports/report_20251226_191600.json
data/reports/report_20251226_191700.json
...
```

### Report Format

```json
{
  "user_id": "USER_001",
  "timestamp": "2025-12-26T19:15:00",
  "decision": "FAKE_WORK (HIGH CONFIDENCE)",
  "fake_probability": 0.875,
  "confidence": "HIGH",
  "reasons": [
    "Excessive key repetition (0.71)",
    "Suspicious activity spike (1.00)"
  ]
}
```

---

## ⚙️ Settings बदलना

### Analysis Interval बदलना

`monitor.py` में edit करें:

```python
monitor = RealtimeMonitor(
    analysis_interval=30,  # 30 seconds (default: 60)
    user_id="USER_001"
)
```

### User ID बदलना

```python
monitor = RealtimeMonitor(
    analysis_interval=60,
    user_id="PRAVIN_001"  # अपना नाम डालें
)
```

---

## 🎯 Use Cases

### 1. पूरे दिन Monitor करना

```bash
# सुबह start करें
python monitor.py

# शाम को Ctrl+C से बंद करें
```

### 2. Background में चलाना (Windows)

```powershell
# Background में start करें
Start-Process python -ArgumentList "monitor.py" -WindowStyle Hidden

# या
pythonw monitor.py  # No console window
```

### 3. Startup पर Auto-Start

**Windows:**

1. `monitor.py` का shortcut बनाएं
2. `shell:startup` folder में रखें
3. Restart करें - auto-start होगा!

---

## 🔍 Logs देखना

सभी logs यहाँ save होते हैं:

```
work_detection.log
```

### Logs देखने के लिए

```bash
# Windows
type work_detection.log

# Linux/macOS
tail -f work_detection.log
```

---

## ⚡ Quick Commands

```bash
# Monitor start करें
python monitor.py

# Monitor बंद करें
Ctrl+C

# Reports देखें
dir data\reports

# Latest report देखें
type data\reports\report_*.json | Select-Object -Last 1

# Logs देखें
type work_detection.log
```

---

## 🆚 Quick Start vs Monitor

| Feature | quick_start.py | monitor.py |
|---------|----------------|------------|
| **Duration** | 30 seconds | Continuous |
| **Purpose** | Demo/Test | Real monitoring |
| **Output** | One report | Multiple reports |
| **Use Case** | Testing | Production |

---

## 💡 Tips

1. **सुबह start करें**: जब work शुरू करें, monitor start कर दें
2. **शाम को बंद करें**: Work खत्म होने पर Ctrl+C
3. **Reports check करें**: हर शाम reports देखें
4. **Logs monitor करें**: अगर कुछ गड़बड़ लगे तो logs देखें

---

## 🐛 Troubleshooting

### Monitor बंद नहीं हो रहा?

```bash
# Force stop
Ctrl+C (2-3 बार दबाएं)
```

### Reports नहीं बन रहीं?

```bash
# Check permissions
mkdir data\reports
```

### बहुत ज्यादा Fake Work detect हो रहा?

```python
# config.py में thresholds कम करें
RULE_THRESHOLDS = {
    'repeat_key_ratio': 0.8,  # 0.7 से बढ़ाएं
    'idle_spike_threshold': 0.9,  # 0.8 से बढ़ाएं
}
```

---

## ✅ Summary

**एक बार चलाएं:**

```bash
python monitor.py
```

**Monitor:**

- ✅ Background में चलता रहेगा
- ✅ हर minute analyze करेगा
- ✅ Fake work detect करेगा
- ✅ Reports save करेगा
- ✅ Ctrl+C से बंद होगा

**बस इतना ही! आसान है! 🎉**
