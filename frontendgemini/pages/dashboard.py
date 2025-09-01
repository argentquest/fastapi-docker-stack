from nicegui import ui

def create_dashboard_page(prefix: str):
    """Creates the visually appealing dashboard page."""
    with ui.column().classes('w-full items-center'):
        ui.label('Gemini Frontend Dashboard').classes('text-4xl font-bold mt-8 mb-4')
        ui.label('A modern UI for the InkAndQuill V2 POC').classes('text-lg text-gray-600 mb-8')

        with ui.row().classes('justify-center gap-8'):
            # Card for AI Test
            with ui.card().classes('w-64 text-center hover:shadow-xl transition-shadow'):
                ui.icon('psychology', size='xl').classes('text-blue-500 mx-auto')
                ui.label('AI Test').classes('text-xl font-semibold my-2')
                ui.label('Run the core end-to-end test workflow.').classes('text-sm text-gray-500 mb-4')
                ui.button('Go to AI Test', on_click=lambda: ui.open(f'{prefix}/ai_test')).props('color=primary flat')

            # Card for API Explorer
            with ui.card().classes('w-64 text-center hover:shadow-xl transition-shadow'):
                ui.icon('travel_explore', size='xl').classes('text-green-500 mx-auto')
                ui.label('API Explorer').classes('text-xl font-semibold my-2')
                ui.label('Interact with simple AI prompt endpoints.').classes('text-sm text-gray-500 mb-4')
                ui.button('Go to Explorer', on_click=lambda: ui.open(f'{prefix}/api_explorer')).props('color=primary flat')

            # Card for Health Check
            with ui.card().classes('w-64 text-center hover:shadow-xl transition-shadow'):
                ui.icon('monitor_heart', size='xl').classes('text-red-500 mx-auto')
                ui.label('System Health').classes('text-xl font-semibold my-2')
                ui.label('Check the status of all backend services.').classes('text-sm text-gray-500 mb-4')
                ui.button('Check Health', on_click=lambda: ui.open(f'{prefix}/health')).props('color=primary flat')
