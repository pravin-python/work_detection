"""
Model evaluation module
Evaluates trained models on test data and generates performance reports
"""

import numpy as np
import pandas as pd
import joblib
from pathlib import Path
import json

from ..utils.data_simulator import DataSimulator
from ..utils.logger import setup_logger
from ..utils.config import LOG_LEVEL, LOG_FILE, MODELS_DIR

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class ModelEvaluator:
    """Evaluate trained models"""
    
    def __init__(self):
        self.simulator = DataSimulator()
        logger.info("ModelEvaluator initialized")
    
    def load_models(self):
        """Load all trained models"""
        models = {}
        
        # Load Random Forest
        rf_path = MODELS_DIR / "random_forest_model.joblib"
        if rf_path.exists():
            models['random_forest'] = joblib.load(rf_path)
            logger.info("Loaded Random Forest model")
        else:
            logger.warning(f"Random Forest model not found at {rf_path}")
        
        # Load XGBoost
        xgb_path = MODELS_DIR / "xgboost_model.joblib"
        if xgb_path.exists():
            try:
                models['xgboost'] = joblib.load(xgb_path)
                logger.info("Loaded XGBoost model")
            except Exception as e:
                logger.warning(f"Failed to load XGBoost model: {e}")
                logger.warning("XGBoost may not be installed or model is incompatible")
        else:
            logger.warning(f"XGBoost model not found at {xgb_path}")
        
        # Load Isolation Forest
        iso_path = MODELS_DIR / "isolation_forest_model.joblib"
        if iso_path.exists():
            models['isolation_forest'] = joblib.load(iso_path)
            logger.info("Loaded Isolation Forest model")
        else:
            logger.warning(f"Isolation Forest model not found at {iso_path}")
        
        # Load scaler
        scaler_path = MODELS_DIR / "feature_scaler.joblib"
        if scaler_path.exists():
            scaler = joblib.load(scaler_path)
            logger.info("Loaded feature scaler")
        else:
            logger.warning(f"Feature scaler not found at {scaler_path}")
            scaler = None
        
        return models, scaler
    
    def generate_test_data(self, num_samples: int = 100):
        """Generate fresh test data"""
        logger.info(f"Generating {num_samples} test samples...")
        X, y = self.simulator.generate_training_data(
            num_genuine=num_samples // 2,
            num_fake=num_samples // 2
        )
        return X, y
    
    def evaluate_model(self, model, X_test, y_test, model_name: str):
        """Evaluate a single model"""
        from sklearn.metrics import (
            accuracy_score, precision_score, recall_score, f1_score,
            confusion_matrix, classification_report
        )
        
        logger.info(f"\nEvaluating {model_name}...")
        
        # Predict
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        
        # Confusion matrix
        cm = confusion_matrix(y_test, y_pred)
        
        # Classification report
        report = classification_report(y_test, y_pred)
        
        logger.info(f"{model_name} Metrics:")
        logger.info(f"  Accuracy:  {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1 Score:  {f1:.4f}")
        logger.info(f"\nConfusion Matrix:\n{cm}")
        logger.info(f"\nClassification Report:\n{report}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1,
            'confusion_matrix': cm.tolist(),
            'classification_report': report
        }
    
    def evaluate_all_models(self, num_test_samples: int = 100):
        """Evaluate all trained models"""
        logger.info("="*70)
        logger.info("MODEL EVALUATION")
        logger.info("="*70)
        
        # Load models
        models, scaler = self.load_models()
        
        if not models:
            logger.error("No models found! Train models first with: python -m src.models.train")
            return None
        
        # Generate test data
        X_test, y_test = self.generate_test_data(num_test_samples)
        
        # Scale features
        if scaler:
            X_test_scaled = scaler.transform(X_test)
            X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)
        else:
            logger.warning("No scaler found, using unscaled features")
            X_test_scaled = X_test
        
        # Evaluate each model
        results = {}
        
        for model_name, model in models.items():
            if model_name == 'isolation_forest':
                logger.info(f"\nSkipping {model_name} (unsupervised, no labels)")
                continue
            
            results[model_name] = self.evaluate_model(
                model, X_test_scaled, y_test, model_name
            )
        
        # Print summary
        self._print_summary(results, num_test_samples)
        
        return results
    
    def _print_summary(self, results, num_samples):
        """Print evaluation summary"""
        print("\n" + "="*70)
        print("EVALUATION SUMMARY")
        print("="*70)
        print(f"\nTest Set: {num_samples} samples ({num_samples//2} genuine, {num_samples//2} fake)")
        
        for model_name, metrics in results.items():
            print(f"\n📊 {model_name.replace('_', ' ').title()} Performance:")
            print(f"   Accuracy............ {metrics['accuracy']:.4f}")
            print(f"   Precision........... {metrics['precision']:.4f}")
            print(f"   Recall.............. {metrics['recall']:.4f}")
            print(f"   F1 Score............ {metrics['f1_score']:.4f}")
            
            # Show confusion matrix
            cm = metrics['confusion_matrix']
            print(f"\n   Confusion Matrix:")
            print(f"   [[{cm[0][0]:3d}  {cm[0][1]:3d}]  ← Genuine")
            print(f"    [{cm[1][0]:3d}  {cm[1][1]:3d}]]  ← Fake")
            print(f"     ↑    ↑")
            print(f"     G    F")
        
        # Compare models
        if len(results) > 1:
            print(f"\n🏆 Best Model by Metric:")
            best_accuracy = max(results.items(), key=lambda x: x[1]['accuracy'])
            best_f1 = max(results.items(), key=lambda x: x[1]['f1_score'])
            print(f"   Accuracy: {best_accuracy[0]} ({best_accuracy[1]['accuracy']:.4f})")
            print(f"   F1 Score: {best_f1[0]} ({best_f1[1]['f1_score']:.4f})")
        
        print("\n" + "="*70)


def main():
    """Main evaluation function"""
    print("🧠 Work Detection System - Model Evaluation")
    print("="*70 + "\n")
    
    evaluator = ModelEvaluator()
    
    # Evaluate with 200 test samples
    results = evaluator.evaluate_all_models(num_test_samples=200)
    
    if results:
        print("\n✅ Evaluation complete!")
        print("\nNext steps:")
        print("  • Run detection: python quick_start.py")
        print("  • Test individual modules: python -m src.collectors.keyboard_collector")
    else:
        print("\n❌ Evaluation failed!")
        print("Train models first: python -m src.models.train")


if __name__ == "__main__":
    main()
