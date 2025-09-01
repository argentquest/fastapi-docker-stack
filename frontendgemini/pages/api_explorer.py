from nicegui import ui
from frontendgemini.utils.api import run_simple_prompt_api

def create_api_explorer_page():
    """Creates the page for interacting with simple AI endpoints."""
    with ui.column().classes('w-full items-center'):
        ui.label('Simple API Explorer').classes('text-4xl font-bold mt-8 mb-4')
        ui.label('Send a prompt to any of the simple AI models.').classes('text-lg text-gray-600 mb-8')

        with ui.card().classes('w-full max-w-3xl'):
            ui.label('Model Selection').classes('text-xl font-semibold')
            model_select = ui.select({
                '/google-ai/gemini': 'Google AI Gemini',
                '/openrouter/simple': 'OpenRouter Simple',
                '/openrouter/langchain': 'OpenRouter LangChain',
                '/openrouter/langgraph': 'OpenRouter LangGraph',
            }, label='Select a Model Endpoint').classes('w-full').props('outlined')

            prompt_input = ui.textarea('Prompt').props('outlined').classes('w-full mt-4')
            
            submit_button = ui.button('Send Prompt', on_click=lambda: handle_submission()).props('color=primary').classes('w-full mt-4')

    result_card = ui.card().classes('w-full max-w-3xl mt-4').style('display: none;')
    spinner = ui.spinner(size='lg', color='primary').classes('absolute-center')
    spinner.visible = False

    async def handle_submission():
        if not prompt_input.value or not model_select.value:
            ui.notify('Model and Prompt are required.', type='warning')
            return

        submit_button.disable()
        spinner.visible = True
        result_card.style('display: none;')

        try:
            result = await run_simple_prompt_api(prompt_input.value, model_select.value)
            
            with result_card:
                result_card.clear()
                ui.label(f"Response from {result.get('service_type')}").classes('text-2xl font-semibold')
                ui.markdown(result.get('response', 'No response returned.'))
            
            result_card.style('display: block;')
        except Exception as e:
            ui.notify(f"An error occurred: {e}", type='negative', multi_line=True)
        finally:
            submit_button.enable()
            spinner.visible = False
