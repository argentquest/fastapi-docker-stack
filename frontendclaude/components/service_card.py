# Service Status Card Component
"""
Reusable component for displaying service health status.
"""

from nicegui import ui
from typing import Dict, Any
from ..utils.helpers import get_status_color, get_status_icon, format_response_time


class ServiceCard:
    """Service health status card component."""
    
    def __init__(self, service_name: str, service_data: Dict[str, Any]):
        self.service_name = service_name
        self.service_data = service_data
        self.card = None
        
    def create(self) -> ui.card:
        """Create the service status card."""
        status = self.service_data.get('status', 'unknown')
        color = get_status_color(status)
        icon = get_status_icon(status)
        
        self.card = ui.card().classes('q-pa-md q-ma-sm')
        
        with self.card:
            with ui.card_section():
                # Header with service name and status icon
                with ui.row().classes('items-center justify-between'):
                    with ui.row().classes('items-center'):
                        ui.icon(icon).classes(f'text-{color} text-h5 q-mr-sm')
                        ui.label(self.service_name.title()).classes('text-h6 font-weight-bold')
                    
                    # Status badge
                    ui.badge(status.title()).classes(f'bg-{color}')
            
            with ui.card_section():
                # Service details
                details = self.service_data.get('details', '')
                if details:
                    ui.label(details).classes('text-body2 text-grey-7')
                
                # Additional info based on service type
                self.add_service_specific_info()
        
        # Click to show more details
        if self.has_detailed_info():
            self.card.classes('cursor-pointer')
            self.card.on('click', self.show_details)
        
        return self.card
    
    def add_service_specific_info(self):
        """Add service-specific information."""
        # Database info
        if 'database' in self.service_name.lower() or 'postgres' in self.service_name.lower():
            if 'pool_size' in self.service_data:
                ui.label(f"Pool Size: {self.service_data['pool_size']}").classes('text-caption')
        
        # AI service info  
        elif any(ai in self.service_name.lower() for ai in ['openrouter', 'google', 'ai']):
            if 'model' in self.service_data:
                ui.label(f"Model: {self.service_data['model']}").classes('text-caption')
        
        # Response time for any service
        if 'response_time_ms' in self.service_data:
            response_time = format_response_time(self.service_data['response_time_ms'])
            ui.label(f"Response: {response_time}").classes('text-caption')
    
    def has_detailed_info(self) -> bool:
        """Check if service has detailed information to show."""
        detail_keys = ['error', 'connection_info', 'config', 'metrics']
        return any(key in self.service_data for key in detail_keys)
    
    def show_details(self):
        """Show detailed service information in a dialog."""
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            with ui.card_section():
                ui.label(f'{self.service_name.title()} Details').classes('text-h6')
            
            with ui.card_section():
                # Show all service data in a readable format
                for key, value in self.service_data.items():
                    if key not in ['status']:  # Skip already displayed info
                        ui.label(f'{key.replace("_", " ").title()}: {value}').classes('text-body2')
            
            with ui.card_actions().classes('justify-end'):
                ui.button('Close', on_click=dialog.close)
        
        dialog.open()


def create_services_grid(services_data: Dict[str, Dict[str, Any]]) -> ui.element:
    """Create a grid of service status cards."""
    with ui.grid(columns=3).classes('w-full q-pa-md') as grid:
        for service_name, service_data in services_data.items():
            card = ServiceCard(service_name, service_data)
            card.create()
    
    return grid