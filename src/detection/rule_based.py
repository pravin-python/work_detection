"""
Rule-based detection engine
Provides immediate detection using deterministic rules
"""

from typing import Dict, List, Tuple
import json

from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE, RULE_THRESHOLDS

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class RuleBasedDetector:
    """Rule-based fake work detector"""
    
    def __init__(self, thresholds: Dict[str, float] = None):
        """
        Initialize rule-based detector
        
        Args:
            thresholds: Custom thresholds (uses defaults if None)
        """
        self.thresholds = thresholds or RULE_THRESHOLDS
        logger.info(f"RuleBasedDetector initialized with thresholds: {self.thresholds}")
    
    def detect(self, features: Dict[str, float]) -> Tuple[bool, float, List[str]]:
        """
        Detect fake work using rules
        
        Args:
            features: Feature dictionary
        
        Returns:
            Tuple of (is_fake, confidence, reasons)
        """
        violations = []
        violation_scores = []
        
        # Rule 1: Excessive key repetition
        if features.get('repeat_key_ratio', 0) > self.thresholds['repeat_key_ratio']:
            violations.append(f"Excessive key repetition ({features['repeat_key_ratio']:.2f})")
            violation_scores.append(features['repeat_key_ratio'])
        
        # Rule 2: Linear mouse movement (bot-like)
        mouse_curvature = features.get('mouse_curvature', 0.5)
        if mouse_curvature < (1.0 - self.thresholds['mouse_linearity']):
            violations.append(f"Linear mouse movement detected (curvature: {mouse_curvature:.2f})")
            violation_scores.append(1.0 - mouse_curvature)
        
        # Rule 3: Shortcut abuse
        if features.get('shortcut_abuse_score', 0) > self.thresholds['shortcut_abuse_ratio']:
            violations.append(f"Shortcut abuse detected ({features['shortcut_abuse_score']:.2f})")
            violation_scores.append(features['shortcut_abuse_score'])
        
        # Rule 4: Activity spike (idle timeout gaming)
        if features.get('activity_spike_score', 0) > self.thresholds['idle_spike_threshold']:
            violations.append(f"Suspicious activity spike ({features['activity_spike_score']:.2f})")
            violation_scores.append(features['activity_spike_score'])
        
        # Rule 5: Very low entropy (bot-like)
        keystroke_entropy = features.get('keystroke_entropy', 0.5)
        mouse_entropy = features.get('mouse_entropy', 0.5)
        avg_entropy = (keystroke_entropy + mouse_entropy) / 2.0
        
        if avg_entropy < self.thresholds['zero_entropy_threshold']:
            violations.append(f"Very low behavioral entropy ({avg_entropy:.2f})")
            violation_scores.append(1.0 - avg_entropy)
        
        # Rule 6: High mouse jitter (mouse mover bot)
        if features.get('mouse_jitter_score', 0) > 0.7:
            violations.append(f"High mouse jitter detected ({features['mouse_jitter_score']:.2f})")
            violation_scores.append(features['mouse_jitter_score'])
        
        # Rule 7: Periodic behavior (bot-like)
        if features.get('periodic_behavior_score', 0) > 0.8:
            violations.append(f"Periodic behavior detected ({features['periodic_behavior_score']:.2f})")
            violation_scores.append(features['periodic_behavior_score'])
        
        # Rule 8: No input diversity (only one type of input)
        if features.get('input_diversity_score', 1.0) < 0.4:
            violations.append(f"Low input diversity ({features['input_diversity_score']:.2f})")
            violation_scores.append(1.0 - features['input_diversity_score'])
        
        # Determine if fake
        is_fake = len(violations) >= 2  # At least 2 violations = fake
        
        # Calculate confidence based on number and severity of violations
        if violation_scores:
            confidence = min(sum(violation_scores) / len(violation_scores), 1.0)
        else:
            confidence = 0.0
        
        if is_fake:
            logger.info(f"FAKE WORK DETECTED - {len(violations)} violations, confidence: {confidence:.2f}")
            for violation in violations:
                logger.info(f"  - {violation}")
        
        return is_fake, confidence, violations
    
    def get_decision_label(self, is_fake: bool, confidence: float) -> str:
        """
        Get decision label based on detection result
        
        Args:
            is_fake: Whether fake work was detected
            confidence: Confidence score
        
        Returns:
            Decision label string
        """
        if is_fake:
            if confidence >= 0.8:
                return "FAKE_WORK (HIGH CONFIDENCE)"
            elif confidence >= 0.5:
                return "FAKE_WORK (MEDIUM CONFIDENCE)"
            else:
                return "SUSPICIOUS"
        else:
            return "GENUINE_WORK"
    
    def generate_report(self, features: Dict[str, float], user_id: str = "USER_001") -> Dict:
        """
        Generate a detection report
        
        Args:
            features: Feature dictionary
            user_id: User identifier
        
        Returns:
            Detection report dictionary
        """
        from datetime import datetime
        
        is_fake, confidence, reasons = self.detect(features)
        decision = self.get_decision_label(is_fake, confidence)
        
        # Determine confidence level
        if confidence >= 0.8:
            confidence_level = "HIGH"
        elif confidence >= 0.5:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        report = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "fake_probability": confidence if is_fake else (1.0 - confidence),
            "decision": decision,
            "confidence": confidence_level,
            "reasons": reasons,
            "feature_scores": {
                "keystroke_entropy": features.get('keystroke_entropy', 0.0),
                "mouse_curvature": features.get('mouse_curvature', 0.0),
                "shortcut_abuse_score": features.get('shortcut_abuse_score', 0.0),
                "activity_spike_score": features.get('activity_spike_score', 0.0),
                "periodic_behavior_score": features.get('periodic_behavior_score', 0.0),
            }
        }
        
        return report


# Standalone test
if __name__ == "__main__":
    # Test with fake work features
    fake_features = {
        'repeat_key_ratio': 0.9,  # High repetition
        'mouse_curvature': 0.05,  # Very linear
        'shortcut_abuse_score': 0.7,  # High shortcuts
        'activity_spike_score': 0.85,  # Spike detected
        'keystroke_entropy': 0.05,  # Very low
        'mouse_entropy': 0.08,
        'mouse_jitter_score': 0.8,  # High jitter
        'periodic_behavior_score': 0.9,  # Very periodic
        'input_diversity_score': 0.3,  # Low diversity
    }
    
    # Test with genuine work features
    genuine_features = {
        'repeat_key_ratio': 0.2,
        'mouse_curvature': 0.6,
        'shortcut_abuse_score': 0.1,
        'activity_spike_score': 0.2,
        'keystroke_entropy': 0.7,
        'mouse_entropy': 0.65,
        'mouse_jitter_score': 0.1,
        'periodic_behavior_score': 0.2,
        'input_diversity_score': 0.9,
    }
    
    detector = RuleBasedDetector()
    
    print("=" * 60)
    print("Testing FAKE WORK features:")
    print("=" * 60)
    report = detector.generate_report(fake_features)
    print(json.dumps(report, indent=2))
    
    print("\n" + "=" * 60)
    print("Testing GENUINE WORK features:")
    print("=" * 60)
    report = detector.generate_report(genuine_features)
    print(json.dumps(report, indent=2))
