# 🎯 OskarTrack AI - Customer Tracking System

**Developed by Mr.OSKAR**

An intelligent customer tracking and analytics system powered by AI, designed to monitor customer behavior, movement patterns, and store analytics in real-time.

---

## 📋 Table of Contents

- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Web Dashboard](#web-dashboard)
- [Database Schema](#database-schema)
- [Zone Management](#zone-management)
- [Deployment](#deployment)
- [Future Enhancements](#future-enhancements)

---

## ✨ Features

### Core Features
- **🤖 AI-Powered Person Detection** - Uses OpenCV HOG detector for person detection
- **👥 Customer Tracking** - Track individual customers across store visits
- **🗺️ Zone Analytics** - Define custom zones and track customer movement
- **⏱️ Dwell Time Analysis** - Measure how long customers spend in different areas
- **📊 Real-time Analytics** - Live dashboards with visitor statistics
- **🔌 WebSocket Support** - Real-time updates via WebSocket connections
- **📸 Image/Video Processing** - Upload and analyze images and videos
- **💾 PostgreSQL Database** - Robust data storage with full analytics

### Analytics & Reporting
- Daily/Hourly visitor statistics
- Peak hour identification
- Visitor type breakdown (new vs returning)
- Zone performance metrics
- 7-day trend analysis
- Dwell time per zone

---

## 🛠️ Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11** - Programming language
- **PostgreSQL** - Database (Neon-backed)
- **SQLAlchemy** - ORM for database operations
- **Uvicorn** - ASGI server

### AI & Computer Vision
- **OpenCV** - Computer vision library for person detection
- **NumPy** - Numerical computing
- **SciPy** - Scientific computing for tracking algorithms

### Frontend
- **HTML5/CSS3/JavaScript** - Core web technologies
- **Bootstrap 5** - Responsive UI framework
- **Chart.js** - Interactive charts and graphs
- **Font Awesome** - Icons

---

## 📁 Project Structure

```
/oskartrack/
├── api/
│   ├── __init__.py
│   └── main.py              # FastAPI application & all endpoints
├── database/
│   ├── __init__.py
│   ├── models.py            # SQLAlchemy database models
│   ├── engine.py            # Database connection & session management
│   └── crud.py              # CRUD operations
├── ai_models/
│   ├── __init__.py
│   ├── detector.py          # Person detection using OpenCV HOG
│   └── processor.py         # Video/image processing pipeline
├── utils/
│   ├── __init__.py
│   └── helpers.py           # Utility functions
├── web/
│   ├── index.html           # Home page
│   ├── dashboard.html       # Analytics dashboard
│   ├── live.html            # Live tracking & upload
│   ├── clients.html         # Customer management
│   ├── zones.html           # Zone management
│   ├── style.css            # Styles
│   └── script.js            # Shared JavaScript
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore file
└── README.md               # This file
```

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.11+
- PostgreSQL database (automatically provided by Replit)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- FastAPI & Uvicorn (web framework & server)
- SQLAlchemy & Psycopg2 (database)
- OpenCV, NumPy, SciPy (AI & computer vision)
- WebSockets (real-time updates)
- And other required packages

### 2. Environment Variables

The following environment variables are automatically set by Replit:
- `DATABASE_URL` - PostgreSQL connection string
- `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE` - Database credentials

For local development, create a `.env` file:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/oskartrack
```

### 3. Initialize Database

The database is automatically initialized when the application starts. All tables are created from SQLAlchemy models.

---

## 🏃 Running the Application

### On Replit

The application runs automatically! Just click the **Run** button.

The workflow is configured to start the server on port 5000:
```bash
uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload
```

### Locally

```bash
# Start the server
uvicorn api.main:app --host 0.0.0.0 --port 5000 --reload

# Access the application
# Open: http://localhost:5000/web/index.html
```

### Access Points

- **Home Page**: `/web/index.html`
- **Dashboard**: `/web/dashboard.html`
- **Live Tracking**: `/web/live.html`
- **Customers**: `/web/clients.html`
- **Zones**: `/web/zones.html`
- **API Docs**: `/docs` (Swagger UI)
- **API**: `/api/*`

---

## 📡 API Documentation

### Health Check
```http
GET /
GET /api/health
```

### Customer Endpoints

#### Get All Customers
```http
GET /api/customers?skip=0&limit=100
```

#### Get Customer Details
```http
GET /api/customers/{customer_id}
```

#### Create Customer
```http
POST /api/customers?age=25&gender=male
```

### Visit Endpoints

#### Get Active Visits
```http
GET /api/visits/active
```

#### Start Visit
```http
POST /api/visits/start?customer_id=CUST_XXX
```

#### End Visit
```http
POST /api/visits/{visit_id}/end
```

### Zone Endpoints

#### Get All Zones
```http
GET /api/zones
```

#### Create Zone
```http
POST /api/zones
Content-Type: application/json

{
  "name": "Entrance",
  "coordinates": [[50, 50], [200, 50], [200, 150], [50, 150]],
  "zone_type": "entrance",
  "description": "Main entrance area"
}
```

### Analytics Endpoints

#### Daily Analytics
```http
GET /api/analytics/daily?date=2024-11-24
```

#### Hourly Distribution
```http
GET /api/analytics/hourly?date=2024-11-24
```

#### Zone Statistics
```http
GET /api/analytics/zones
```

#### 7-Day Summary
```http
GET /api/analytics/summary?days=7
```

### Processing Endpoints

#### Process Image
```http
POST /api/process/image
Content-Type: multipart/form-data

file: <image_file>
```

#### Process Video
```http
POST /api/process/video
Content-Type: multipart/form-data

file: <video_file>
```

### Demo Data

#### Populate Demo Data
```http
POST /api/demo/populate
```
Creates 3 demo zones and 10 demo customers.

### WebSocket

#### Real-time Updates
```javascript
const ws = new WebSocket('ws://localhost:5000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log(data);
};
```

---

## 🌐 Web Dashboard

### Home Page
- Real-time statistics
- Total visitors today
- Active visitors
- Average duration
- Active zones

### Analytics Dashboard
- Hourly visitor distribution chart
- Visitor types (new vs returning)
- Zone performance bar chart
- 7-day trend line chart

### Live Tracking
- Upload images/videos for analysis
- Real-time activity log
- Active visits table
- WebSocket live updates

### Customer Management
- View all customers
- Search and filter
- Customer visit history
- Demographics (age, gender)

### Zone Management
- List all zones
- Zone statistics
- Create demo zones
- Zone performance charts

---

## 🗄️ Database Schema

### Tables

#### `customers`
- Customer tracking and demographics
- Fields: customer_id, first_seen, last_seen, total_visits, estimated_age, estimated_gender

#### `visits`
- Individual visit sessions
- Fields: entry_time, exit_time, duration, path_data, zones_visited

#### `zones`
- Store zones/areas
- Fields: name, coordinates, zone_type, total_visitors, average_dwell_time

#### `tracking_events`
- Real-time tracking events
- Fields: event_type, timestamp, position_x, position_y, zone_id

#### `analytics_summary`
- Daily/hourly analytics
- Fields: summary_date, total_visitors, unique_visitors, peak_hour

---

## 🗺️ Zone Management

### Zone Types

1. **Entrance** - Entry points to the store
2. **Product Area** - Shopping and browsing zones
3. **Checkout** - Payment and exit areas
4. **Exit** - Exit points from the store

### Creating Zones

Zones are defined as polygons with coordinate arrays:

```json
{
  "name": "Electronics Section",
  "coordinates": [[100, 100], [300, 100], [300, 250], [100, 250]],
  "zone_type": "product_area",
  "description": "Electronics and gadgets"
}
```

### Zone Analytics

Each zone tracks:
- Total visitors
- Average dwell time
- Peak hours
- Customer paths

---

## 🚀 Deployment

### Replit Deployment

This application is already configured for Replit deployment:
1. The workflow automatically starts the server
2. Database is provided by Replit
3. Port 5000 is exposed for web access

### Manual Deployment

For deployment on other platforms:

1. **Set Environment Variables**
   ```bash
   DATABASE_URL=your_postgres_url
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run with Production Server**
   ```bash
   uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
   ```

---

## 🔮 Future Enhancements

### Phase 1 (Current) ✅
- ✅ Basic person detection with OpenCV
- ✅ Customer tracking and analytics
- ✅ Zone management
- ✅ Web dashboard with charts
- ✅ REST API
- ✅ PostgreSQL integration

### Phase 2 (Recommended for Production)
- **YOLOv8 Integration** - More accurate person detection
- **DeepSORT Tracking** - Advanced multi-object tracking
- **Face Recognition** - Identify returning customers with InsightFace
- **Age & Gender Detection** - Demographic analytics
- **IP Camera Integration** - Real-time video stream processing
- **Export Features** - CSV/Excel/PDF reports
- **Alerts & Notifications** - Email/SMS notifications for events
- **Heat Maps** - Visual representation of customer movement

### Phase 3 (Advanced)
- **Multi-store Support** - Manage multiple locations
- **Predictive Analytics** - ML-based foot traffic prediction
- **Customer Behavior Patterns** - AI-powered insights
- **Mobile App** - iOS/Android companion app
- **Integration with POS** - Link with sales data
- **Privacy Controls** - GDPR compliance features

---

## 📝 Notes

### AI Model Considerations

**Current Implementation:**
- Uses OpenCV HOG (Histogram of Oriented Gradients) for person detection
- CPU-friendly and works well in Replit environment
- Suitable for development and testing

**Production Recommendations:**
For production deployment on dedicated servers with GPU:
- YOLOv8 for real-time object detection
- DeepSORT for multi-object tracking
- InsightFace for face recognition
- GPU acceleration for better performance

### Performance

- The system is optimized for Replit's environment
- Processes every 5th frame for video analysis
- Uses headless OpenCV (no display required)
- Efficient database queries with indexes

### Security

- Environment variables for sensitive data
- PostgreSQL with proper authentication
- Input validation on all endpoints
- CORS configured for security

---

## 👨‍💻 Developer Information

**Developed by:** Mr.OSKAR  
**Version:** 1.0.0  
**License:** Proprietary  
**Support:** Contact Mr.OSKAR for support and customization

---

## 🙏 Acknowledgments

- FastAPI - Modern web framework
- OpenCV - Computer vision library
- Chart.js - Beautiful charts
- Bootstrap - Responsive UI
- Replit - Development platform

---

**© 2024 OskarTrack AI System - All Rights Reserved**

---

For questions, issues, or feature requests, please contact Mr.OSKAR.
