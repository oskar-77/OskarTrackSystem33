# OskarTrack AI System – Developed by Mr.OSKAR
"""
Database Models for OskarTrack Customer Tracking System
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Customer(Base):
    """Customer/Visitor tracking"""
    __tablename__ = "customers"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(String, unique=True, index=True)  # Unique tracking ID
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_seen = Column(DateTime, default=datetime.utcnow)
    total_visits = Column(Integer, default=1)
    total_time_spent = Column(Float, default=0.0)  # in seconds
    
    # Demographics (from AI analysis)
    estimated_age = Column(Integer, nullable=True)
    estimated_gender = Column(String, nullable=True)
    
    # Face recognition
    face_encoding = Column(Text, nullable=True)  # Stored as JSON string
    
    # Visits relationship
    visits = relationship("Visit", back_populates="customer")
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Visit(Base):
    """Individual visit session"""
    __tablename__ = "visits"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"))
    
    entry_time = Column(DateTime, default=datetime.utcnow)
    exit_time = Column(DateTime, nullable=True)
    duration = Column(Float, default=0.0)  # in seconds
    
    # Path tracking
    path_data = Column(JSON, nullable=True)  # Store movement path
    zones_visited = Column(JSON, nullable=True)  # List of zone IDs
    
    # Behavioral metrics
    dwell_time_per_zone = Column(JSON, nullable=True)  # {zone_id: seconds}
    interactions = Column(Integer, default=0)  # Product interactions count
    
    # Relationship
    customer = relationship("Customer", back_populates="visits")
    events = relationship("TrackingEvent", back_populates="visit")
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Zone(Base):
    """Store zones/areas for tracking"""
    __tablename__ = "zones"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    
    # Coordinates for zone polygon
    coordinates = Column(JSON)  # [[x1,y1], [x2,y2], ...]
    
    # Zone type
    zone_type = Column(String)  # entrance, exit, product_area, checkout, etc.
    
    # Stats
    total_visitors = Column(Integer, default=0)
    average_dwell_time = Column(Float, default=0.0)
    
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrackingEvent(Base):
    """Real-time tracking events"""
    __tablename__ = "tracking_events"
    
    id = Column(Integer, primary_key=True, index=True)
    visit_id = Column(Integer, ForeignKey("visits.id"))
    
    event_type = Column(String)  # detection, zone_enter, zone_exit, interaction
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Location data
    position_x = Column(Float, nullable=True)
    position_y = Column(Float, nullable=True)
    zone_id = Column(Integer, nullable=True)
    
    # Additional data
    extra_data = Column(JSON, nullable=True)
    
    # Relationship
    visit = relationship("Visit", back_populates="events")


class AnalyticsSummary(Base):
    """Daily/hourly analytics summaries"""
    __tablename__ = "analytics_summary"
    
    id = Column(Integer, primary_key=True, index=True)
    
    summary_date = Column(DateTime, index=True)
    summary_type = Column(String)  # hourly, daily, weekly
    
    # Metrics
    total_visitors = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)
    returning_visitors = Column(Integer, default=0)
    average_visit_duration = Column(Float, default=0.0)
    
    # Peak times
    peak_hour = Column(Integer, nullable=True)
    peak_visitors_count = Column(Integer, default=0)
    
    # Zone stats
    zone_stats = Column(JSON, nullable=True)  # {zone_id: {visitors, dwell_time}}
    
    # Demographics breakdown
    age_distribution = Column(JSON, nullable=True)
    gender_distribution = Column(JSON, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
