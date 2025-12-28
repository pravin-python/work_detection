"""
Train Neural Network Model for Work Detection
Run this script to train the deep learning model
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.neural_network import NeuralNetworkTrainer
from src.utils.data_simulator import DataSimulator
from src.utils.logger import setup_logger
from src.utils.config import LOG_LEVEL, LOG_FILE

logger = setup_logger(__name__, LOG_FILE, LOG_LEVEL)


def main():
    """Main training function"""
    print("\n" + "="*70)
    print("🧠 NEURAL NETWORK TRAINING FOR WORK DETECTION")
    print("="*70)
    print("\nThis will train a deep learning model to detect fake work.")
    print("The model uses keyboard, mouse, temporal, and visual features.\n")
    
    # Get user input for training parameters
    try:
        num_genuine = int(input("Number of genuine work samples (default: 1000): ") or "1000")
        num_fake = int(input("Number of fake work samples (default: 1000): ") or "1000")
        epochs = int(input("Training epochs (default: 100): ") or "100")
    except (ValueError, KeyboardInterrupt):
        print("\nUsing default values...")
        num_genuine = 1000
        num_fake = 1000
        epochs = 100
    
    print(f"\n📊 Training Configuration:")
    print(f"   Genuine samples: {num_genuine}")
    print(f"   Fake samples: {num_fake}")
    print(f"   Epochs: {epochs}")
    print(f"   Total samples: {num_genuine + num_fake}\n")
    
    # Initialize trainer
    trainer = NeuralNetworkTrainer()
    
    # Train model
    print("🚀 Starting training...\n")
    try:
        results = trainer.train_from_simulator(
            num_genuine=num_genuine,
            num_fake=num_fake,
            epochs=epochs
        )
        
        # Print results
        print("\n" + "="*70)
        print("✅ TRAINING COMPLETE")
        print("="*70)
        
        if results and 'test_metrics' in results:
            metrics = results['test_metrics']
            print(f"\n📊 Test Set Performance:")
            print(f"   Accuracy:  {metrics['accuracy']:.4f}")
            print(f"   Precision: {metrics['precision']:.4f}")
            print(f"   Recall:    {metrics['recall']:.4f}")
            print(f"   F1 Score:  {metrics['f1_score']:.4f}")
        
        print(f"\n💾 Model saved to: data/models/neural_network_model.h5")
        print(f"💾 Scaler saved to: data/models/neural_network_scaler.joblib")
        print("\n✅ The model is now ready to use!")
        print("\nNext steps:")
        print("  • Run monitoring: python monitor.py")
        print("  • Test detection: python quick_start.py")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        print(f"\n❌ Training failed: {e}")
        print("\nTroubleshooting:")
        print("  • Make sure TensorFlow is installed: pip install tensorflow")
        print("  • Check that all dependencies are installed: pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()

