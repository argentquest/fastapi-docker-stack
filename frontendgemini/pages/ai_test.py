from nicegui import ui
from frontendgemini.utils.api import run_ai_test_api

def create_ai_test_page():
    """Creates the page for the AI Test workflow."""
    with ui.column().classes('w-full items-center'):
        ui.label('Core AI Test Workflow').classes('text-4xl font-bold mt-8 mb-4')
        ui.label('Submit a system prompt and user context to run the full end-to-end test.').classes('text-lg text-gray-600 mb-8')

        with ui.card().classes('w-full max-w-3xl'):
            with ui.row().classes('w-full no-wrap'):
                system_prompt_input = ui.textarea('System Prompt').props('outlined dense').classes('w-1/2')
                user_context_input = ui.textarea('User Context').props('outlined dense').classes('w-1/2')
            
            submit_button = ui.button('Run AI Test', on_click=lambda: handle_submission()).props('color=primary').classes('w-full mt-4')

    result_card = ui.card().classes('w-full max-w-3xl mt-4').style('display: none;')
    spinner = ui.spinner(size='lg', color='primary').classes('absolute-center')
    spinner.visible = False

    async def handle_submission():
        if not system_prompt_input.value or not user_context_input.value:
            ui.notify('Both System Prompt and User Context are required.', type='warning')
            return

        submit_button.disable()
        spinner.visible = True
        result_card.style('display: none;')

        try:
            result = await run_ai_test_api(system_prompt_input.value, user_context_input.value)
            
            with result_card:
                result_card.clear()
                ui.label('Test Complete').classes('text-2xl font-semibold')
                ui.separator().classes('my-4')
                
                with ui.grid(columns=2).classes('w-full gap-4'):
                    ui.label('Log ID:').classes('font-bold')
                    ui.label(f"{result.get('id')}").classes('font-mono')
                    
                    ui.label('Response Time:').classes('font-bold')
                    ui.label(f"{result.get('response_time_ms')} ms").classes('font-mono')

                with ui.expansion('AI Result', icon='psychology').classes('w-full mt-4 border rounded-lg'):
                    ui.markdown(result.get('ai_result', 'No result returned.'))

                with ui.expansion('File URL', icon='storage').classes('w-full border rounded-lg'):
                    ui.link(result.get('file_url'), result.get('file_url'), target='_blank')

                with ui.expansion('Containers Tested', icon='memory').classes('w-full border rounded-lg'):
                    for container, status in result.get('containers_tested', {}).items():
                        with ui.row().classes('items-center'):
                            ui.icon('check_circle' if status == 'success' else 'cancel', color='green-500' if status == 'success' else 'red-500')
                            ui.label(f"{container}:").classes('font-semibold')
                            ui.label(status).classes(f"text-{'green-600' if status == 'success' else 'red-600'}")
            
            result_card.style('display: block;')
        except Exception as e:
            ui.notify(f"An error occurred: {e}", type='negative', multi_line=True)
        finally:
            submit_button.enable()
            spinner.visible = False
