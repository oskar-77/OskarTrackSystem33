# OskarTrack AI System – Developed by Mr.OSKAR
"""
Utility helper functions
"""

import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Dict, List
import json


def generate_customer_id() -> str:
    """Generate unique customer tracking ID"""
    return f"CUST_{uuid.uuid4().hex[:12].upper()}"


def calculate_dwell_time(entry_time: datetime, exit_time: datetime = None) -> float:
    """Calculate time spent in seconds"""
    if exit_time is None:
        exit_time = datetime.utcnow()
    return (exit_time - entry_time).total_seconds()


def format_duration(seconds: float) -> str:
    """Format seconds into human-readable duration"""
    if seconds < 60:
        return f"{int(seconds)}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes}m {int(seconds % 60)}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def get_time_of_day(hour: int) -> str:
    """Get period of day from hour"""
    if 6 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 21:
        return "evening"
    else:
        return "night"


def calculate_peak_hours(hourly_data: Dict[int, int]) -> List[int]:
    """Find peak hours from hourly distribution"""
    sorted_hours = sorted(hourly_data.items(), key=lambda x: x[1], reverse=True)
    return [hour for hour, count in sorted_hours[:3]]


def encode_face(face_image) -> str:
    """Encode face for storage (placeholder)"""
    # In production, use InsightFace or similar
    return hashlib.md5(str(uuid.uuid4()).encode()).hexdigest()


def decode_face(encoded: str):
    """Decode stored face encoding (placeholder)"""
    return None


def validate_coordinates(coords: List[List]) -> bool:
    """Validate zone coordinates"""
    if not coords or len(coords) < 3:
        return False
    
    for point in coords:
        if not isinstance(point, list) or len(point) != 2:
            return False
        if not all(isinstance(x, (int, float)) for x in point):
            return False
    
    return True


def get_date_range(days: int = 7) -> tuple:
    """Get date range for last N days"""
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    return start_date, end_date


def export_to_json(data: any, filename: str):
    """Export data to JSON file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, default=str)
    return filename
