"""
Real ML-based exercise analyzer using MediaPipe pose detection
"""

import cv2
import numpy as np
import mediapipe as mp
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import math

class RealExerciseAnalyzer:
    """Real exercise analyzer using MediaPipe pose detection"""
    
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
        self.pose_history = []
    
    def analyze_video(self, video_path: str) -> Dict:
        """Analyze video file and return real exercise counts"""
        print(f"Starting real analysis of video: {video_path}")
        
        # Reset counters
        self.reset_counters()
        
        # Open video file
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise Exception(f"Could not open video file: {video_path}")
        
        frame_results = []
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        
        print(f"Video info: {total_frames} frames, {fps} FPS")
        
        frame_idx = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every 5th frame for efficiency
            if frame_idx % 5 == 0:
                result = self.process_frame(frame, frame_idx)
                if result:
                    frame_results.append(result)
            
            frame_idx += 1
        
        cap.release()
        
        # Get final counts
        final_counts = {}
        for exercise_type, counter in self.counters.items():
            final_counts[exercise_type] = counter.count
        
        # Determine most detected exercise
        detected_exercise = self._get_most_detected_exercise(frame_results)
        
        # Calculate form score based on pose detection quality
        form_score = self._calculate_form_score(frame_results)
        
        results = {
            'video_path': video_path,
            'total_frames': total_frames,
            'final_counts': final_counts,
            'frame_results': frame_results[-10:],  # Last 10 results
            'detected_exercise': detected_exercise,
            'analysis_quality': 'Real Analysis',
            'form_score': form_score,
            'pose_detection_rate': len([f for f in frame_results if f['pose_detected']]) / max(len(frame_results), 1) * 100
        }
        
        print(f"Analysis complete: {final_counts}, detected: {detected_exercise}")
        return results
    
    def process_frame(self, frame, frame_number: int) -> Optional[Dict]:
        """Process single frame and return analysis results"""
        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Process pose detection
        pose_results = self.pose.process(rgb_frame)
        
        # Extract pose landmarks
        pose_landmarks = None
        pose_detected = False
        
        if pose_results.pose_landmarks:
            landmarks = pose_results.pose_landmarks.landmark
            pose_landmarks = [(lm.x, lm.y, lm.z) for lm in landmarks]
            pose_detected = True
            
            # Store pose for history
            self.pose_history.append(pose_landmarks)
            if len(self.pose_history) > 30:  # Keep last 30 poses
                self.pose_history.pop(0)
        
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
            'frame_number': frame_number,
            'exercise': self.current_exercise,
            'count': count,
            'feedback': feedback,
            'pose_detected': pose_detected
        }
    
    def _detect_exercise_type(self, pose_landmarks) -> Optional[str]:
        """Detect exercise type based on pose landmarks"""
        if not pose_landmarks or len(pose_landmarks) < 33:
            return None
        
        try:
            # Get key points (MediaPipe pose landmarks)
            left_shoulder = pose_landmarks[11]
            right_shoulder = pose_landmarks[12]
            left_hip = pose_landmarks[23]
            right_hip = pose_landmarks[24]
            left_knee = pose_landmarks[25]
            right_knee = pose_landmarks[26]
            left_ankle = pose_landmarks[27]
            right_ankle = pose_landmarks[28]
            left_elbow = pose_landmarks[13]
            right_elbow = pose_landmarks[14]
            left_wrist = pose_landmarks[15]
            right_wrist = pose_landmarks[16]
            
            # Calculate key angles and positions
            shoulder_hip_angle = self._calculate_angle(left_shoulder, left_hip, left_knee)
            hip_knee_angle = self._calculate_angle(left_hip, left_knee, left_ankle)
            elbow_angle_left = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
            elbow_angle_right = self._calculate_angle(right_shoulder, right_elbow, right_wrist)
            
            # Check for push-up position (body horizontal, arms bent)
            if (shoulder_hip_angle < 30 and  # Body is horizontal
                (elbow_angle_left < 120 or elbow_angle_right < 120)):  # Arms are bent
                return 'pushup'
            
            # Check for sit-up position (body vertical, knees bent)
            elif (shoulder_hip_angle > 60 and  # Body is more vertical
                  hip_knee_angle < 90):  # Knees are bent
                return 'situp'
            
            # Check for jump position (feet off ground)
            elif self._is_jumping_pose(pose_landmarks):
                return 'jump'
            
        except (IndexError, TypeError) as e:
            print(f"Error in pose detection: {e}")
            return None
        
        return None
    
    def _is_jumping_pose(self, pose_landmarks) -> bool:
        """Check if pose indicates jumping"""
        if not pose_landmarks or len(pose_landmarks) < 28:
            return False
        
        try:
            # Check if feet are off ground (ankles higher than knees)
            left_ankle = pose_landmarks[27]
            left_knee = pose_landmarks[25]
            right_ankle = pose_landmarks[28]
            right_knee = pose_landmarks[26]
            
            # Also check if there's significant vertical movement in recent poses
            if len(self.pose_history) > 5:
                current_hip_y = pose_landmarks[23][1]  # Left hip y-coordinate
                avg_hip_y = np.mean([p[23][1] for p in self.pose_history[-5:]])
                
                # If hip is significantly higher than average, might be jumping
                if current_hip_y < avg_hip_y - 0.05:  # 5% higher
                    return True
            
            return (left_ankle[1] < left_knee[1] and right_ankle[1] < right_knee[1])
        except (IndexError, TypeError):
            return False
    
    def _calculate_angle(self, point1, point2, point3) -> float:
        """Calculate angle between three points"""
        try:
            a = np.array([point1[0], point1[1]])
            b = np.array([point2[0], point2[1]])
            c = np.array([point3[0], point3[1]])
            
            ba = a - b
            bc = c - b
            
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            
            return np.degrees(angle)
        except:
            return 0
    
    def _get_most_detected_exercise(self, frame_results: List[Dict]) -> Optional[str]:
        """Get the most frequently detected exercise"""
        if not frame_results:
            return None
        
        exercise_counts = {}
        for frame in frame_results:
            if frame['exercise']:
                exercise_counts[frame['exercise']] = exercise_counts.get(frame['exercise'], 0) + 1
        
        if exercise_counts:
            return max(exercise_counts, key=exercise_counts.get)
        return None
    
    def _calculate_form_score(self, frame_results: List[Dict]) -> int:
        """Calculate form score based on pose detection quality"""
        if not frame_results:
            return 0
        
        pose_detected_frames = len([f for f in frame_results if f['pose_detected']])
        total_frames = len(frame_results)
        
        if total_frames == 0:
            return 0
        
        detection_rate = pose_detected_frames / total_frames
        return int(detection_rate * 100)
    
    def reset_counters(self):
        """Reset all counters"""
        for counter in self.counters.values():
            counter.count = 0
            counter.state = "up"
            counter.pose_history = []
        self.current_exercise = None
        self.frame_count = 0
        self.pose_history = []

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
        if not pose_landmarks or len(pose_landmarks) < 33:
            return self.count, "No pose detected"
        
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
        try:
            left_shoulder = pose_landmarks[11]
            left_elbow = pose_landmarks[13]
            left_wrist = pose_landmarks[15]
            
            angle = self._calculate_angle(left_shoulder, left_elbow, left_wrist)
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
        try:
            left_shoulder = pose_landmarks[11]
            left_hip = pose_landmarks[23]
            left_knee = pose_landmarks[25]
            
            torso_angle = self._calculate_angle(left_shoulder, left_hip, left_knee)
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
        try:
            if len(self.pose_history) < 5:
                return self.count, "Analyzing..."
            
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
        try:
            a = np.array([point1[0], point1[1]])
            b = np.array([point2[0], point2[1]])
            c = np.array([point3[0], point3[1]])
            
            ba = a - b
            bc = c - b
            
            cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
            
            return np.degrees(angle)
        except:
            return 0

# Global analyzer instance
analyzer = RealExerciseAnalyzer()

def analyze_video_file(video_path: str) -> Dict:
    """Analyze video file and return real exercise counts"""
    return analyzer.analyze_video(video_path)

def reset_analyzer():
    """Reset the global analyzer"""
    analyzer.reset_counters()

def get_supported_exercises() -> List[str]:
    """Get list of supported exercise types"""
    return ['pushup', 'situp', 'jump']
