from nicegui import ui
from fastapi import FastAPI

# Import components and pages
from .components.navigation import create_navigation
from .pages import dashboard, ai_test, health, api_explorer

def setup_gemini_frontend(app: FastAPI, prefix: str, register_only: bool = False):
    """
    Sets up the complete, modular NiceGUI frontend for Gemini.
    """
    
    @ui.page(f'{prefix}/')
    def dashboard_page():
        create_navigation(prefix)
        dashboard.create_dashboard_page(prefix)
    
    @ui.page(f'{prefix}/ai_test')
    def ai_test_page():
        create_navigation(prefix)
        ai_test.create_ai_test_page()
        
    @ui.page(f'{prefix}/health')
    def health_page():
        create_navigation(prefix)
        health.create_health_page()
        
    @ui.page(f'{prefix}/api_explorer')
    def api_explorer_page():
        create_navigation(prefix)
        api_explorer.create_api_explorer_page()