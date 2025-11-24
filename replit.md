# OskarTrack AI - Customer Tracking System

## Overview

OskarTrack AI is an intelligent customer tracking and analytics system that monitors customer behavior, movement patterns, and store analytics in real-time. The system uses computer vision (OpenCV HOG detector) to detect and track individuals, analyze their movement through defined zones, measure dwell times, and provide comprehensive analytics dashboards. It features a FastAPI backend with WebSocket support for real-time updates, a web-based dashboard for visualization, and PostgreSQL database storage for analytics data.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
**Problem**: Provide intuitive, real-time visualization of customer tracking data and analytics.

**Solution**: Multi-page web application using vanilla JavaScript with Bootstrap 5 for UI components. The frontend consists of:
- `index.html` - Landing page and system overview
- `dashboard.html` - Analytics visualization with charts and statistics
- `live.html` - Real-time tracking interface with file upload
- `clients.html` - Customer management interface
- `zones.html` - Zone definition and management
- `style.css` - Shared styling with custom dashboard components
- `script.js` - Shared utility functions for formatting and UI operations

**Rationale**: Chose vanilla JavaScript over frameworks for simplicity and ease of deployment on Replit. Bootstrap provides responsive design without additional build tools.

**Pros**: No build process, easy to debug, fast initial load
**Cons**: May require more code for complex state management

### Backend Architecture
**Problem**: Process video/image streams, detect people, track movements, and serve analytics data in real-time.

**Solution**: FastAPI-based REST API with WebSocket support (`api/main.py`). Key components:
- REST endpoints for CRUD operations on customers, visits, zones, and analytics
- WebSocket endpoint for real-time tracking updates via `ConnectionManager` class
- CORS middleware for cross-origin requests
- Static file serving for web dashboard
- Integration with AI processing pipeline

**Rationale**: FastAPI provides async support for WebSocket connections, automatic OpenAPI documentation, and fast performance for real-time requirements.

**Pros**: Built-in async support, automatic API documentation, type validation with Pydantic
**Cons**: Requires understanding of async patterns

### AI/Computer Vision Pipeline
**Problem**: Detect people in images/video streams and track their movement across frames.

**Solution**: Two-layer processing system:
1. **Person Detection** (`ai_models/detector.py`): Uses OpenCV's HOG (Histogram of Oriented Gradients) descriptor with pre-trained SVM for person detection
2. **Video Processing** (`ai_models/processor.py`): Orchestrates detection, tracking, and zone analysis with `VideoProcessor` class and `SimpleTracker` for object persistence

**Alternatives Considered**: YOLOv8 or other modern object detectors mentioned in code comments
**Rationale**: HOG detector chosen for simplicity and lower resource requirements suitable for Replit environment

**Pros**: Lightweight, no GPU required, fast setup
**Cons**: Lower accuracy than modern deep learning approaches, less robust to occlusions

### Data Storage Architecture
**Problem**: Persist customer tracking data, visit sessions, zone definitions, and analytics with efficient querying.

**Solution**: PostgreSQL database with SQLAlchemy ORM (`database/` module):

**Schema Design**:
- `Customer` - Stores unique customer profiles with tracking IDs, demographics (age/gender estimates), face encodings, and visit counts
- `Visit` - Individual visit sessions with entry/exit times, duration, and path tracking
- `Zone` - Defined areas with coordinates (polygon format) for movement analysis
- `TrackingEvent` - Real-time movement events within zones
- `AnalyticsSummary` - Pre-aggregated daily/hourly statistics

**Database Engine** (`database/engine.py`): 
- Primary: PostgreSQL via `DATABASE_URL` environment variable
- Fallback: SQLite for local development when `DATABASE_URL` not set
- Session management via `SessionLocal` factory pattern

**CRUD Operations** (`database/crud.py`): Abstracted database operations for each model type

**Rationale**: SQLAlchemy ORM provides database-agnostic code with automatic migrations via Alembic. Separate models for raw events and aggregated summaries optimizes query performance.

**Pros**: Type-safe queries, automatic schema migrations, works with multiple database backends
**Cons**: ORM overhead for complex queries

### Zone Analysis System
**Problem**: Track customer movement through defined physical areas and measure engagement.

**Solution**: Polygon-based zone system with point-in-polygon algorithm (`processor.py`):
- Zones defined as coordinate arrays stored in database
- Real-time centroid calculation for detected persons
- Ray-casting algorithm for polygon containment checks
- Zone transition tracking for path analysis

**Rationale**: Flexible polygon shapes accommodate irregular store layouts better than rectangular regions.

**Pros**: Handles complex shapes, mathematically precise
**Cons**: Performance scales with polygon complexity

### Real-time Communication
**Problem**: Push live tracking updates to connected dashboard clients.

**Solution**: WebSocket implementation with `ConnectionManager` class managing multiple concurrent connections. Broadcasts detection events, customer entries/exits, and zone transitions to all connected clients.

**Rationale**: WebSockets provide full-duplex communication with lower latency than HTTP polling for real-time requirements.

**Pros**: Low latency, efficient for frequent updates, standardized protocol
**Cons**: Requires connection management, less compatible with some proxies

### Authentication & Session Management
**Problem**: Secure access to customer tracking data and analytics.

**Solution**: Prepared infrastructure with `python-jose` for JWT tokens and `passlib` for password hashing included in dependencies, but implementation not visible in provided code.

**Note**: Authentication endpoints and middleware not present in current codebase - may be planned for future implementation.

## External Dependencies

### Third-Party Services
- **OpenAI API** (`openai==1.3.7`): Listed in requirements for potential advanced analytics features (not actively used in visible code)

### AI/ML Libraries
- **OpenCV** (`opencv-python-headless==4.8.1.78`): Core computer vision library for person detection using HOG descriptor
- **NumPy** (`numpy==1.26.2`): Array operations for image processing
- **Pillow** (`PIL==10.1.0`): Image loading and manipulation
- **SciPy** (`scipy`): Scientific computing utilities

### Web Framework Stack
- **FastAPI** (`fastapi==0.104.1`): Primary web framework
- **Uvicorn** (`uvicorn[standard]==0.24.0`): ASGI server with WebSocket support
- **WebSockets** (`websockets==12.0`): WebSocket protocol implementation
- **python-multipart** (`python-multipart==0.0.6`): Multipart form data parsing for file uploads
- **aiofiles** (`aiofiles==23.2.1`): Async file operations

### Database Stack
- **SQLAlchemy** (`sqlalchemy==2.0.23`): ORM and database toolkit
- **psycopg2-binary** (`psycopg2-binary==2.9.9`): PostgreSQL adapter (with SQLite fallback)
- **Alembic** (`alembic==1.12.1`): Database migration tool

### Security & Authentication
- **python-jose[cryptography]** (`python-jose[cryptography]==3.3.0`): JWT token handling
- **passlib[bcrypt]** (`passlib[bcrypt]==1.7.4`): Password hashing

### Utilities
- **Pydantic** (`pydantic==2.5.0`): Data validation and settings management
- **python-dotenv** (`python-dotenv==1.0.0`): Environment variable loading

### Frontend CDN Resources
- **Bootstrap 5.3.0**: UI framework (loaded via CDN)
- **Font Awesome 6.4.0**: Icon library (loaded via CDN)

### Database Configuration
- **Primary Database**: PostgreSQL (production) - configured via `DATABASE_URL` environment variable
- **Fallback Database**: SQLite (`oskartrack.db`) - used when `DATABASE_URL` not set
- **Note**: The system is designed to work with PostgreSQL but includes SQLite fallback for development flexibility