#!/usr/bin/env python3
"""Test the real ML analyzer"""

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
    from ml.real_analyzer import RealExerciseAnalyzer
    print("✅ RealExerciseAnalyzer imported successfully")
    
    # Test creating analyzer
    analyzer = RealExerciseAnalyzer()
    print("✅ RealExerciseAnalyzer instance created successfully")
    
except ImportError as e:
    print(f"❌ RealExerciseAnalyzer import failed: {e}")
except Exception as e:
    print(f"❌ RealExerciseAnalyzer test failed: {e}")

print("\n🎯 Real ML test complete!")
