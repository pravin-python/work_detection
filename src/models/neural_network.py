"""
Deep Learning Neural Network Model for Work Detection
Uses TensorFlow/Keras to create a multi-layer neural network
"""

import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

try:
    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras import layers, models
    from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
    TENSORFLOW_AVAILABLE = True
except ImportError:
    TENSORFLOW_AVAILABLE = False

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report, confusion_matrix, 
    accuracy_score, precision_score, recall_score, f1_score
)
import joblib

from ..utils.logger import setup_logger
from ..utils.config import (
    LOG_LEVEL, LOG_FILE, MODELS_DIR, PROCESSED_DATA_DIR,
    TRAIN_TEST_SPLIT, RANDOM_SEED
)

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


class NeuralNetworkDetector:
    """
    Deep Learning Neural Network for work detection
    
    Architecture:
    - Input layer: All features (keyboard, mouse, temporal, visual)
    - Hidden layers: Multiple dense layers with dropout
    - Output layer: Binary classification (genuine/fake)
    """
    
    def __init__(self, model_path: Optional[Path] = None):
        """
        Initialize neural network detector
        
        Args:
            model_path: Path to saved model (if loading existing)
        """
        if not TENSORFLOW_AVAILABLE:
            logger.error("TensorFlow not available! Install: pip install tensorflow")
            raise ImportError("TensorFlow is required for neural network model")
        
        self.model = None
        self.scaler = StandardScaler()
        self.model_path = model_path or (MODELS_DIR / "neural_network_model.h5")
        self.scaler_path = MODELS_DIR / "neural_network_scaler.joblib"
        
        # Set random seeds for reproducibility
        np.random.seed(RANDOM_SEED)
        if TENSORFLOW_AVAILABLE:
            tf.random.set_seed(RANDOM_SEED)
        
        logger.info("NeuralNetworkDetector initialized")
    
    def build_model(self, input_dim: int) -> keras.Model:
        """
        Build neural network architecture
        
        Args:
            input_dim: Number of input features
        
        Returns:
            Compiled Keras model
        """
        model = models.Sequential([
            # Input layer
            layers.Dense(128, activation='relu', input_shape=(input_dim,)),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Hidden layer 1
            layers.Dense(64, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            # Hidden layer 2
            layers.Dense(32, activation='relu'),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Hidden layer 3
            layers.Dense(16, activation='relu'),
            layers.Dropout(0.2),
            
            # Output layer (binary classification)
            layers.Dense(1, activation='sigmoid')
        ])
        
        # Compile model
        # Use only 'accuracy' metric to avoid compatibility issues
        # Precision and recall will be calculated separately using sklearn
        model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info(f"Neural network built: {model.summary()}")
        return model
    
    def train(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        epochs: int = 100,
        batch_size: int = 32,
        validation_split: float = 0.2
    ) -> Dict:
        """
        Train the neural network
        
        Args:
            X: Feature DataFrame
            y: Target labels (0=genuine, 1=fake)
            epochs: Number of training epochs
            batch_size: Batch size
            validation_split: Validation split ratio
        
        Returns:
            Training history dictionary
        """
        logger.info("="*70)
        logger.info("TRAINING NEURAL NETWORK")
        logger.info("="*70)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TRAIN_TEST_SPLIT, random_state=RANDOM_SEED, stratify=y
        )
        
        logger.info(f"Train set: {X_train.shape}, Test set: {X_test.shape}")
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Build model
        self.model = self.build_model(X_train.shape[1])
        
        # Callbacks
        early_stopping = EarlyStopping(
            monitor='val_loss',
            patience=15,
            restore_best_weights=True,
            verbose=1
        )
        
        model_checkpoint = ModelCheckpoint(
            str(self.model_path),
            monitor='val_loss',
            save_best_only=True,
            verbose=1
        )
        
        # Train model
        logger.info(f"Training for {epochs} epochs...")
        history = self.model.fit(
            X_train_scaled, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=validation_split,
            callbacks=[early_stopping, model_checkpoint],
            verbose=1
        )
        
        # Evaluate on test set
        eval_results = self.model.evaluate(X_test_scaled, y_test, verbose=0)
        
        # Extract metrics (order: loss, accuracy)
        test_loss = eval_results[0]
        test_accuracy = eval_results[1]
        
        # Predictions for precision, recall, and F1 score
        y_pred_proba = self.model.predict(X_test_scaled, verbose=0)
        y_pred = (y_pred_proba > 0.5).astype(int).flatten()
        
        # Calculate metrics using sklearn for consistency
        from sklearn.metrics import precision_score, recall_score
        test_precision_sk = precision_score(y_test, y_pred, zero_division=0)
        test_recall_sk = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred)
        
        logger.info(f"\nTest Metrics:")
        logger.info(f"  Loss:     {test_loss:.4f}")
        logger.info(f"  Accuracy: {test_accuracy:.4f}")
        logger.info(f"  Precision: {test_precision_sk:.4f}")
        logger.info(f"  Recall:   {test_recall_sk:.4f}")
        logger.info(f"  F1 Score: {f1:.4f}")
        
        # Save scaler and feature names
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.scaler, self.scaler_path)
        logger.info(f"Scaler saved to {self.scaler_path}")
        
        # Save feature names for later reference
        feature_names_path = MODELS_DIR / "neural_network_feature_names.joblib"
        joblib.dump(X_train.columns.tolist(), feature_names_path)
        logger.info(f"Feature names saved to {feature_names_path}")
        
        return {
            'history': history.history,
            'test_metrics': {
                'loss': float(test_loss),
                'accuracy': float(test_accuracy),
                'precision': float(test_precision_sk),
                'recall': float(test_recall_sk),
                'f1_score': float(f1)
            },
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
    
    def load_model(self) -> bool:
        """
        Load trained model and scaler
        
        Returns:
            True if loaded successfully, False otherwise
        """
        if not self.model_path.exists():
            logger.warning(f"Model not found at {self.model_path}")
            return False
        
        try:
            self.model = keras.models.load_model(str(self.model_path))
            logger.info(f"Model loaded from {self.model_path}")
            
            if self.scaler_path.exists():
                self.scaler = joblib.load(self.scaler_path)
                logger.info(f"Scaler loaded from {self.scaler_path}")
                
                # Try to load feature names and attach to scaler
                feature_names_path = MODELS_DIR / "neural_network_feature_names.joblib"
                if feature_names_path.exists():
                    feature_names = joblib.load(feature_names_path)
                    # Store in scaler for easy access
                    if not hasattr(self.scaler, 'feature_names_in_'):
                        self.scaler.feature_names_in_ = np.array(feature_names)
                    logger.info(f"Loaded feature names ({len(feature_names)} features)")
            
            return True
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False
    
    def predict(self, features: pd.DataFrame) -> Tuple[float, float]:
        """
        Predict fake work probability
        
        Args:
            features: Feature DataFrame (single row or multiple rows)
        
        Returns:
            Tuple of (is_fake_probability, confidence)
            is_fake_probability: Probability of fake work (0-1)
            confidence: Confidence in prediction (0-1)
        """
        if self.model is None:
            if not self.load_model():
                raise ValueError("Model not loaded and cannot be loaded")
        
        # Get expected feature names from scaler (features used during training)
        if hasattr(self.scaler, 'feature_names_in_'):
            if isinstance(self.scaler.feature_names_in_, np.ndarray):
                expected_features = self.scaler.feature_names_in_.tolist()
            else:
                expected_features = list(self.scaler.feature_names_in_)
        else:
            # Try to load from saved feature names file
            feature_names_path = MODELS_DIR / "neural_network_feature_names.joblib"
            if feature_names_path.exists():
                expected_features = joblib.load(feature_names_path)
            else:
                # Fallback: use all features in DataFrame
                logger.warning("Feature names not available, using all features in DataFrame")
                expected_features = features.columns.tolist()
        
        # Filter features to only include those expected by the model
        missing_features = set(expected_features) - set(features.columns)
        extra_features = set(features.columns) - set(expected_features)
        
        if missing_features:
            logger.warning(f"Missing features (will be set to 0): {missing_features}")
            # Add missing features with 0 values
            for feat in missing_features:
                features[feat] = 0.0
        
        if extra_features:
            logger.debug(f"Removing extra features not in training data: {extra_features}")
            # Remove features not in training data
            features = features[list(expected_features)]
        else:
            # Reorder to match training order
            features = features[list(expected_features)]
        
        # Scale features
        features_scaled = self.scaler.transform(features)
        
        # Predict
        predictions = self.model.predict(features_scaled, verbose=0)
        fake_probability = float(predictions[0][0])
        
        # Calculate confidence (distance from 0.5)
        confidence = abs(fake_probability - 0.5) * 2.0
        
        return fake_probability, confidence
    
    def predict_batch(self, features: pd.DataFrame) -> np.ndarray:
        """
        Predict for multiple samples
        
        Args:
            features: Feature DataFrame (multiple rows)
        
        Returns:
            Array of fake probabilities
        """
        if self.model is None:
            if not self.load_model():
                raise ValueError("Model not loaded and cannot be loaded")
        
        features_scaled = self.scaler.transform(features)
        predictions = self.model.predict(features_scaled, verbose=0)
        
        return predictions.flatten()


class NeuralNetworkTrainer:
    """Trainer class for neural network model"""
    
    def __init__(self):
        self.detector = NeuralNetworkDetector()
        logger.info("NeuralNetworkTrainer initialized")
    
    def train_from_data(
        self, 
        X: pd.DataFrame, 
        y: pd.Series,
        epochs: int = 100
    ) -> Dict:
        """
        Train model from data
        
        Args:
            X: Feature DataFrame
            y: Target labels
            epochs: Training epochs
        
        Returns:
            Training results
        """
        return self.detector.train(X, y, epochs=epochs)
    
    def train_from_simulator(
        self, 
        num_genuine: int = 1000,
        num_fake: int = 1000,
        epochs: int = 100
    ) -> Dict:
        """
        Train model using data simulator
        
        Args:
            num_genuine: Number of genuine samples
            num_fake: Number of fake samples
            epochs: Training epochs
        
        Returns:
            Training results
        """
        from ..utils.data_simulator import DataSimulator
        
        logger.info("Generating training data...")
        simulator = DataSimulator()
        X, y = simulator.generate_training_data(num_genuine, num_fake)
        
        logger.info(f"Generated {len(X)} samples")
        
        return self.detector.train(X, y, epochs=epochs)


# Standalone training
if __name__ == "__main__":
    print("🧠 Neural Network Training")
    print("="*70 + "\n")
    
    trainer = NeuralNetworkTrainer()
    results = trainer.train_from_simulator(
        num_genuine=1000,
        num_fake=1000,
        epochs=100
    )
    
    print("\n✅ Training complete!")
    print(f"Model saved to: {MODELS_DIR / 'neural_network_model.h5'}")

