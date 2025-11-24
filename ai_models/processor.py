# OskarTrack AI System – Developed by Mr.OSKAR
"""
Video/Image processing pipeline
"""

import cv2
import numpy as np
from typing import Dict, List
from ai_models.detector import PersonDetector, SimpleTracker
import json


class VideoProcessor:
    """Process video frames for customer tracking"""
    
    def __init__(self):
        self.detector = PersonDetector()
        self.tracker = SimpleTracker(max_disappeared=50)
        self.zones = []  # Will be loaded from database
        print("✅ Video Processor initialized")
    
    def load_zones(self, zones: List[Dict]):
        """Load zone definitions"""
        self.zones = zones
        print(f"✅ Loaded {len(zones)} zones")
    
    def point_in_polygon(self, point: tuple, polygon: List[List]) -> bool:
        """Check if point is inside polygon"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def detect_zone(self, centroid: tuple) -> int:
        """Detect which zone a point belongs to"""
        for zone in self.zones:
            if self.point_in_polygon(centroid, zone['coordinates']):
                return zone['id']
        return None
    
    def process_frame(self, frame: np.ndarray) -> Dict:
        """
        Process single frame
        Returns detection results and tracking info
        """
        # Detect persons
        detections = self.detector.detect(frame)
        
        # Update tracker
        tracked_objects = self.tracker.update(detections)
        
        # Analyze zones for each tracked object
        zone_analysis = {}
        for object_id, centroid in tracked_objects.items():
            zone_id = self.detect_zone(centroid)
            zone_analysis[object_id] = {
                'position': centroid,
                'zone_id': zone_id
            }
        
        # Draw results
        annotated_frame = self.detector.draw_detections(frame, detections)
        
        # Draw zones
        for zone in self.zones:
            coords = np.array(zone['coordinates'], dtype=np.int32)
            cv2.polylines(annotated_frame, [coords], True, (255, 0, 0), 2)
            # Zone label
            if len(coords) > 0:
                cv2.putText(annotated_frame, zone['name'], 
                           tuple(coords[0]), cv2.FONT_HERSHEY_SIMPLEX,
                           0.6, (255, 0, 0), 2)
        
        # Draw tracked objects
        for object_id, centroid in tracked_objects.items():
            cv2.circle(annotated_frame, centroid, 4, (0, 0, 255), -1)
            cv2.putText(annotated_frame, f"ID: {object_id}", 
                       (centroid[0] - 10, centroid[1] - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
        
        return {
            'detections': detections,
            'tracked_objects': tracked_objects,
            'zone_analysis': zone_analysis,
            'annotated_frame': annotated_frame,
            'person_count': len(tracked_objects)
        }
    
    def process_image(self, image_path: str) -> Dict:
        """Process single image file"""
        frame = cv2.imread(image_path)
        if frame is None:
            raise ValueError(f"Could not read image: {image_path}")
        
        return self.process_frame(frame)
    
    def process_video(self, video_path: str, callback=None):
        """Process video file frame by frame"""
        cap = cv2.VideoCapture(video_path)
        
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        frame_count = 0
        results = []
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Process every 5th frame for performance
            if frame_count % 5 == 0:
                result = self.process_frame(frame)
                results.append(result)
                
                if callback:
                    callback(result, frame_count)
            
            frame_count += 1
        
        cap.release()
        return results
