# OskarTrack AI System – Developed by Mr.OSKAR
"""
FastAPI Backend for OskarTrack Customer Tracking System
"""

from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import cv2
import numpy as np
import io
import json
import os

from database.engine import init_db, get_db
from database import crud, models
from ai_models.processor import VideoProcessor
from utils.helpers import generate_customer_id, format_duration, get_date_range

# Initialize FastAPI app
app = FastAPI(
    title="OskarTrack AI System",
    description="Customer Tracking & Analytics System by Mr.OSKAR",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files
app.mount("/web", StaticFiles(directory="web", html=True), name="web")

# Initialize video processor
processor = VideoProcessor()

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass

manager = ConnectionManager()


# ==================== STARTUP ====================

@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()
    print("🚀 OskarTrack System Started")


# ==================== HEALTH CHECK ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "OskarTrack AI System - Developed by Mr.OSKAR",
        "status": "running",
        "version": "1.0.0"
    }


@app.get("/api/health")
async def health_check():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "database": "connected"
    }


# ==================== CUSTOMER ENDPOINTS ====================

@app.get("/api/customers")
async def get_customers(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all customers with pagination"""
    customers = crud.get_all_customers(db, skip=skip, limit=limit)
    return [{
        "id": c.id,
        "customer_id": c.customer_id,
        "first_seen": c.first_seen.isoformat(),
        "last_seen": c.last_seen.isoformat(),
        "total_visits": c.total_visits,
        "total_time_spent": c.total_time_spent,
        "total_time_formatted": format_duration(c.total_time_spent),
        "estimated_age": c.estimated_age,
        "estimated_gender": c.estimated_gender
    } for c in customers]


@app.get("/api/customers/{customer_id}")
async def get_customer_details(customer_id: str, db: Session = Depends(get_db)):
    """Get detailed customer information"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    return {
        "id": customer.id,
        "customer_id": customer.customer_id,
        "first_seen": customer.first_seen.isoformat(),
        "last_seen": customer.last_seen.isoformat(),
        "total_visits": customer.total_visits,
        "total_time_spent": customer.total_time_spent,
        "estimated_age": customer.estimated_age,
        "estimated_gender": customer.estimated_gender,
        "visits": len(customer.visits)
    }


@app.post("/api/customers")
async def create_customer(age: Optional[int] = None, gender: Optional[str] = None, 
                         db: Session = Depends(get_db)):
    """Create new customer"""
    customer_id = generate_customer_id()
    customer = crud.create_customer(db, customer_id, age, gender)
    
    # Broadcast to WebSocket
    await manager.broadcast({
        "type": "new_customer",
        "data": {"customer_id": customer_id}
    })
    
    return {"customer_id": customer_id, "id": customer.id}


# ==================== VISIT ENDPOINTS ====================

@app.get("/api/visits/active")
async def get_active_visits(db: Session = Depends(get_db)):
    """Get all currently active visits"""
    visits = crud.get_active_visits(db)
    return [{
        "id": v.id,
        "customer_id": v.customer.customer_id,
        "entry_time": v.entry_time.isoformat(),
        "duration": (datetime.utcnow() - v.entry_time).total_seconds()
    } for v in visits]


@app.post("/api/visits/start")
async def start_visit(customer_id: str, db: Session = Depends(get_db)):
    """Start new visit session"""
    customer = crud.get_customer(db, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    
    visit = crud.create_visit(db, customer.id)
    crud.update_customer_visit(db, customer_id)
    
    return {"visit_id": visit.id, "entry_time": visit.entry_time.isoformat()}


@app.post("/api/visits/{visit_id}/end")
async def end_visit(visit_id: int, db: Session = Depends(get_db)):
    """End visit session"""
    visit = crud.end_visit(db, visit_id)
    if not visit:
        raise HTTPException(status_code=404, detail="Visit not found")
    
    return {
        "visit_id": visit.id,
        "duration": visit.duration,
        "duration_formatted": format_duration(visit.duration)
    }


# ==================== ZONE ENDPOINTS ====================

@app.get("/api/zones")
async def get_zones(db: Session = Depends(get_db)):
    """Get all zones"""
    zones = crud.get_all_zones(db)
    return [{
        "id": z.id,
        "name": z.name,
        "description": z.description,
        "coordinates": z.coordinates,
        "zone_type": z.zone_type,
        "total_visitors": z.total_visitors,
        "average_dwell_time": z.average_dwell_time
    } for z in zones]


@app.post("/api/zones")
async def create_zone(name: str, coordinates: List[List[int]], zone_type: str,
                     description: Optional[str] = None, db: Session = Depends(get_db)):
    """Create new zone"""
    zone = crud.create_zone(db, name, coordinates, zone_type, description)
    
    # Reload zones in processor
    zones = crud.get_all_zones(db)
    processor.load_zones([{
        "id": z.id,
        "name": z.name,
        "coordinates": z.coordinates
    } for z in zones])
    
    return {"zone_id": zone.id, "name": zone.name}


# ==================== ANALYTICS ENDPOINTS ====================

@app.get("/api/analytics/daily")
async def get_daily_analytics(date: Optional[str] = None, db: Session = Depends(get_db)):
    """Get daily analytics"""
    if date:
        target_date = datetime.fromisoformat(date)
    else:
        target_date = datetime.utcnow()
    
    stats = crud.get_daily_stats(db, target_date)
    return stats


@app.get("/api/analytics/hourly")
async def get_hourly_analytics(date: Optional[str] = None, db: Session = Depends(get_db)):
    """Get hourly visitor distribution"""
    if date:
        target_date = datetime.fromisoformat(date)
    else:
        target_date = datetime.utcnow()
    
    distribution = crud.get_hourly_distribution(db, target_date)
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "hourly_data": distribution
    }


@app.get("/api/analytics/zones")
async def get_zone_analytics(db: Session = Depends(get_db)):
    """Get zone statistics"""
    stats = crud.get_zone_stats(db)
    return {"zones": stats}


@app.get("/api/analytics/summary")
async def get_analytics_summary(days: int = 7, db: Session = Depends(get_db)):
    """Get analytics summary for last N days"""
    today = datetime.utcnow()
    stats_list = []
    
    for i in range(days):
        date = today - timedelta(days=i)
        stats = crud.get_daily_stats(db, date)
        stats_list.append(stats)
    
    return {"summary": stats_list}


# ==================== VIDEO/IMAGE PROCESSING ====================

@app.post("/api/process/image")
async def process_image(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Process uploaded image for person detection"""
    # Read image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    # Load zones
    zones = crud.get_all_zones(db)
    processor.load_zones([{
        "id": z.id,
        "name": z.name,
        "coordinates": z.coordinates
    } for z in zones])
    
    # Process image
    result = processor.process_frame(image)
    
    # Encode annotated image
    _, buffer = cv2.imencode('.jpg', result['annotated_frame'])
    image_bytes = buffer.tobytes()
    
    return {
        "person_count": result['person_count'],
        "detections": len(result['detections']),
        "tracked_objects": len(result['tracked_objects']),
        "zone_analysis": result['zone_analysis']
    }


@app.post("/api/process/video")
async def process_video(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Process uploaded video"""
    # Save uploaded video temporarily
    temp_path = f"/tmp/{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())
    
    try:
        # Load zones
        zones = crud.get_all_zones(db)
        processor.load_zones([{
            "id": z.id,
            "name": z.name,
            "coordinates": z.coordinates
        } for z in zones])
        
        # Process video
        results = processor.process_video(temp_path)
        
        # Calculate statistics
        total_frames = len(results)
        max_persons = max([r['person_count'] for r in results]) if results else 0
        avg_persons = sum([r['person_count'] for r in results]) / total_frames if results else 0
        
        return {
            "status": "processed",
            "total_frames": total_frames,
            "max_persons_detected": max_persons,
            "average_persons": round(avg_persons, 2)
        }
    finally:
        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)


# ==================== WEBSOCKET ====================

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Wait for messages
            data = await websocket.receive_text()
            
            # Echo back (can be customized for specific actions)
            await websocket.send_json({
                "type": "echo",
                "message": data
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ==================== DEMO DATA ====================

@app.post("/api/demo/populate")
async def populate_demo_data(db: Session = Depends(get_db)):
    """Populate database with demo data"""
    # Create demo zones
    zones_data = [
        {
            "name": "Entrance",
            "coordinates": [[50, 50], [200, 50], [200, 150], [50, 150]],
            "zone_type": "entrance",
            "description": "Main entrance area"
        },
        {
            "name": "Product Zone A",
            "coordinates": [[250, 100], [450, 100], [450, 300], [250, 300]],
            "zone_type": "product_area",
            "description": "Electronics section"
        },
        {
            "name": "Checkout",
            "coordinates": [[500, 50], [650, 50], [650, 150], [500, 150]],
            "zone_type": "checkout",
            "description": "Checkout counters"
        }
    ]
    
    created_zones = []
    for zone_data in zones_data:
        zone = crud.create_zone(
            db,
            zone_data["name"],
            zone_data["coordinates"],
            zone_data["zone_type"],
            zone_data["description"]
        )
        created_zones.append(zone.id)
    
    # Create demo customers
    demo_customers = []
    for i in range(10):
        customer_id = generate_customer_id()
        age = 25 + (i * 3)
        gender = "male" if i % 2 == 0 else "female"
        customer = crud.create_customer(db, customer_id, age, gender)
        demo_customers.append(customer)
    
    return {
        "status": "success",
        "zones_created": len(created_zones),
        "customers_created": len(demo_customers)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
