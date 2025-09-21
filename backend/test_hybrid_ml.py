#!/usr/bin/env python3
"""Test the hybrid ML analyzer"""

try:
    from ml.hybrid_analyzer import analyze_video_file, get_supported_exercises
    print("✅ Hybrid analyzer imported successfully")
    
    # Test supported exercises
    exercises = get_supported_exercises()
    print(f"✅ Supported exercises: {exercises}")
    
    # Test video analysis with a mock file
    result = analyze_video_file("test_video.webm")
    print(f"✅ Video analysis test passed")
    print(f"   Detected exercise: {result['detected_exercise']}")
    print(f"   Final counts: {result['final_counts']}")
    print(f"   Form score: {result['form_score']}%")
    print(f"   Analysis quality: {result['analysis_quality']}")
    
except Exception as e:
    print(f"❌ Hybrid analyzer test failed: {e}")

print("\n🎯 Hybrid ML test complete!")
