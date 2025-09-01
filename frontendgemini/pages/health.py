from nicegui import ui
from frontendgemini.utils.api import run_health_check_api

def create_health_page():
    """Creates the page for viewing system health status."""
    with ui.column().classes('w-full items-center'):
        ui.label('System Health Status').classes('text-4xl font-bold mt-8 mb-4')
        ui.label('Check the real-time status of all backend services.').classes('text-lg text-gray-600 mb-8')

        results_div = ui.html().classes('w-full max-w-md p-4 border rounded-lg shadow-sm')
        
        async def get_health():
            """Fetches and displays health status."""
            try:
                results = await run_health_check_api()
                html = "<div class='space-y-2'>"
                for service, data in results.get('containers', {}).items():
                    status = data.get('status', 'unknown')
                    color = 'text-green-500' if status == 'healthy' else 'text-red-500'
                    icon = 'check_circle' if status == 'healthy' else 'cancel'
                    
                    html += f"""
                        <div class='flex items-center justify-between p-2 border-b'>
                            <span class='font-bold text-lg'>{service.title()}</span>
                            <div class='flex items-center gap-2'>
                                <i class='material-icons {color}'>{icon}</i>
                                <span class='font-semibold {color}'>{status.title()}</span>
                            </div>
                        </div>
                    """
                html += "</div>"
                results_div.set_content(html)
            except Exception as e:
                results_div.set_content(f"<p class='text-red-500'>Error fetching health status: {e}</p>")

        # Automatically load health status on page load
        ui.timer(0.1, get_health, once=True)
        
        ui.button('Refresh Status', on_click=get_health, icon='refresh').props('color=primary').classes('mt-4')
