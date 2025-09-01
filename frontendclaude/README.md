# Frontend Claude - NiceGUI POC Interface

A NiceGUI-based frontend for testing and demonstrating the V2 POC FastAPI endpoints.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the main FastAPI application (which includes this frontend):
```bash
cd ..
python app/main.py
```

3. Access the frontend at: http://localhost:8001/claude/

## Features

- **Dashboard**: Overview of all services and recent activity
- **AI Test**: Interactive testing of all AI endpoints
- **Health Monitor**: Real-time service status monitoring  
- **API Explorer**: Generic endpoint testing interface

## Pages

- `/claude/` - Main dashboard
- `/claude/ai-test` - AI endpoint testing
- `/claude/health` - Service monitoring
- `/claude/api-explorer` - API testing tool

## Architecture

- Built with NiceGUI (Python reactive web framework)
- Makes HTTP calls to FastAPI backend on same port
- Integrated into main FastAPI app via URL prefix
- No separate server process needed