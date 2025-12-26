"""
Machine Learning model training module
Trains Random Forest, XGBoost, and Isolation Forest models
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, IsolationForest
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, precision_score, recall_score, f1_score
import joblib
from pathlib import Path

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

from ..utils.data_simulator import DataSimulator
from ..utils.logger import setup_logger
from ..utils.config import (
    LOG_LEVEL, LOG_FILE, MODELS_DIR, PROCESSED_DATA_DIR,
    RF_PARAMS, XGB_PARAMS, IFOREST_PARAMS, TRAIN_TEST_SPLIT, RANDOM_SEED
)

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class ModelTrainer:
    """Train and evaluate ML models for fake work detection"""
    
    def __init__(self):
        self.simulator = DataSimulator()
        self.scaler = StandardScaler()
        self.models = {}
        
        logger.info("ModelTrainer initialized")
    
    def generate_or_load_data(self, num_genuine: int = 500, num_fake: int = 500, force_generate: bool = False):
        """
        Generate or load training data
        
        Args:
            num_genuine: Number of genuine samples
            num_fake: Number of fake samples
            force_generate: Force regeneration even if data exists
        
        Returns:
            Tuple of (X, y)
        """
        data_path = PROCESSED_DATA_DIR / "training_data.csv"
        
        if data_path.exists() and not force_generate:
            logger.info(f"Loading existing training data from {data_path}")
            df = pd.read_csv(data_path)
            X = df.drop('label', axis=1)
            y = df['label']
        else:
            logger.info("Generating new training data...")
            X, y = self.simulator.generate_training_data(num_genuine, num_fake)
            
            # Save for future use
            df = X.copy()
            df['label'] = y
            data_path.parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(data_path, index=False)
            logger.info(f"Training data saved to {data_path}")
        
        logger.info(f"Data shape: {X.shape}, Labels: {y.value_counts().to_dict()}")
        
        return X, y
    
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """Train Random Forest classifier"""
        logger.info("Training Random Forest model...")
        
        rf_model = RandomForestClassifier(**RF_PARAMS)
        rf_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = rf_model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred, "Random Forest")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': rf_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info(f"Top 10 important features:\n{feature_importance.head(10)}")
        
        self.models['random_forest'] = rf_model
        
        return rf_model, metrics, feature_importance
    
    def train_xgboost(self, X_train, y_train, X_test, y_test):
        """Train XGBoost classifier"""
        if not XGBOOST_AVAILABLE:
            logger.warning("XGBoost not available, skipping...")
            return None, None, None
        
        logger.info("Training XGBoost model...")
        
        xgb_model = xgb.XGBClassifier(**XGB_PARAMS)
        xgb_model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = xgb_model.predict(X_test)
        metrics = self._calculate_metrics(y_test, y_pred, "XGBoost")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': X_train.columns,
            'importance': xgb_model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        self.models['xgboost'] = xgb_model
        
        return xgb_model, metrics, feature_importance
    
    def train_isolation_forest(self, X_train):
        """Train Isolation Forest (unsupervised anomaly detection)"""
        logger.info("Training Isolation Forest model...")
        
        iso_model = IsolationForest(**IFOREST_PARAMS)
        iso_model.fit(X_train)
        
        logger.info("Isolation Forest trained (unsupervised)")
        
        self.models['isolation_forest'] = iso_model
        
        return iso_model
    
    def _calculate_metrics(self, y_true, y_pred, model_name: str):
        """Calculate and log evaluation metrics"""
        accuracy = accuracy_score(y_true, y_pred)
        precision = precision_score(y_true, y_pred)
        recall = recall_score(y_true, y_pred)
        f1 = f1_score(y_true, y_pred)
        
        logger.info(f"\n{model_name} Metrics:")
        logger.info(f"  Accuracy:  {accuracy:.4f}")
        logger.info(f"  Precision: {precision:.4f}")
        logger.info(f"  Recall:    {recall:.4f}")
        logger.info(f"  F1 Score:  {f1:.4f}")
        
        logger.info(f"\nConfusion Matrix:\n{confusion_matrix(y_true, y_pred)}")
        logger.info(f"\nClassification Report:\n{classification_report(y_true, y_pred)}")
        
        return {
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1_score': f1
        }
    
    def save_models(self):
        """Save trained models and scaler"""
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        
        for model_name, model in self.models.items():
            model_path = MODELS_DIR / f"{model_name}_model.joblib"
            joblib.dump(model, model_path)
            logger.info(f"Saved {model_name} to {model_path}")
        
        # Save scaler
        scaler_path = MODELS_DIR / "feature_scaler.joblib"
        joblib.dump(self.scaler, scaler_path)
        logger.info(f"Saved scaler to {scaler_path}")
    
    def train_all_models(self, num_genuine: int = 500, num_fake: int = 500):
        """
        Complete training pipeline
        
        Args:
            num_genuine: Number of genuine samples
            num_fake: Number of fake samples
        """
        logger.info("="*70)
        logger.info("STARTING MODEL TRAINING PIPELINE")
        logger.info("="*70)
        
        # 1. Generate/load data
        X, y = self.generate_or_load_data(num_genuine, num_fake)
        
        # 2. Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TRAIN_TEST_SPLIT, random_state=RANDOM_SEED, stratify=y
        )
        
        logger.info(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
        
        # 3. Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Convert back to DataFrame for feature names
        X_train_scaled = pd.DataFrame(X_train_scaled, columns=X_train.columns)
        X_test_scaled = pd.DataFrame(X_test_scaled, columns=X_test.columns)
        
        # 4. Train Random Forest
        rf_model, rf_metrics, rf_importance = self.train_random_forest(
            X_train_scaled, y_train, X_test_scaled, y_test
        )
        
        # 5. Train XGBoost
        xgb_model, xgb_metrics, xgb_importance = self.train_xgboost(
            X_train_scaled, y_train, X_test_scaled, y_test
        )
        
        # 6. Train Isolation Forest
        iso_model = self.train_isolation_forest(X_train_scaled)
        
        # 7. Save models
        self.save_models()
        
        logger.info("="*70)
        logger.info("TRAINING COMPLETE")
        logger.info("="*70)
        
        # Summary
        print("\n" + "="*70)
        print("TRAINING SUMMARY")
        print("="*70)
        print(f"\nDataset: {len(X)} samples ({num_genuine} genuine, {num_fake} fake)")
        print(f"Features: {X.shape[1]}")
        print(f"Train/Test Split: {1-TRAIN_TEST_SPLIT:.0%}/{TRAIN_TEST_SPLIT:.0%}")
        
        print("\n📊 Random Forest Performance:")
        for metric, value in rf_metrics.items():
            print(f"   {metric.capitalize():.<20} {value:.4f}")
        
        if xgb_metrics:
            print("\n📊 XGBoost Performance:")
            for metric, value in xgb_metrics.items():
                print(f"   {metric.capitalize():.<20} {value:.4f}")
        
        print(f"\n💾 Models saved to: {MODELS_DIR}")
        print("="*70 + "\n")
        
        return {
            'random_forest': {'model': rf_model, 'metrics': rf_metrics, 'importance': rf_importance},
            'xgboost': {'model': xgb_model, 'metrics': xgb_metrics, 'importance': xgb_importance} if xgb_model else None,
            'isolation_forest': {'model': iso_model}
        }


def main():
    """Main training function"""
    print("🧠 Work Detection System - Model Training")
    print("="*70 + "\n")
    
    trainer = ModelTrainer()
    
    # Train with default parameters (500 genuine + 500 fake samples)
    results = trainer.train_all_models(num_genuine=500, num_fake=500)
    
    print("\n✅ Training complete! Models are ready for use.")
    print("\nNext steps:")
    print("  • Test models: python -m src.models.evaluate")
    print("  • Run detection: python quick_start.py")


if __name__ == "__main__":
    main()
