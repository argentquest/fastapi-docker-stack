# Health Monitoring Page
"""
Live monitoring of all service health statuses.
"""

from nicegui import ui
from ..components.navigation import Navigation
from ..components.service_card import create_services_grid
from ..utils.api_client import api_client
from ..utils.helpers import is_success_response


def create_health_page():
    """Create the health monitoring page."""
    
    # Page header
    Navigation.create_page_header(
        "Health Monitor", 
        "Live service status monitoring"
    )
    
    # Control row
    with ui.row().classes('w-full q-pa-md'):
        refresh_btn = ui.button("Refresh All", 
                               on_click=lambda: refresh_health(),
                               icon="refresh").classes('q-mr-md')
        
        auto_refresh_switch = ui.switch("Auto Refresh (10s)").classes('q-mr-md')
        
        last_update = ui.label("Last Update: Never").classes('text-grey-7')
    
    # Overall status card
    with Navigation.create_card("Overall System Status", "monitor_heart"):
        overall_status = ui.label("Loading...").classes('text-h5')
        status_summary = ui.label("").classes('text-body2 text-grey-7')
    
    # Services grid container
    services_container = ui.column().classes('w-full')
    
    # Auto refresh timer
    auto_timer = None
    
    async def refresh_health():
        """Refresh all service health status."""
        refresh_btn.props('loading')
        overall_status.text = "🔄 Checking services..."
        
        try:
            response = await api_client.health_check()
            
            if is_success_response(response):
                status = response.get('status', 'unknown')
                containers = response.get('containers', {})
                
                # Update overall status
                if status == 'healthy':
                    overall_status.text = "✅ All Systems Healthy"
                    overall_status.classes('text-positive')
                elif status == 'degraded':
                    overall_status.text = "⚠️ System Degraded"
                    overall_status.classes('text-warning')
                else:
                    overall_status.text = "❌ System Issues"
                    overall_status.classes('text-negative')
                
                # Count healthy/total services
                total_services = len(containers)
                healthy_services = sum(1 for c in containers.values() if c.get('status') == 'healthy')
                status_summary.text = f"{healthy_services}/{total_services} services healthy"
                
                # Clear and rebuild services grid
                services_container.clear()
                with services_container:
                    if containers:
                        create_services_grid(containers)
                    else:
                        ui.label("No service data available").classes('text-grey-7')
                
            else:
                overall_status.text = "❌ Health Check Failed"
                overall_status.classes('text-negative')
                status_summary.text = "Unable to retrieve service status"
                
        except Exception as e:
            overall_status.text = "❌ Connection Failed"
            overall_status.classes('text-negative')
            status_summary.text = f"Error: {str(e)}"
        
        finally:
            refresh_btn.props('loading=false')
            from datetime import datetime
            last_update.text = f"Last Update: {datetime.now().strftime('%H:%M:%S')}"
    
    def toggle_auto_refresh():
        """Toggle auto refresh."""
        nonlocal auto_timer
        
        if auto_refresh_switch.value:
            # Start auto refresh every 10 seconds
            auto_timer = ui.timer(10.0, refresh_health)
            ui.notify("Auto refresh enabled (10s interval)")
        else:
            # Stop auto refresh
            if auto_timer:
                auto_timer.cancel()
                auto_timer = None
            ui.notify("Auto refresh disabled")
    
    # Setup auto refresh toggle
    auto_refresh_switch.on('update:model-value', toggle_auto_refresh)
    
    # Individual service test functions
    with ui.row().classes('w-full q-pa-md'):
        with Navigation.create_card("Individual Tests", "science"):
            ui.label("Test individual services").classes('text-body2 text-grey-7 q-mb-md')
            
            with ui.row().classes('w-full'):
                ui.button("Test Google AI", 
                         on_click=lambda: test_individual_service('google_ai'),
                         icon="smart_toy").classes('col q-mr-xs')
                ui.button("Test Database", 
                         on_click=lambda: test_individual_service('database'),
                         icon="storage").classes('col q-mr-xs')
                ui.button("Test Redis", 
                         on_click=lambda: test_individual_service('redis'),
                         icon="memory").classes('col q-mr-xs')
                ui.button("Test MinIO", 
                         on_click=lambda: test_individual_service('minio'),
                         icon="folder").classes('col')
    
    async def test_individual_service(service_name: str):
        """Test an individual service."""
        ui.notify(f"Testing {service_name}...")
        
        try:
            if service_name == 'google_ai':
                response = await api_client.google_ai_test()
                if response.get('status') == 'success':
                    ui.notify("✅ Google AI is working!", type='positive')
                else:
                    ui.notify(f"❌ Google AI failed: {response.get('message', 'Unknown error')}", type='negative')
            else:
                # For other services, refresh the main health check
                await refresh_health()
                ui.notify(f"Health check refreshed for {service_name}")
                
        except Exception as e:
            ui.notify(f"❌ Error testing {service_name}: {str(e)}", type='negative')
    
    # Initial load
    ui.timer(0.1, refresh_health, once=True)