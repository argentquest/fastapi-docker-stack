# Frontend Claude - NiceGUI Main Application
"""
NiceGUI-based frontend for the V2 POC FastAPI application.
This creates a multi-page web interface for testing all POC endpoints.
"""

from nicegui import ui, app
from fastapi import FastAPI
from .components.navigation import Navigation
from .pages import dashboard, ai_test, health, api_explorer


def setup_claude_frontend(fastapi_app: FastAPI, prefix: str = "/claude", register_only: bool = False):
    """
    Setup the NiceGUI frontend with the given FastAPI app.
    
    Args:
        fastapi_app: The FastAPI application instance
        prefix: URL prefix for all frontend routes
        register_only: If True, only register pages without calling ui.run_with()
    """
    
    # Setup routes
    @ui.page(f'{prefix}/')
    def dashboard_page():
        """Dashboard page - main overview."""
        Navigation('dashboard')
        dashboard.create_dashboard_page()
    
    @ui.page(f'{prefix}/ai-test')
    def ai_test_page():
        """AI testing page."""
        Navigation('ai-test')
        ai_test.create_ai_test_page()
    
    @ui.page(f'{prefix}/health')  
    def health_page():
        """Health monitoring page."""
        Navigation('health')
        health.create_health_page()
    
    @ui.page(f'{prefix}/api-explorer')
    def api_explorer_page():
        """API explorer page."""
        Navigation('api-explorer')
        api_explorer.create_api_explorer_page()
    
    # Only configure NiceGUI if not in register_only mode
    if not register_only:
        ui.run_with(fastapi_app, mount_path=prefix, storage_secret='poc-claude-frontend-2025')


# For development/testing - standalone mode
if __name__ == '__main__':
    # Create standalone pages for development
    @ui.page('/')
    def index():
        Navigation('dashboard')
        dashboard.create_dashboard_page()
    
    @ui.page('/ai-test')
    def ai_test():
        Navigation('ai-test') 
        ai_test.create_ai_test_page()
    
    @ui.page('/health')
    def health():
        Navigation('health')
        health.create_health_page()
    
    @ui.page('/api-explorer')
    def api_explorer():
        Navigation('api-explorer')
        api_explorer.create_api_explorer_page()
    
    # Run standalone
    ui.run(port=8080, reload=True, title='Frontend Claude - V2 POC')