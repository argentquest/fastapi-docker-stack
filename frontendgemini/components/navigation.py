from nicegui import ui

def create_navigation(prefix: str):
    """
    Creates a stylish, reusable navigation header.
    """
    with ui.header().classes('bg-gray-800 text-white shadow-md'):
        with ui.row().classes('w-full items-center justify-between p-2'):
            with ui.row().classes('items-center'):
                ui.icon('auto_awesome', classes='text-2xl text-blue-400 mr-2')
                ui.label('Gemini Frontend').classes('text-lg font-bold')

            with ui.row().classes('items-center space-x-4'):
                ui.link('Dashboard', f'{prefix}/').classes('hover:text-blue-400')
                ui.link('AI Test', f'{prefix}/ai_test').classes('hover:text-blue-400')
                ui.link('API Explorer', f'{prefix}/api_explorer').classes('hover:text-blue-400')
                ui.link('Health', f'{prefix}/health').classes('hover:text-blue-400')
