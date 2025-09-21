import cv2
import numpy as np
import mediapipe as mp
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class SimpleExerciseAnalyzer:
    """Simplified exercise analyzer using MediaPipe pose detection"""
    
    def __init__(self):
        # Initialize MediaPipe pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=False,
            model_complexity=1,
            enable_segmentation=False,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Exercise counters
        self.counters = {
            'pushup': ExerciseCounter('pushup'),
            'situp': ExerciseCounter('situp'),
            'jump': ExerciseCounter('jump')
        }
        
        self.current_exercise = None
        self.frame_count = 0
    
    def analyze_video(self, video_path: str) -> Dict:
        """Analyze entire video and return results"""
        cap = cv2.VideoCapture(video_path)
        results = []
        
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            result = self.process_frame(frame)
            results.append(result)
            self.frame_count += 1
        
        cap.release()
        
        # Get final counts
        final_counts = {}
        for exercise_type, counter in self.counters.items():
            final_counts[exercise_type] = counter.count
        
        return {
            'video_path': video_path,
            'total_frames': self.frame_count,
            'final_counts': final_counts,
            'frame_results': results[-10:] if results else []  # Last 10 frames
        }
    
    def process_frame(self, frame) -> Dict:
        """Process single frame and return analysis results"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose detection
        pose_results = self.pose.process(rgb_frame)
        
        # Extract pose landmarks
        pose_landmarks = None
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            pose_landmarks = [(lm.x, lm.y, lm.z) for lm in landmarks]
        
        # Detect exercise type based on pose
        detected_exercise = self._detect_exercise_type(pose_landmarks)
        
        if detected_exercise and detected_exercise != self.current_exercise:
            self.current_exercise = detected_exercise
            print(f"Exercise detected: {detected_exercise}")
        
        # Count reps for detected exercise
        count, feedback = 0, "No exercise detected"
        if self.current_exercise and pose_landmarks:
            counter = self.counters[self.current_exercise]
            count, feedback = counter.process_frame(pose_landmarks)
        
        return {
            'frame_number': self.frame_count,
            'exercise': self.current_exercise,
            'count': count,
            'feedback': feedback,
            'pose_detected': pose_landmarks is not None
        }
    
    def _detect_exercise_type(self, pose_landmarks) -> Optional[str]:
        """Detect exercise type based on pose landmarks"""
        if not pose_landmarks:
            return None
        
        # Get key points
        left_shoulder = pose_landmarks[11]
        right_shoulder = pose_landmarks[12]
        left_hip = pose_landmarks[23]
        right_hip = pose_landmarks[24]
        left_knee = pose_landmarks[25]
        right_knee = pose_landmarks[26]
        left_ankle = pose_landmarks[27]
        right_ankle = pose_landmarks[28]
        
        # Calculate angles and positions
        shoulder_hip_angle = self._calculate_angle(left_shoulder, left_hip, left_knee)
        hip_knee_angle = self._calculate_angle(left_hip, left_knee, left_ankle)
        
        # Simple heuristics for exercise detection
        if shoulder_hip_angle < 45:  # Body is horizontal
            return 'pushup'
        elif hip_knee_angle < 90:  # Knees bent significantly
            return 'situp'
        elif self._is_jumping_pose(pose_landmarks):
            return 'jump'
        
        return None
    
    def _is_jumping_pose(self, pose_landmarks) -> bool:
        """Check if pose indicates jumping"""
        if not pose_landmarks:
            return False
        
        # Check if feet are off ground (ankles higher than knees)
        left_ankle = pose_landmarks[27]
        left_knee = pose_landmarks[25]
        right_ankle = pose_landmarks[28]
        right_knee = pose_landmarks[26]
        
        return (left_ankle[1] < left_knee[1] and right_ankle[1] < right_knee[1])
    
    def _calculate_angle(self, point1, point2, point3) -> float:
        """Calculate angle between three points"""
        a = np.array([point1[0], point1[1]])
        b = np.array([point2[0], point2[1]])
        c = np.array([point3[0], point3[1]])
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def reset_counters(self):
        """Reset all exercise counters"""
        for counter in self.counters.values():
            counter.count = 0
            counter.state = "up"
            counter.pose_history = []
        self.current_exercise = None
        self.frame_count = 0

class ExerciseCounter:
    """Count exercise repetitions with state tracking"""
    
    def __init__(self, exercise_type):
        self.exercise_type = exercise_type
        self.count = 0
        self.state = "up"  # up, down, transition
        self.pose_history = []
        
        # State thresholds for each exercise
        self.thresholds = {
            'pushup': {'up_threshold': 150, 'down_threshold': 90},
            'situp': {'up_threshold': 45, 'down_threshold': 15},
            'jump': {'height_threshold': 0.05}
        }
    
    def process_frame(self, pose_landmarks):
        """Process single frame and update count"""
        self.pose_history.append(pose_landmarks)
        if len(self.pose_history) > 10:  # Keep last 10 frames
            self.pose_history.pop(0)
        
        if self.exercise_type == 'pushup':
            return self._count_pushups(pose_landmarks)
        elif self.exercise_type == 'situp':
            return self._count_situps(pose_landmarks)
        elif self.exercise_type == 'jump':
            return self._count_jumps(pose_landmarks)
        
        return self.count, "Unknown exercise"
    
    def _count_pushups(self, pose_landmarks):
        """Count push-ups based on elbow angle"""
        if not pose_landmarks or len(pose_landmarks) < 16:
            return self.count, "No pose detected"
        
        try:
            shoulder = pose_landmarks[11]
            elbow = pose_landmarks[13]
            wrist = pose_landmarks[15]
            
            angle = self._calculate_angle(shoulder, elbow, wrist)
            thresholds = self.thresholds['pushup']
            
            if self.state == "up" and angle < thresholds['down_threshold']:
                self.state = "down"
            elif self.state == "down" and angle > thresholds['up_threshold']:
                self.state = "up"
                self.count += 1
                return self.count, f"Push-up {self.count} completed!"
            
            return self.count, f"Push-up {self.count} - {self.state}"
        except (IndexError, TypeError):
            return self.count, "Invalid pose data"
    
    def _count_situps(self, pose_landmarks):
        """Count sit-ups based on torso angle"""
        if not pose_landmarks or len(pose_landmarks) < 28:
            return self.count, "No pose detected"
        
        try:
            shoulder = pose_landmarks[11]
            hip = pose_landmarks[23]
            knee = pose_landmarks[25]
            
            torso_angle = self._calculate_angle(shoulder, hip, knee)
            thresholds = self.thresholds['situp']
            
            if self.state == "down" and torso_angle > thresholds['up_threshold']:
                self.state = "up"
            elif self.state == "up" and torso_angle < thresholds['down_threshold']:
                self.state = "down"
                self.count += 1
                return self.count, f"Sit-up {self.count} completed!"
            
            return self.count, f"Sit-up {self.count} - {self.state}"
        except (IndexError, TypeError):
            return self.count, "Invalid pose data"
    
    def _count_jumps(self, pose_landmarks):
        """Count jumps based on hip height change"""
        if not pose_landmarks or len(self.pose_history) < 5:
            return self.count, "Analyzing..."
        
        try:
            current_height = pose_landmarks[23][1]  # Hip y-coordinate
            baseline_height = np.mean([p[23][1] for p in self.pose_history[-5:-1]])
            
            height_change = abs(current_height - baseline_height)
            threshold = self.thresholds['jump']['height_threshold']
            
            if self.state == "ground" and height_change > threshold:
                self.state = "air"
            elif self.state == "air" and height_change < threshold:
                self.state = "ground"
                self.count += 1
                return self.count, f"Jump {self.count} completed!"
            
            return self.count, f"Jump {self.count} - {self.state}"
        except (IndexError, TypeError):
            return self.count, "Invalid pose data"
    
    def _calculate_angle(self, point1, point2, point3) -> float:
        """Calculate angle between three points"""
        a = np.array([point1[0], point1[1]])
        b = np.array([point2[0], point2[1]])
        c = np.array([point3[0], point3[1]])
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)

# Global analyzer instance
analyzer = SimpleExerciseAnalyzer()

def analyze_video_file(video_path: str) -> Dict:
    """Analyze video file and return exercise counts"""
    return analyzer.analyze_video(video_path)

def reset_analyzer():
    """Reset the global analyzer"""
    analyzer.reset_counters()
