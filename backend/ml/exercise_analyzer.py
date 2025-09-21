import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
import cv2
import numpy as np
import mediapipe as mp
import json
import os
from pathlib import Path
import albumentations as A
from albumentations.pytorch import ToTensorV2
import yaml
from ultralytics import YOLO
import math

class ExerciseDataset(Dataset):
    """Custom dataset for exercise pose detection"""
    
    def __init__(self, data_path, img_size=640, augment=True):
        self.data_path = Path(data_path)
        self.img_size = img_size
        self.augment = augment
        
        # Load annotations
        self.annotations = self._load_annotations()
        
        # Mediapipe for pose detection
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=False,
            min_detection_confidence=0.5
        )
        
        # Augmentations
        if augment:
            self.transform = A.Compose([
                A.HorizontalFlip(p=0.5),
                A.RandomBrightnessContrast(p=0.2),
                A.Blur(blur_limit=3, p=0.1),
                A.GaussNoise(p=0.1),
                A.Resize(img_size, img_size),
                A.Normalize(),
                ToTensorV2()
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
        else:
            self.transform = A.Compose([
                A.Resize(img_size, img_size),
                A.Normalize(),
                ToTensorV2()
            ], bbox_params=A.BboxParams(format='yolo', label_fields=['class_labels']))
    
    def _load_annotations(self):
        """Load YOLO format annotations"""
        annotations = []
        
        # Scan for image and label files
        img_extensions = {'.jpg', '.jpeg', '.png', '.bmp'}
        
        for img_path in self.data_path.rglob('*'):
            if img_path.suffix.lower() in img_extensions:
                label_path = img_path.with_suffix('.txt')
                if label_path.exists():
                    annotations.append({
                        'image': str(img_path),
                        'label': str(label_path)
                    })
        
        return annotations
    
    def __len__(self):
        return len(self.annotations)
    
    def __getitem__(self, idx):
        annotation = self.annotations[idx]
        
        # Load image
        image = cv2.imread(annotation['image'])
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Load labels
        with open(annotation['label'], 'r') as f:
            labels = []
            for line in f.readlines():
                parts = line.strip().split()
                if len(parts) == 5:
                    class_id = int(parts[0])
                    bbox = [float(x) for x in parts[1:]]
                    labels.append([class_id] + bbox)
        
        if not labels:
            labels = [[0, 0.5, 0.5, 0.1, 0.1]]  # Default bbox if no labels
        
        labels = np.array(labels)
        bboxes = labels[:, 1:]
        class_labels = labels[:, 0].astype(int).tolist()
        
        # Apply transformations
        if self.transform:
            transformed = self.transform(
                image=image,
                bboxes=bboxes,
                class_labels=class_labels
            )
            image = transformed['image']
            bboxes = transformed['bboxes']
            class_labels = transformed['class_labels']
        
        # Extract pose keypoints
        pose_features = self._extract_pose_features(image)
        
        return {
            'image': image,
            'bboxes': torch.tensor(bboxes, dtype=torch.float32),
            'labels': torch.tensor(class_labels, dtype=torch.long),
            'pose_features': torch.tensor(pose_features, dtype=torch.float32)
        }
    
    def _extract_pose_features(self, image):
        """Extract pose keypoints using MediaPipe"""
        if isinstance(image, torch.Tensor):
            image_np = image.permute(1, 2, 0).numpy()
            image_np = (image_np * 255).astype(np.uint8)
        else:
            image_np = image
        
        results = self.pose.process(image_np)
        
        if results.pose_landmarks:
            landmarks = []
            for landmark in results.pose_landmarks.landmark:
                landmarks.extend([landmark.x, landmark.y, landmark.z])
            return np.array(landmarks[:99])  # 33 landmarks * 3 coords
        else:
            return np.zeros(99)  # Default if no pose detected

class ExerciseFormAnalyzer:
    """Analyze exercise form and detect cheating"""
    
    def __init__(self):
        self.exercise_rules = {
            'pushup': {
                'min_angle': 70,  # Minimum elbow angle at bottom
                'max_angle': 160, # Maximum elbow angle at top
                'body_alignment_threshold': 20  # Degrees deviation allowed
            },
            'situp': {
                'min_torso_angle': 30,  # Minimum sit-up angle
                'knee_bend_max': 120,   # Maximum knee bend allowed
                'back_curve_threshold': 15
            },
            'jump': {
                'min_height': 0.1,      # Minimum jump height (normalized)
                'landing_symmetry': 0.1, # Landing balance threshold
                'takeoff_angle': 15     # Knee bend at takeoff
            }
        }
    
    def analyze_pushup(self, pose_landmarks):
        """Analyze push-up form"""
        if not pose_landmarks:
            return False, "No pose detected"
        
        # Calculate elbow angle
        shoulder = pose_landmarks[11]  # Left shoulder
        elbow = pose_landmarks[13]    # Left elbow  
        wrist = pose_landmarks[15]    # Left wrist
        
        angle = self._calculate_angle(shoulder, elbow, wrist)
        
        # Check body alignment
        shoulder_r = pose_landmarks[12]
        hip = pose_landmarks[23]
        knee = pose_landmarks[25]
        
        body_angle = self._calculate_body_line_angle([shoulder, hip, knee])
        
        rules = self.exercise_rules['pushup']
        
        is_valid = (rules['min_angle'] <= angle <= rules['max_angle'] and 
                   abs(body_angle) <= rules['body_alignment_threshold'])
        
        feedback = []
        if angle < rules['min_angle']:
            feedback.append("Go lower - increase elbow bend")
        elif angle > rules['max_angle']:
            feedback.append("Don't fully lock elbows")
        
        if abs(body_angle) > rules['body_alignment_threshold']:
            feedback.append("Keep body straight")
        
        return is_valid, "; ".join(feedback) if feedback else "Good form"
    
    def analyze_situp(self, pose_landmarks):
        """Analyze sit-up form"""
        if not pose_landmarks:
            return False, "No pose detected"
        
        shoulder = pose_landmarks[11]
        hip = pose_landmarks[23]
        knee = pose_landmarks[25]
        ankle = pose_landmarks[27]
        
        # Torso angle
        torso_angle = self._calculate_angle(shoulder, hip, knee)
        
        # Knee bend
        knee_angle = self._calculate_angle(hip, knee, ankle)
        
        rules = self.exercise_rules['situp']
        
        is_valid = (torso_angle >= rules['min_torso_angle'] and 
                   knee_angle <= rules['knee_bend_max'])
        
        feedback = []
        if torso_angle < rules['min_torso_angle']:
            feedback.append("Sit up higher")
        if knee_angle > rules['knee_bend_max']:
            feedback.append("Keep knees more bent")
        
        return is_valid, "; ".join(feedback) if feedback else "Good form"
    
    def analyze_jump(self, pose_landmarks_sequence):
        """Analyze jump form using sequence of poses"""
        if len(pose_landmarks_sequence) < 3:
            return False, "Insufficient frames for jump analysis"
        
        # Analyze takeoff, peak, and landing
        takeoff = pose_landmarks_sequence[0]
        peak = pose_landmarks_sequence[len(pose_landmarks_sequence)//2]
        landing = pose_landmarks_sequence[-1]
        
        # Calculate jump height (hip y-coordinate change)
        takeoff_height = takeoff[23][1]  # Hip y
        peak_height = peak[23][1]
        
        jump_height = abs(takeoff_height - peak_height)
        
        rules = self.exercise_rules['jump']
        
        is_valid = jump_height >= rules['min_height']
        
        feedback = []
        if jump_height < rules['min_height']:
            feedback.append("Jump higher")
        
        return is_valid, "; ".join(feedback) if feedback else "Good jump"
    
    def _calculate_angle(self, point1, point2, point3):
        """Calculate angle between three points"""
        a = np.array([point1[0], point1[1]])
        b = np.array([point2[0], point2[1]])
        c = np.array([point3[0], point3[1]])
        
        ba = a - b
        bc = c - b
        
        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(np.clip(cosine_angle, -1.0, 1.0))
        
        return np.degrees(angle)
    
    def _calculate_body_line_angle(self, points):
        """Calculate deviation from straight line"""
        if len(points) < 3:
            return 0
        
        # Calculate angle of line from first to last point
        start, end = points[0], points[-1]
        line_vector = np.array([end[0] - start[0], end[1] - start[1]])
        
        # Check middle point deviation
        middle = points[1]
        mid_vector = np.array([middle[0] - start[0], middle[1] - start[1]])
        
        # Cross product for perpendicular distance
        cross = np.cross(line_vector, mid_vector)
        line_length = np.linalg.norm(line_vector)
        
        if line_length == 0:
            return 0
        
        deviation = abs(cross) / line_length
        return np.degrees(np.arcsin(np.clip(deviation, 0, 1)))

class ExerciseCounter:
    """Count exercise repetitions with state tracking"""
    
    def __init__(self, exercise_type):
        self.exercise_type = exercise_type
        self.count = 0
        self.state = "up"  # up, down, transition
        self.last_valid = True
        self.pose_history = []
        self.analyzer = ExerciseFormAnalyzer()
        
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
    
    def _count_pushups(self, pose_landmarks):
        """Count push-ups based on elbow angle"""
        if not pose_landmarks:
            return self.count, "No pose detected"
        
        shoulder = pose_landmarks[11]
        elbow = pose_landmarks[13]
        wrist = pose_landmarks[15]
        
        angle = self.analyzer._calculate_angle(shoulder, elbow, wrist)
        is_valid, feedback = self.analyzer.analyze_pushup(pose_landmarks)
        
        thresholds = self.thresholds['pushup']
        
        if self.state == "up" and angle < thresholds['down_threshold']:
            self.state = "down"
        elif self.state == "down" and angle > thresholds['up_threshold']:
            self.state = "up"
            if is_valid:
                self.count += 1
                return self.count, "Good rep! " + feedback
            else:
                return self.count, "Invalid rep: " + feedback
        
        return self.count, feedback
    
    def _count_situps(self, pose_landmarks):
        """Count sit-ups based on torso angle"""
        if not pose_landmarks:
            return self.count, "No pose detected"
        
        shoulder = pose_landmarks[11]
        hip = pose_landmarks[23]
        knee = pose_landmarks[25]
        
        torso_angle = self.analyzer._calculate_angle(shoulder, hip, knee)
        is_valid, feedback = self.analyzer.analyze_situp(pose_landmarks)
        
        thresholds = self.thresholds['situp']
        
        if self.state == "down" and torso_angle > thresholds['up_threshold']:
            self.state = "up"
        elif self.state == "up" and torso_angle < thresholds['down_threshold']:
            self.state = "down"
            if is_valid:
                self.count += 1
                return self.count, "Good rep! " + feedback
            else:
                return self.count, "Invalid rep: " + feedback
        
        return self.count, feedback
    
    def _count_jumps(self, pose_landmarks):
        """Count jumps based on hip height change"""
        if not pose_landmarks or len(self.pose_history) < 5:
            return self.count, "Analyzing..."
        
        current_height = pose_landmarks[23][1]  # Hip y-coordinate
        baseline_height = np.mean([p[23][1] for p in self.pose_history[-5:-1]])
        
        height_change = abs(current_height - baseline_height)
        is_valid, feedback = self.analyzer.analyze_jump(self.pose_history[-5:])
        
        threshold = self.thresholds['jump']['height_threshold']
        
        if self.state == "ground" and height_change > threshold:
            self.state = "air"
        elif self.state == "air" and height_change < threshold:
            self.state = "ground"
            if is_valid:
                self.count += 1
                return self.count, "Good jump! " + feedback
            else:
                return self.count, "Invalid jump: " + feedback
        
        return self.count, feedback

class ExerciseYOLO(nn.Module):
    """Custom YOLO model with pose estimation for exercise detection"""
    
    def __init__(self, num_classes=4):  # person, pushup, situp, jump
        super(ExerciseYOLO, self).__init__()
        
        # Load pre-trained YOLOv8 model
        self.yolo_backbone = YOLO('yolov8n.pt').model
        
        # Custom head for pose-aware detection
        self.pose_head = nn.Sequential(
            nn.Linear(99, 256),  # 33 pose landmarks * 3 coords
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(256, 128),
            nn.ReLU(),
            nn.Linear(128, 64)
        )
        
        # Fusion layer
        self.fusion = nn.Sequential(
            nn.Linear(64 + 256, 128),  # pose features + yolo features
            nn.ReLU(),
            nn.Linear(128, num_classes)
        )
    
    def forward(self, x, pose_features):
        # Extract YOLO features
        yolo_features = self.yolo_backbone(x)
        
        # Process pose features
        pose_out = self.pose_head(pose_features)
        
        # Fuse features
        combined = torch.cat([pose_out, yolo_features.view(yolo_features.size(0), -1)], dim=1)
        output = self.fusion(combined)
        
        return output

def create_dataset_yaml():
    """Create YOLO dataset configuration"""
    config = {
        'path': './exercise_dataset',
        'train': 'train/images',
        'val': 'val/images',
        'test': 'test/images',
        'nc': 4,
        'names': ['person', 'pushup', 'situp', 'jump']
    }
    
    with open('exercise_dataset.yaml', 'w') as f:
        yaml.dump(config, f)

def train_exercise_model():
    """Main training function"""
    
    # Create dataset config
    create_dataset_yaml()
    
    # Initialize model
    model = YOLO('yolov8n.pt')  # Start with pretrained weights
    
    # Training parameters
    train_params = {
        'data': 'exercise_dataset.yaml',
        'epochs': 100,
        'imgsz': 640,
        'batch': 16,
        'name': 'exercise_yolo',
        'patience': 10,
        'save_period': 10,
        'cache': True,
        'device': 0,  # GPU
        'workers': 8,
        'project': 'runs/detect',
        'optimizer': 'AdamW',
        'lr0': 0.01,
        'weight_decay': 0.0005,
        'warmup_epochs': 3,
        'box': 7.5,
        'cls': 0.5,
        'dfl': 1.5,
        'pose': 12.0,  # Pose loss weight
        'kobj': 2.0,
        'label_smoothing': 0.0,
        'nbs': 64,
        'hsv_h': 0.015,
        'hsv_s': 0.7,
        'hsv_v': 0.4,
        'degrees': 0.0,
        'translate': 0.1,
        'scale': 0.5,
        'shear': 0.0,
        'perspective': 0.0,
        'flipud': 0.0,
        'fliplr': 0.5,
        'mosaic': 1.0,
        'mixup': 0.0,
        'copy_paste': 0.0
    }
    
    # Train the model
    results = model.train(**train_params)
    
    # Validate the model
    metrics = model.val()
    
    # Export model
    model.export(format='onnx')  # Export to ONNX for web deployment
    
    print(f"Training completed! Best model saved.")
    print(f"mAP50: {metrics.box.map50}")
    print(f"mAP50-95: {metrics.box.map}")
    
    return model, results, metrics

def create_inference_pipeline():
    """Create inference pipeline for real-time exercise counting"""
    
    class ExerciseInference:
        def __init__(self, model_path):
            self.model = YOLO(model_path)
            self.mp_pose = mp.solutions.pose
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            
            self.counters = {
                'pushup': ExerciseCounter('pushup'),
                'situp': ExerciseCounter('situp'),
                'jump': ExerciseCounter('jump')
            }
            
            self.current_exercise = None
        
        def process_frame(self, frame):
            """Process video frame and return results"""
            # YOLO detection
            results = self.model(frame)
            
            # Pose detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pose_results = self.pose.process(rgb_frame)
            
            # Extract pose landmarks
            pose_landmarks = None
            if pose_results.pose_landmarks:
                landmarks = pose_results.pose_landmarks.landmark
                pose_landmarks = [(lm.x, lm.y, lm.z) for lm in landmarks]
            
            # Determine exercise type from YOLO results
            detected_exercise = self._get_exercise_type(results)
            
            if detected_exercise and detected_exercise != self.current_exercise:
                self.current_exercise = detected_exercise
                print(f"Exercise changed to: {detected_exercise}")
            
            # Count reps if exercise detected
            count, feedback = 0, "No exercise detected"
            if self.current_exercise and pose_landmarks:
                counter = self.counters[self.current_exercise]
                count, feedback = counter.process_frame(pose_landmarks)
            
            return {
                'frame': frame,
                'exercise': self.current_exercise,
                'count': count,
                'feedback': feedback,
                'pose_landmarks': pose_landmarks,
                'yolo_results': results
            }
        
        def _get_exercise_type(self, results):
            """Extract exercise type from YOLO results"""
            if results[0].boxes is not None:
                classes = results[0].boxes.cls.cpu().numpy()
                names = results[0].names
                
                for cls in classes:
                    class_name = names[int(cls)]
                    if class_name in ['pushup', 'situp', 'jump']:
                        return class_name
            return None
    
    return ExerciseInference

# Usage example
if __name__ == "__main__":
    print("Starting Exercise YOLO Model Training...")
    
    # Train the model
    model, results, metrics = train_exercise_model()
    
    # Create inference pipeline
    InferencePipeline = create_inference_pipeline()
    
    print("Training complete! Model ready for deployment.")
    print("To use: inference = InferencePipeline('path/to/best.pt')")
    print("Then: results = inference.process_frame(video_frame)")
