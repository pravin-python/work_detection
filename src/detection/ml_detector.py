"""
Machine Learning-based detection engine using Neural Network
Provides accurate detection using deep learning model
"""

from typing import Dict, List, Tuple
import pandas as pd
from datetime import datetime

from ..models.neural_network import NeuralNetworkDetector
from ..features.visual_features import VisualFeatureExtractor
from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class MLDetector:
    """
    ML-based fake work detector using Neural Network
    
    Features:
    - Uses deep learning neural network
    - Integrates keyboard, mouse, temporal, and visual features
    - Provides probability-based detection
    - More accurate than rule-based approach
    """
    
    def __init__(self, model_path=None):
        """
        Initialize ML detector
        
        Args:
            model_path: Path to saved neural network model
        """
        try:
            self.neural_net = NeuralNetworkDetector(model_path=model_path)
            self.visual_extractor = VisualFeatureExtractor()
            self.model_loaded = self.neural_net.load_model()
            
            if not self.model_loaded:
                logger.warning("Neural network model not found. Using rule-based fallback.")
                logger.warning("Train model first: python -m src.models.neural_network")
            
            logger.info("MLDetector initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MLDetector: {e}")
            self.model_loaded = False
            self.neural_net = None
            self.visual_extractor = VisualFeatureExtractor()
    
    def extract_all_features(
        self, 
        events: Dict, 
        screenshots: List[Dict] = None,
        window_seconds: int = 60
    ) -> pd.DataFrame:
        """
        Extract all features including visual features from screenshots
        
        Args:
            events: Dictionary with keyboard, mouse, window events
            screenshots: List of screenshot dictionaries
            window_seconds: Time window for analysis
        
        Returns:
            DataFrame with all features
        """
        from ..features.feature_extractor import FeatureExtractor
        
        # Extract standard features
        extractor = FeatureExtractor()
        features = extractor.extract_features(events, window_seconds)
        
        # Extract visual features if screenshots available
        if screenshots and len(screenshots) >= 2:
            try:
                # Get last two screenshots for comparison
                screenshot1 = screenshots[-2]
                screenshot2 = screenshots[-1]
                
                visual_features = self.visual_extractor.extract_visual_features(
                    screenshot1, screenshot2
                )
                features.update(visual_features)
                logger.debug("Visual features extracted from screenshots")
            except Exception as e:
                logger.warning(f"Failed to extract visual features: {e}")
        
        # Convert to DataFrame
        df = pd.DataFrame([features])
        
        # Get expected features from the model's scaler (if model is loaded)
        # This ensures we only use features that were in training data
        if self.model_loaded and self.neural_net and hasattr(self.neural_net.scaler, 'feature_names_in_'):
            expected_features = self.neural_net.scaler.feature_names_in_.tolist()
        else:
            # Fallback: use standard features only (visual features will be added later if model supports them)
            from ..utils.config import FEATURE_NAMES
            expected_features = FEATURE_NAMES.copy()
        
        # Ensure all expected features are present (fill missing with 0)
        for feat in expected_features:
            if feat not in df.columns:
                df[feat] = 0.0
        
        # Only keep features that were in training data
        # Remove any visual features if they weren't in training
        df = df[[f for f in expected_features if f in df.columns]]
        
        return df
    
    def detect(
        self, 
        features: pd.DataFrame,
        screenshots: List[Dict] = None,
        events: Dict = None
    ) -> Tuple[bool, float, List[str]]:
        """
        Detect fake work using neural network
        
        Args:
            features: Feature DataFrame (can be from extract_all_features)
            screenshots: Optional screenshots for visual features
            events: Optional events dict for activity check
        
        Returns:
            Tuple of (is_fake, confidence, reasons)
        """
        if not self.model_loaded or self.neural_net is None:
            # Fallback to rule-based if model not available
            logger.warning("Using rule-based fallback (neural network not available)")
            from .rule_based import RuleBasedDetector
            fallback = RuleBasedDetector()
            features_dict = features.iloc[0].to_dict()
            return fallback.detect(features_dict)
        
        try:
            # Ensure features are in correct format
            if isinstance(features, dict):
                features = pd.DataFrame([features])
            
            # Check minimum activity to reduce false positives
            from ..utils.config import MIN_ACTIVITY_FOR_ANALYSIS
            if events:
                total_events = (
                    len(events.get('keyboard', [])) + 
                    len(events.get('mouse', [])) + 
                    len(events.get('window', []))
                )
                
                if total_events < MIN_ACTIVITY_FOR_ANALYSIS:
                    # Too little activity - likely idle, not fake work
                    logger.debug(f"Insufficient activity ({total_events} events) - marking as genuine")
                    return False, 0.3, ["Insufficient activity for analysis"]
            
            # If screenshots provided, extract visual features
            # But only add them if the model was trained with them
            if screenshots and len(screenshots) >= 2:
                try:
                    screenshot1 = screenshots[-2]
                    screenshot2 = screenshots[-1]
                    visual_features = self.visual_extractor.extract_visual_features(
                        screenshot1, screenshot2
                    )
                    
                    # Check if model supports visual features
                    if self.neural_net and hasattr(self.neural_net.scaler, 'feature_names_in_'):
                        expected_features = set(self.neural_net.scaler.feature_names_in_)
                        # Only add visual features if they were in training
                        for key, value in visual_features.items():
                            if key in expected_features and key not in features.columns:
                                features[key] = value
                    else:
                        # Model not loaded or doesn't have feature names - skip visual features
                        logger.debug("Skipping visual features (not in training data)")
                except Exception as e:
                    logger.warning(f"Failed to add visual features: {e}")
            
            # Predict using neural network
            fake_probability, confidence = self.neural_net.predict(features)
            
            # Determine if fake (use higher threshold for better accuracy)
            from ..utils.config import ML_DETECTION_THRESHOLD
            threshold = ML_DETECTION_THRESHOLD
            is_fake = fake_probability > threshold
            
            # Generate reasons based on probability and features
            reasons = self._generate_reasons(fake_probability, confidence, features)
            
            logger.debug(f"ML Detection: fake_prob={fake_probability:.3f}, "
                        f"confidence={confidence:.3f}, is_fake={is_fake}")
            
            return is_fake, confidence, reasons
            
        except Exception as e:
            logger.error(f"Error in ML detection: {e}")
            # Fallback
            from .rule_based import RuleBasedDetector
            fallback = RuleBasedDetector()
            features_dict = features.iloc[0].to_dict()
            return fallback.detect(features_dict)
    
    def _generate_reasons(
        self, 
        fake_probability: float, 
        confidence: float,
        features: pd.DataFrame
    ) -> List[str]:
        """
        Generate human-readable reasons for detection
        
        Args:
            fake_probability: Probability of fake work
            confidence: Confidence in prediction
            features: Feature DataFrame
        
        Returns:
            List of reason strings
        """
        reasons = []
        
        if fake_probability > 0.8:
            reasons.append(f"High fake work probability ({fake_probability:.1%})")
        elif fake_probability > 0.6:
            reasons.append(f"Moderate fake work probability ({fake_probability:.1%})")
        
        # Check specific features
        feat_dict = features.iloc[0].to_dict()
        
        if feat_dict.get('repeat_key_ratio', 0) > 0.6:
            reasons.append("High key repetition detected")
        
        if feat_dict.get('mouse_curvature', 0.5) < 0.3:
            reasons.append("Linear mouse movement pattern")
        
        if feat_dict.get('keystroke_entropy', 0.5) < 0.2:
            reasons.append("Low keystroke entropy (bot-like)")
        
        if feat_dict.get('screen_similarity_score', 1.0) > 0.98:
            reasons.append("Screen unchanged (no visual progress)")
        
        if feat_dict.get('visual_entropy', 0) < 2.0:
            reasons.append("Low visual complexity")
        
        if not reasons:
            if fake_probability > 0.5:
                reasons.append("Neural network detected suspicious patterns")
            else:
                reasons.append("Patterns appear genuine")
        
        return reasons
    
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
            if confidence >= 0.8:
                return "GENUINE_WORK (HIGH CONFIDENCE)"
            elif confidence >= 0.5:
                return "GENUINE_WORK (MEDIUM CONFIDENCE)"
            else:
                return "GENUINE_WORK"
    
    def generate_report(
        self, 
        features: Dict[str, float] = None,
        events: Dict = None,
        screenshots: List[Dict] = None,
        user_id: str = "USER_001"
    ) -> Dict:
        """
        Generate a detection report using ML model
        
        Args:
            features: Feature dictionary (optional, will extract if not provided)
            events: Events dictionary (required if features not provided)
            screenshots: List of screenshots (optional)
            user_id: User identifier
        
        Returns:
            Detection report dictionary
        """
        # Extract features if not provided
        if features is None:
            if events is None:
                raise ValueError("Either features or events must be provided")
            
            features_df = self.extract_all_features(events, screenshots)
        else:
            features_df = pd.DataFrame([features])
        
        # Detect
        is_fake, confidence, reasons = self.detect(features_df, screenshots, events)
        decision = self.get_decision_label(is_fake, confidence)
        
        # Determine confidence level
        if confidence >= 0.8:
            confidence_level = "HIGH"
        elif confidence >= 0.5:
            confidence_level = "MEDIUM"
        else:
            confidence_level = "LOW"
        
        # Get feature values
        feat_dict = features_df.iloc[0].to_dict()
        
        report = {
            "user_id": user_id,
            "timestamp": datetime.now().isoformat(),
            "fake_probability": confidence if is_fake else (1.0 - confidence),
            "decision": decision,
            "confidence": confidence_level,
            "reasons": reasons,
            "model_type": "neural_network" if self.model_loaded else "rule_based_fallback",
            "feature_scores": {
                "keystroke_entropy": feat_dict.get('keystroke_entropy', 0.0),
                "mouse_curvature": feat_dict.get('mouse_curvature', 0.0),
                "repeat_key_ratio": feat_dict.get('repeat_key_ratio', 0.0),
                "screen_similarity_score": feat_dict.get('screen_similarity_score', 0.0),
                "visual_entropy": feat_dict.get('visual_entropy', 0.0),
            }
        }
        
        return report


# Standalone test
if __name__ == "__main__":
    from ..utils.data_simulator import DataSimulator
    
    print("Testing MLDetector...")
    
    detector = MLDetector()
    
    if not detector.model_loaded:
        print("⚠️  Neural network model not found!")
        print("Train model first: python -m src.models.neural_network")
    else:
        print("✅ Neural network model loaded")
        
        # Generate test features
        simulator = DataSimulator()
        X, y = simulator.generate_training_data(10, 10)
        
        # Test detection
        for idx in range(5):
            features = X.iloc[idx:idx+1]
            is_fake, confidence, reasons = detector.detect(features)
            
            print(f"\nSample {idx+1} (actual: {'FAKE' if y.iloc[idx] else 'GENUINE'}):")
            print(f"  Detected: {'FAKE' if is_fake else 'GENUINE'}")
            print(f"  Confidence: {confidence:.3f}")
            print(f"  Reasons: {', '.join(reasons[:2])}")

