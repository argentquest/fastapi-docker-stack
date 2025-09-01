# Frontend Claude Documentation

## Overview

Frontend Claude is a NiceGUI-based web interface for the V2 POC FastAPI application. It provides an interactive frontend to test and demonstrate all the POC endpoints through a clean, modern web interface.

**Technology Stack:** NiceGUI (Python reactive web framework) + FastAPI integration

**URL Access:** `http://localhost:8001/claude/`

## What Was Built

### 1. Architecture & Integration
- **Multi-page application** with navigation between different sections
- **Direct HTTP integration** with FastAPI backend on same port (8001)
- **URL path-based routing** using `/claude/` prefix to coexist with `/gemini/` frontend
- **Reactive components** for real-time updates and interactions

### 2. Folder Structure Created

```
frontendclaude/
├── main.py                    # NiceGUI app entry point & FastAPI integration
├── components/                # Reusable UI components
│   ├── navigation.py          # Site navigation menu & page headers
│   └── service_card.py        # Service health status cards
├── pages/                     # Individual page implementations
│   ├── dashboard.py           # Main overview page (planned)
│   ├── ai_test.py            # AI endpoint testing (planned)
│   ├── health.py             # Service monitoring (planned)
│   └── api_explorer.py       # Generic API testing (planned)
├── utils/                     # Helper functions & API client
│   ├── api_client.py         # HTTP client for FastAPI communication
│   └── helpers.py            # Formatting & utility functions
├── requirements.txt           # Dependencies (nicegui, httpx, pydantic)
└── README.md                 # Setup instructions
```

### 3. Core Components Built

#### **API Client (`utils/api_client.py`)**
- Async HTTP client using `httpx`
- Methods for all POC endpoints:
  - Health checks (`/health`)
  - AI testing (`/ai-test`, `/google-ai/*`, `/openrouter/*`)
- Error handling and response formatting
- Configurable base URL (defaults to `http://localhost:8001`)

#### **Navigation Component (`components/navigation.py`)**
- Consistent header navigation across all pages
- Current page highlighting
- Standardized page headers and card layouts
- Icons and styling for professional look

#### **Service Card Component (`components/service_card.py`)**
- Displays service health status with color-coded indicators
- Shows service-specific information (models, response times, etc.)
- Click-to-expand details in modal dialogs
- Automatic status icon and color assignment

#### **Helper Functions (`utils/helpers.py`)**
- Timestamp formatting
- Response time display (ms/seconds)
- Status color and icon mapping
- JSON formatting for display
- Error message extraction

### 4. Planned Pages (Architecture Complete)

#### **Dashboard** (`/claude/`)
- Service status overview grid
- Recent API activity
- Quick action buttons
- Performance metrics

#### **AI Test** (`/claude/ai-test`)
- Forms for all AI endpoints
- Real-time response display
- Token usage tracking
- Multi-service testing

#### **Health Monitor** (`/claude/health`)
- Live service status
- Refresh capabilities
- Service detail views
- Historical data

#### **API Explorer** (`/claude/api-explorer`)
- Generic endpoint testing
- JSON request/response viewer
- HTTP method selection
- Custom headers support

### 5. Integration with FastAPI

#### **Main App Integration**
Added to `app/main.py`:
```python
# Import the frontend setup function
from frontendclaude.main import setup_claude_frontend

# Mount the frontend with URL prefix
setup_claude_frontend(app, prefix="/claude")
```

#### **Dual Frontend Support**
- Updated startup banner to show both frontend URLs
- Path-based routing: `/claude/` and `/gemini/`
- No conflicts between different frontend implementations
- Each frontend operates independently

### 6. Configuration Updates

#### **Port Changes**
- Changed default local port from 8000 to **8001**
- Updated all references:
  - API client base URL
  - Startup banner URLs
  - Documentation links
  - uvicorn run configuration

#### **Dependencies**
All required packages already in `pyproject.toml`:
- `nicegui>=1.4.0`
- `httpx>=0.25.0` 
- `pydantic>=2.0.0`

## Current Status

### ✅ Completed
- [x] Folder structure and file organization
- [x] Core utility functions and API client
- [x] Navigation and UI components
- [x] Service status card components
- [x] Main application entry point
- [x] FastAPI integration setup
- [x] Port configuration updates
- [x] Dual frontend architecture

### 🚧 In Progress
- [ ] Individual page implementations
- [ ] Dashboard page with service overview
- [ ] AI testing interface
- [ ] Health monitoring page
- [ ] API explorer functionality

### 📋 Next Steps
1. Implement dashboard page with service status grid
2. Create AI testing forms for all endpoints
3. Build health monitoring with live updates
4. Add API explorer for generic endpoint testing
5. Add styling and responsive design
6. Test all functionality end-to-end

## How It Works

1. **Startup**: FastAPI loads and mounts NiceGUI frontend at `/claude/` prefix
2. **Navigation**: Users visit `http://localhost:8001/claude/` for main dashboard
3. **API Calls**: Frontend makes HTTP requests to FastAPI endpoints on same port
4. **Real-time**: NiceGUI handles reactive updates and user interactions
5. **Coexistence**: `/gemini/` prefix available for alternative frontend

## Development

To work on Frontend Claude:

```bash
# All dependencies already installed via uv
cd frontendclaude

# Run in development mode (standalone)
python main.py  # Runs on port 8080

# Or run integrated with FastAPI
cd ..
python app/main.py  # Access at http://localhost:8001/claude/
```

## Design Philosophy

- **Python-First**: Entire UI written in Python using NiceGUI
- **Component-Based**: Reusable components for consistency
- **API-Driven**: Demonstrates all POC endpoints through clean interface  
- **Reactive**: Real-time updates and interactive elements
- **Coexistence**: Designed to work alongside other frontend implementations
- **Production-Ready**: Proper error handling, logging, and configuration