# OskarTrack AI System – Developed by Mr.OSKAR
"""
Person Detection using OpenCV (Simplified for Replit)
For production: Replace with YOLOv8 or similar
"""

import cv2
import numpy as np
from typing import List, Tuple


class PersonDetector:
    """Simple person detector using OpenCV HOG"""
    
    def __init__(self):
        # Initialize HOG descriptor for person detection
        self.hog = cv2.HOGDescriptor()
        self.hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        print("✅ Person Detector initialized")
    
    def detect(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """
        Detect persons in image
        Returns: List of bounding boxes [(x, y, w, h), ...]
        """
        # Resize for better performance
        height, width = image.shape[:2]
        if width > 640:
            scale = 640 / width
            image = cv2.resize(image, None, fx=scale, fy=scale)
        
        # Detect people
        boxes, weights = self.hog.detectMultiScale(
            image,
            winStride=(8, 8),
            padding=(4, 4),
            scale=1.05
        )
        
        # Filter by confidence
        detections = []
        for (x, y, w, h), weight in zip(boxes, weights):
            if weight > 0.5:  # Confidence threshold
                detections.append((int(x), int(y), int(w), int(h)))
        
        return detections
    
    def draw_detections(self, image: np.ndarray, detections: List[Tuple]) -> np.ndarray:
        """Draw bounding boxes on image"""
        output = image.copy()
        for (x, y, w, h) in detections:
            cv2.rectangle(output, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(output, 'Person', (x, y - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        return output


class SimpleTracker:
    """Simple tracking using centroid tracking"""
    
    def __init__(self, max_disappeared=30):
        self.next_object_id = 0
        self.objects = {}  # {object_id: centroid}
        self.disappeared = {}  # {object_id: frames_disappeared}
        self.max_disappeared = max_disappeared
    
    def register(self, centroid):
        """Register new object"""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
    
    def deregister(self, object_id):
        """Remove object from tracking"""
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    def update(self, detections: List[Tuple]) -> dict:
        """
        Update tracked objects with new detections
        Returns: {object_id: (cx, cy)}
        """
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return self.objects
        
        # Calculate centroids from detections
        input_centroids = []
        for (x, y, w, h) in detections:
            cx = int(x + w / 2.0)
            cy = int(y + h / 2.0)
            input_centroids.append((cx, cy))
        
        # If no existing objects, register all
        if len(self.objects) == 0:
            for centroid in input_centroids:
                self.register(centroid)
        else:
            # Match existing objects with new centroids
            object_ids = list(self.objects.keys())
            object_centroids = list(self.objects.values())
            
            # Calculate distances
            from scipy.spatial import distance as dist
            D = dist.cdist(np.array(object_centroids), np.array(input_centroids))
            
            # Find minimum distances
            rows = D.min(axis=1).argsort()
            cols = D.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for (row, col) in zip(rows, cols):
                if row in used_rows or col in used_cols:
                    continue
                
                if D[row, col] > 50:  # Max distance threshold
                    continue
                
                object_id = object_ids[row]
                self.objects[object_id] = input_centroids[col]
                self.disappeared[object_id] = 0
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Handle disappeared objects
            unused_rows = set(range(0, D.shape[0])).difference(used_rows)
            for row in unused_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            
            # Register new objects
            unused_cols = set(range(0, D.shape[1])).difference(used_cols)
            for col in unused_cols:
                self.register(input_centroids[col])
        
        return self.objects
