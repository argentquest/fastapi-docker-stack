# Dashboard Page
"""
Main dashboard page showing service overview and quick actions.
"""

from nicegui import ui
from ..components.navigation import Navigation
from ..components.service_card import create_services_grid
from ..utils.api_client import api_client
from ..utils.helpers import is_success_response, format_error_details


def create_dashboard_page():
    """Create the main dashboard page."""
    
    ui.label('Frontend Claude Dashboard').classes('text-h4')
    ui.label('Welcome to the V2 POC Interface').classes('text-subtitle1')
    
    # Frontend URLs section
    with ui.card().classes('w-full'):
        ui.label('Frontend Experiments').classes('text-h6')
        ui.label('Two UI approaches for testing and comparison').classes('text-caption text-grey-7')
        
        with ui.row().classes('w-full q-gutter-md'):
            with ui.card().classes('col'):
                ui.icon('smart_toy', size='lg').classes('text-primary')
                ui.label('Frontend Claude').classes('text-subtitle1 font-weight-bold')
                ui.label('NiceGUI-based interface (current)').classes('text-caption')
                ui.link('http://127.0.0.1:8001/claude/', 'http://127.0.0.1:8001/claude/', new_tab=True).classes('text-primary')
            
            with ui.card().classes('col'):
                ui.icon('auto_awesome', size='lg').classes('text-green')
                ui.label('Frontend Gemini').classes('text-subtitle1 font-weight-bold')
                ui.label('Alternative UI (coming soon)').classes('text-caption')
                ui.link('http://127.0.0.1:8001/gemini/', 'http://127.0.0.1:8001/gemini/', new_tab=True).classes('text-green')
    
    # Quick Actions section
    with ui.card().classes('w-full'):
        ui.label('Quick Actions').classes('text-h6')
        with ui.row().classes('w-full q-gutter-md'):
            ui.button('Test API Health', on_click=lambda: test_health(), icon='health_and_safety').classes('col')
            ui.button('View API Docs', on_click=lambda: ui.open('/docs'), icon='description').classes('col')
            ui.button('View GitHub', on_click=lambda: ui.open('https://github.com/argentquest/fastapi-docker-stack'), icon='code').classes('col')
    
    # Service Status section
    with ui.card().classes('w-full'):
        ui.label('Service Status').classes('text-h6')
        status_container = ui.column().classes('w-full')
        
    async def test_health():
        """Test API health and display results."""
        ui.notify('Checking health status...')
        result = await api_client.health_check()
        
        if result.get('status'):
            status = result.get('status')
            color = 'positive' if status == 'healthy' else 'warning' if status == 'degraded' else 'negative'
            ui.notify(f'Health Status: {status}', color=color)
            
            # Update status display
            status_container.clear()
            with status_container:
                for service, info in result.get('containers', {}).items():
                    with ui.row().classes('items-center'):
                        service_status = info.get('status', 'unknown')
                        icon = 'check_circle' if service_status == 'healthy' else 'error' if service_status == 'error' else 'help'
                        color = 'positive' if service_status == 'healthy' else 'negative' if service_status == 'error' else 'grey'
                        ui.icon(icon, size='sm').classes(f'text-{color}')
                        ui.label(f'{service.title()}: {service_status}').classes('text-caption')
        else:
            # Show detailed error information
            error_details = format_error_details(result)
            ui.notify(f'Health check failed: {error_details}', color='negative')
            
            # Update status display with error
            status_container.clear()
            with status_container:
                ui.label('❌ Health Check Failed').classes('text-negative text-subtitle1')
                ui.label(error_details).classes('text-caption text-grey-7')