"""
Real-time continuous work detection monitor
Runs in background and continuously analyzes work patterns
"""

import time
import signal
import sys
from datetime import datetime
from pathlib import Path

from src.collectors.unified_collector import UnifiedCollector
from src.features.feature_extractor import FeatureExtractor
from src.detection.ml_detector import MLDetector
from src.utils.logger import setup_logger
from src.utils.config import (
    LOG_LEVEL, LOG_FILE, 
    REALTIME_WINDOW_SECONDS,
    DEFAULT_USER_ID,
    DATA_DIR
)

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class RealtimeMonitor:
    """
    Real-time continuous work detection monitor
    
    Features:
    - Runs continuously in background
    - Analyzes work patterns every 60 seconds
    - Logs fake work detections
    - Saves reports automatically
    - Graceful shutdown on Ctrl+C
    """
    
    def __init__(
        self, 
        analysis_interval: int = REALTIME_WINDOW_SECONDS,
        user_id: str = DEFAULT_USER_ID
    ):
        """
        Initialize real-time monitor
        
        Args:
            analysis_interval: Seconds between analyses (default: 60)
            user_id: User identifier
        """
        self.analysis_interval = analysis_interval
        self.user_id = user_id
        self.is_running = False
        
        # Initialize components
        self.collector = UnifiedCollector()
        self.extractor = FeatureExtractor()
        # Use ML detector (neural network) for better accuracy
        self.detector = MLDetector()
        
        # Statistics
        self.total_analyses = 0
        self.fake_detections = 0
        self.genuine_detections = 0
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        logger.info("RealtimeMonitor initialized")
    
    def _signal_handler(self, sig, frame):
        """Handle Ctrl+C gracefully"""
        print("\n\n🛑 Stopping monitor...")
        self.stop()
        sys.exit(0)
    
    def start(self):
        """Start real-time monitoring"""
        if self.is_running:
            logger.warning("Monitor is already running")
            return
        
        print("\n" + "="*70)
        print("🧠 REAL-TIME WORK DETECTION MONITOR")
        print("="*70)
        print(f"\n✅ Monitor started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Analysis interval: {self.analysis_interval} seconds")
        print(f"👤 User ID: {self.user_id}")
        print(f"📁 Reports saved to: {DATA_DIR / 'reports'}")
        print("\n💡 The monitor is now running in the background...")
        print("   It will analyze your work patterns every minute.")
        print("   Press Ctrl+C to stop.\n")
        print("="*70 + "\n")
        
        self.is_running = True
        self.collector.start()
        logger.info("Real-time monitoring started")
        
        # Main monitoring loop
        try:
            while self.is_running:
                time.sleep(self.analysis_interval)
                self._analyze_current_window()
        
        except KeyboardInterrupt:
            self.stop()
    
    def _analyze_current_window(self):
        """Analyze current time window"""
        try:
            # Get events from last window (includes screenshots)
            events = self.collector.get_all_events(
                window_seconds=self.analysis_interval
            )
            
            # Get screenshots for visual analysis
            screenshots = events.get('screenshots', [])
            
            # Check minimum activity before analysis (reduces false positives)
            from src.utils.config import MIN_ACTIVITY_FOR_ANALYSIS
            total_events = (
                len(events.get('keyboard', [])) + 
                len(events.get('mouse', [])) + 
                len(events.get('window', []))
            )
            
            if total_events < MIN_ACTIVITY_FOR_ANALYSIS:
                logger.debug(f"Skipping analysis - insufficient activity ({total_events} events)")
                return
            
            # Generate report using ML detector (includes visual features)
            report = self.detector.generate_report(
                events=events,
                screenshots=screenshots,
                user_id=self.user_id
            )
            
            # Update statistics
            self.total_analyses += 1
            
            if "FAKE" in report['decision']:
                self.fake_detections += 1
                self._handle_fake_detection(report)
            else:
                self.genuine_detections += 1
                self._handle_genuine_detection(report)
            
            # Save report
            self._save_report(report)
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
    
    def _handle_fake_detection(self, report):
        """Handle fake work detection"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"[{timestamp}] ⚠️  FAKE WORK DETECTED!")
        print(f"           Confidence: {report['confidence']}")
        print(f"           Probability: {report['fake_probability']:.1%}")
        print(f"           Reasons: {', '.join(report['reasons'][:2])}")
        
        logger.warning(f"FAKE WORK DETECTED: {report['decision']}")
        logger.warning(f"Reasons: {report['reasons']}")
    
    def _handle_genuine_detection(self, report):
        """Handle genuine work detection"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        
        print(f"[{timestamp}] ✅ Genuine work detected")
        
        logger.info(f"Genuine work: {report['decision']}")
    
    def _save_report(self, report):
        """Save detection report to file"""
        try:
            import json
            
            # Create reports directory
            reports_dir = DATA_DIR / "reports"
            reports_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"report_{timestamp}.json"
            filepath = reports_dir / filename
            
            # Save report
            with open(filepath, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.debug(f"Report saved to {filepath}")
        
        except Exception as e:
            logger.error(f"Failed to save report: {e}")
    
    def stop(self):
        """Stop monitoring"""
        if not self.is_running:
            return
        
        self.is_running = False
        self.collector.stop()
        
        # Print summary
        print("\n" + "="*70)
        print("📊 MONITORING SUMMARY")
        print("="*70)
        print(f"\nTotal analyses: {self.total_analyses}")
        print(f"✅ Genuine work: {self.genuine_detections} ({self.genuine_detections/max(self.total_analyses,1)*100:.1f}%)")
        print(f"⚠️  Fake work: {self.fake_detections} ({self.fake_detections/max(self.total_analyses,1)*100:.1f}%)")
        print(f"\n📁 Reports saved to: {DATA_DIR / 'reports'}")
        print("\n" + "="*70)
        print("✅ Monitor stopped successfully")
        print("="*70 + "\n")
        
        logger.info("Real-time monitoring stopped")


def main():
    """Main entry point"""
    print("\n🚀 Starting Real-Time Work Detection Monitor...\n")
    
    # Create monitor
    monitor = RealtimeMonitor(
        analysis_interval=60,  # Analyze every 60 seconds
        user_id="USER_001"
    )
    
    # Start monitoring (runs until Ctrl+C)
    monitor.start()


if __name__ == "__main__":
    main()
