#!/usr/bin/env python3
"""
Training script for the exercise analysis model.
This script will create a basic model for exercise detection.
"""

import os
import sys
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent))

from ml.exercise_analyzer import train_exercise_model, create_inference_pipeline

def main():
    """Main training function"""
    print("🚀 Starting TRASA Exercise Model Training...")
    print("=" * 50)
    
    # Check if we have a dataset
    dataset_path = Path("exercise_dataset")
    if not dataset_path.exists():
        print("⚠️  No training dataset found. Creating a basic model...")
        print("To train with real data, create a dataset structure:")
        print("exercise_dataset/")
        print("├── train/images/")
        print("├── train/labels/")
        print("├── val/images/")
        print("└── val/labels/")
        print()
        print("For now, we'll use the simplified MediaPipe-based analyzer.")
        return
    
    try:
        # Train the model
        print("📊 Training exercise detection model...")
        model, results, metrics = train_exercise_model()
        
        print("✅ Training completed successfully!")
        print(f"📈 Model performance:")
        print(f"   - mAP50: {metrics.box.map50:.3f}")
        print(f"   - mAP50-95: {metrics.box.map:.3f}")
        
        # Create inference pipeline
        print("🔧 Setting up inference pipeline...")
        InferencePipeline = create_inference_pipeline()
        
        print("🎯 Model ready for deployment!")
        print("📁 Model files saved in: runs/detect/exercise_yolo/")
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        print("Using simplified MediaPipe-based analyzer instead.")
        print("This will still provide basic exercise counting functionality.")

if __name__ == "__main__":
    main()
