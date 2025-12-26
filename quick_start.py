"""
Quick Start Demo for Work Detection System
Demonstrates data collection, feature extraction, and rule-based detection
"""

import time
import json
from datetime import datetime
from pathlib import Path

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.collectors.unified_collector import UnifiedCollector
from src.features.feature_extractor import FeatureExtractor
from src.detection.rule_based import RuleBasedDetector
from src.utils.logger import setup_logger
from src.utils.config import LOG_FILE, COLLECTION_WINDOW_SECONDS

# Setup logger
logger = setup_logger("quick_start", LOG_FILE, "INFO")


def print_banner():
    """Print welcome banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🧠 FAKE vs REAL WORK DETECTION SYSTEM 🧠             ║
    ║                                                              ║
    ║              Real-time Behavioral Analysis                   ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_section(title: str):
    """Print section header"""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def demo_data_collection(duration: int = 30):
    """
    Demo: Collect data for specified duration
    
    Args:
        duration: Collection duration in seconds
    """
    print_section("📊 PHASE 1: Data Collection")
    
    print(f"Starting data collection for {duration} seconds...")
    print("Please perform various activities:")
    print("  • Type some text")
    print("  • Move your mouse")
    print("  • Click around")
    print("  • Switch between windows")
    print("\nCollection starting in 3 seconds...\n")
    
    time.sleep(3)
    
    collector = UnifiedCollector()
    collector.start()
    
    # Show progress
    for i in range(duration):
        time.sleep(1)
        if (i + 1) % 5 == 0:
            summary = collector.get_summary()
            print(f"[{i+1}s] Events collected: {summary['total_events']} "
                  f"(KB: {summary['keyboard_events']}, "
                  f"Mouse: {summary['mouse_events']}, "
                  f"Window: {summary['window_events']})")
    
    collector.stop()
    
    # Get final summary
    summary = collector.get_summary()
    print(f"\n✅ Collection complete!")
    print(f"   Total events: {summary['total_events']}")
    print(f"   Keyboard: {summary['keyboard_events']}")
    print(f"   Mouse: {summary['mouse_events']}")
    print(f"   Window: {summary['window_events']}")
    print(f"   Events/sec: {summary['events_per_second']:.2f}")
    
    # Get events
    events = collector.get_all_events()
    
    return events


def demo_feature_extraction(events):
    """
    Demo: Extract features from collected events
    
    Args:
        events: Dictionary of collected events
    """
    print_section("🔬 PHASE 2: Feature Extraction")
    
    print("Extracting behavioral features...")
    
    extractor = FeatureExtractor()
    features = extractor.extract_features(events, window_seconds=COLLECTION_WINDOW_SECONDS)
    
    print(f"\n✅ Extracted {len(features)} features\n")
    
    # Display features by category
    print("📌 Keyboard Features:")
    keyboard_features = [
        'keys_per_minute', 'unique_key_ratio', 'repeat_key_ratio',
        'keystroke_entropy', 'shortcut_abuse_score', 'burst_typing_score'
    ]
    for feat in keyboard_features:
        if feat in features:
            print(f"   {feat:.<40} {features[feat]:.4f}")
    
    print("\n📌 Mouse Features:")
    mouse_features = [
        'mouse_distance', 'mouse_velocity_avg', 'mouse_curvature',
        'mouse_jitter_score', 'mouse_entropy', 'click_frequency'
    ]
    for feat in mouse_features:
        if feat in features:
            print(f"   {feat:.<40} {features[feat]:.4f}")
    
    print("\n📌 Temporal Features:")
    temporal_features = [
        'idle_seconds', 'active_seconds', 'activity_spike_score',
        'periodic_behavior_score', 'input_diversity_score'
    ]
    for feat in temporal_features:
        if feat in features:
            print(f"   {feat:.<40} {features[feat]:.4f}")
    
    print("\n📌 Context Features:")
    context_features = [
        'window_switch_count', 'active_app_duration', 'unique_apps_count'
    ]
    for feat in context_features:
        if feat in features:
            print(f"   {feat:.<40} {features[feat]:.4f}")
    
    return features


def demo_detection(features):
    """
    Demo: Detect fake work using rule-based detector
    
    Args:
        features: Feature dictionary
    """
    print_section("🎯 PHASE 3: Fake Work Detection")
    
    print("Running rule-based detection engine...\n")
    
    detector = RuleBasedDetector()
    report = detector.generate_report(features)
    
    # Display report
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║                     DETECTION REPORT                         ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")
    
    print(f"User ID:           {report['user_id']}")
    print(f"Timestamp:         {report['timestamp']}")
    print(f"Decision:          {report['decision']}")
    print(f"Confidence:        {report['confidence']}")
    print(f"Fake Probability:  {report['fake_probability']:.2%}")
    
    print(f"\n📋 Reasons ({len(report['reasons'])}):")
    if report['reasons']:
        for i, reason in enumerate(report['reasons'], 1):
            print(f"   {i}. {reason}")
    else:
        print("   ✅ No suspicious patterns detected")
    
    print(f"\n📊 Key Feature Scores:")
    for key, value in report['feature_scores'].items():
        print(f"   {key:.<40} {value:.4f}")
    
    # Save report
    report_path = Path("data") / "detection_report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Report saved to: {report_path}")
    
    return report


def main():
    """Main demo function"""
    print_banner()
    
    print("This demo will:")
    print("  1. Collect your keyboard, mouse, and window activity")
    print("  2. Extract behavioral features")
    print("  3. Detect if the activity appears genuine or fake")
    print("\n⚠️  Note: This is for demonstration purposes only.")
    print("    Perform NORMAL work activities for best results.\n")
    
    input("Press ENTER to start the demo...")
    
    try:
        # Phase 1: Data Collection
        events = demo_data_collection(duration=30)
        
        # Phase 2: Feature Extraction
        features = demo_feature_extraction(events)
        
        # Phase 3: Detection
        report = demo_detection(features)
        
        # Final summary
        print_section("✨ DEMO COMPLETE")
        
        if "FAKE" in report['decision']:
            print("⚠️  WARNING: Suspicious activity detected!")
            print("    The system identified patterns consistent with fake work.")
        else:
            print("✅ Activity appears genuine!")
            print("    No suspicious patterns were detected.")
        
        print("\n📚 Next Steps:")
        print("   • Train ML models: python -m src.models.train")
        print("   • Run real-time detection: python -m src.detection.ml_detector --realtime")
        print("   • View documentation: README.md")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        logger.error(f"Error during demo: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
    
    print("\n" + "="*70)
    print("Thank you for trying the Work Detection System!")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
