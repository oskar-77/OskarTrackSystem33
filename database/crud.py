# OskarTrack AI System – Developed by Mr.OSKAR
"""
CRUD operations for database
"""

from sqlalchemy.orm import Session
from database.models import Customer, Visit, Zone, TrackingEvent, AnalyticsSummary
from datetime import datetime, timedelta
from typing import List, Optional
import json


# ==================== CUSTOMER OPERATIONS ====================

def create_customer(db: Session, customer_id: str, age: int = None, gender: str = None):
    """Create new customer"""
    customer = Customer(
        customer_id=customer_id,
        estimated_age=age,
        estimated_gender=gender
    )
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return customer


def get_customer(db: Session, customer_id: str):
    """Get customer by tracking ID"""
    return db.query(Customer).filter(Customer.customer_id == customer_id).first()


def get_all_customers(db: Session, skip: int = 0, limit: int = 100):
    """Get all customers with pagination"""
    return db.query(Customer).offset(skip).limit(limit).all()


def update_customer_visit(db: Session, customer_id: str):
    """Update customer's last seen and visit count"""
    customer = get_customer(db, customer_id)
    if customer:
        customer.last_seen = datetime.utcnow()
        customer.total_visits += 1
        db.commit()
        db.refresh(customer)
    return customer


# ==================== VISIT OPERATIONS ====================

def create_visit(db: Session, customer_id: int):
    """Create new visit session"""
    visit = Visit(customer_id=customer_id)
    db.add(visit)
    db.commit()
    db.refresh(visit)
    return visit


def end_visit(db: Session, visit_id: int):
    """End visit and calculate duration"""
    visit = db.query(Visit).filter(Visit.id == visit_id).first()
    if visit and not visit.exit_time:
        visit.exit_time = datetime.utcnow()
        visit.duration = (visit.exit_time - visit.entry_time).total_seconds()
        db.commit()
        db.refresh(visit)
    return visit


def get_active_visits(db: Session):
    """Get all currently active visits"""
    return db.query(Visit).filter(Visit.exit_time.is_(None)).all()


def get_visits_by_date(db: Session, date: datetime):
    """Get all visits for a specific date"""
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    return db.query(Visit).filter(
        Visit.entry_time >= start,
        Visit.entry_time < end
    ).all()


# ==================== ZONE OPERATIONS ====================

def create_zone(db: Session, name: str, coordinates: list, zone_type: str, description: str = None):
    """Create new zone"""
    zone = Zone(
        name=name,
        description=description,
        coordinates=coordinates,
        zone_type=zone_type
    )
    db.add(zone)
    db.commit()
    db.refresh(zone)
    return zone


def get_all_zones(db: Session):
    """Get all active zones"""
    return db.query(Zone).filter(Zone.active == True).all()


def update_zone_stats(db: Session, zone_id: int, visitors: int = None, dwell_time: float = None):
    """Update zone statistics"""
    zone = db.query(Zone).filter(Zone.id == zone_id).first()
    if zone:
        if visitors is not None:
            zone.total_visitors += visitors
        if dwell_time is not None:
            # Calculate running average
            total = zone.total_visitors * zone.average_dwell_time
            zone.average_dwell_time = (total + dwell_time) / (zone.total_visitors + 1)
        db.commit()
        db.refresh(zone)
    return zone


# ==================== TRACKING EVENT OPERATIONS ====================

def create_event(db: Session, visit_id: int, event_type: str, position_x: float = None, 
                position_y: float = None, zone_id: int = None, extra_data: dict = None):
    """Create tracking event"""
    event = TrackingEvent(
        visit_id=visit_id,
        event_type=event_type,
        position_x=position_x,
        position_y=position_y,
        zone_id=zone_id,
        extra_data=extra_data
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


# ==================== ANALYTICS OPERATIONS ====================

def get_daily_stats(db: Session, date: datetime = None):
    """Get statistics for a specific day"""
    if not date:
        date = datetime.utcnow()
    
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    
    visits = db.query(Visit).filter(
        Visit.entry_time >= start,
        Visit.entry_time < end
    ).all()
    
    total_visitors = len(visits)
    unique_customers = len(set(v.customer_id for v in visits))
    
    durations = [v.duration for v in visits if v.duration]
    avg_duration = sum(durations) / len(durations) if durations else 0
    
    return {
        "date": date.strftime("%Y-%m-%d"),
        "total_visitors": total_visitors,
        "unique_visitors": unique_customers,
        "returning_visitors": total_visitors - unique_customers,
        "average_duration": round(avg_duration, 2)
    }


def get_hourly_distribution(db: Session, date: datetime = None):
    """Get visitor distribution by hour"""
    if not date:
        date = datetime.utcnow()
    
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    
    visits = db.query(Visit).filter(
        Visit.entry_time >= start,
        Visit.entry_time < end
    ).all()
    
    hourly_data = {hour: 0 for hour in range(24)}
    for visit in visits:
        hour = visit.entry_time.hour
        hourly_data[hour] += 1
    
    return hourly_data


def get_zone_stats(db: Session):
    """Get statistics for all zones"""
    zones = get_all_zones(db)
    return [{
        "id": zone.id,
        "name": zone.name,
        "total_visitors": zone.total_visitors,
        "average_dwell_time": round(zone.average_dwell_time, 2),
        "zone_type": zone.zone_type
    } for zone in zones]
