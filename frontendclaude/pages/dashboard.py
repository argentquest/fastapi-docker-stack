# Dashboard Page
"""
Main dashboard page showing service overview and quick actions.
"""

from nicegui import ui
from ..components.navigation import Navigation
from ..components.service_card import create_services_grid
from ..utils.api_client import api_client
from ..utils.helpers import is_success_response


def create_dashboard_page():
    """Create the main dashboard page."""
    
    ui.label('Frontend Claude Dashboard').classes('text-h4')
    ui.label('Welcome to the V2 POC Interface').classes('text-subtitle1')
    
    with ui.card().classes('w-full max-w-md'):
        ui.label('Quick Actions')
        ui.button('Test API Health', on_click=lambda: ui.notify('Health check clicked!'))
        ui.button('View API Docs', on_click=lambda: ui.open('/docs'))
    
    ui.label('This is a simplified dashboard for testing. More features coming soon!')