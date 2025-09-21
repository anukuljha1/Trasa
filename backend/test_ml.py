#!/usr/bin/env python3
"""Test script for ML dependencies"""

try:
    import mediapipe as mp
    print("✅ MediaPipe imported successfully")
    print(f"   Version: {mp.__version__}")
except ImportError as e:
    print(f"❌ MediaPipe import failed: {e}")

try:
    import cv2
    print("✅ OpenCV imported successfully")
    print(f"   Version: {cv2.__version__}")
except ImportError as e:
    print(f"❌ OpenCV import failed: {e}")

try:
    import numpy as np
    print("✅ NumPy imported successfully")
    print(f"   Version: {np.__version__}")
except ImportError as e:
    print(f"❌ NumPy import failed: {e}")

try:
    from ml.simple_inference import SimpleExerciseAnalyzer
    print("✅ SimpleExerciseAnalyzer imported successfully")
except ImportError as e:
    print(f"❌ SimpleExerciseAnalyzer import failed: {e}")

print("\n🎯 ML dependencies test complete!")
