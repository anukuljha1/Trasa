#!/usr/bin/env python3
"""Test the simple ML analyzer"""

try:
    from ml.simple_analyzer import analyze_video_file, get_supported_exercises
    print("✅ Simple analyzer imported successfully")
    
    # Test supported exercises
    exercises = get_supported_exercises()
    print(f"✅ Supported exercises: {exercises}")
    
    # Test video analysis (mock)
    result = analyze_video_file("test_video.mp4")
    print(f"✅ Video analysis test passed")
    print(f"   Final counts: {result['final_counts']}")
    
except Exception as e:
    print(f"❌ Simple analyzer test failed: {e}")

print("\n🎯 Simple ML test complete!")
