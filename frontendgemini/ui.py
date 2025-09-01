from nicegui import ui
import httpx
import logging

# Configure logging
logger = logging.getLogger(__name__)

# --- Helper Functions for API calls ---

async def run_ai_test_api(system_prompt: str, user_context: str):
    """Calls the /ai-test endpoint."""
    API_URL = "http://localhost:8000/ai-test"
    async with httpx.AsyncClient(timeout=300.0) as client:
        request_data = {"system_prompt": system_prompt, "user_context": user_context}
        logger.info(f"Sending request to {API_URL}")
        response = await client.post(API_URL, json=request_data)
        response.raise_for_status()
        return response.json()

async def run_health_check_api():
    """Calls the /health endpoint."""
    API_URL = "http://localhost:8000/health"
    async with httpx.AsyncClient() as client:
        logger.info(f"Sending request to {API_URL}")
        response = await client.get(API_URL)
        response.raise_for_status()
        return response.json()

async def run_simple_prompt_api(prompt: str, model_path: str):
    """Calls a simple prompt endpoint."""
    API_URL = f"http://localhost:8000{model_path}"
    async with httpx.AsyncClient(timeout=300.0) as client:
        request_data = {"prompt": prompt}
        logger.info(f"Sending request to {API_URL}")
        response = await client.post(API_URL, json=request_data)
        response.raise_for_status()
        return response.json()

# --- UI Page Definitions ---

def render_header():
    """Renders the navigation header."""
    with ui.header().classes('bg-primary text-white'):
        with ui.row().classes('w-full items-center justify-between'):
            ui.label('InkAndQuill V2 POC').classes('text-h6')
            with ui.row():
                ui.link('AI Test', '/').classes('text-white')
                ui.link('Other Tools', '/tools').classes('text-white')

@ui.page('/')
def index_page():
    """Main page for the POC frontend, focusing on the /ai-test endpoint."""
    render_header()
    ui.label('AI Test Interface').classes('text-h4 font-bold text-center my-4')

    with ui.card().classes('w-full max-w-2xl mx-auto'):
        system_prompt_input = ui.textarea('System Prompt').props('outlined').classes('w-full')
        user_context_input = ui.textarea('User Context').props('outlined').classes('w-full')
        submit_button = ui.button('Run AI Test', on_click=lambda: handle_ai_test_submission()).props('color=primary').classes('w-full')

    result_card = ui.card().classes('w-full max-w-2xl mx-auto mt-4').style('display: none;')
    spinner = ui.spinner(size='lg', color='primary').classes('absolute-center')
    spinner.visible = False

    async def handle_ai_test_submission():
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
                ui.label('AI Test Complete').classes('text-h6 font-bold')
                ui.separator()
                ui.label(f"Log ID: {result.get('id')}").classes('font-mono')
                ui.label(f"Response Time: {result.get('response_time_ms')} ms").classes('font-mono')
                with ui.expansion('AI Result', icon='psychology'):
                    ui.markdown(result.get('ai_result', ''))
                with ui.expansion('File URL', icon='storage'):
                    ui.link(result.get('file_url'), result.get('file_url'), target='_blank')
                with ui.expansion('Containers Tested', icon='memory'):
                    for container, status in result.get('containers_tested', {}).items():
                        ui.label(f"{container}: {status}").classes(f"text-{'green' if status == 'success' else 'red'}-600")
            result_card.style('display: block;')
        except Exception as e:
            logger.error(f"Error during AI test: {e}")
            ui.notify(f"An error occurred: {e}", type='negative', multi_line=True)
        finally:
            submit_button.enable()
            spinner.visible = False

@ui.page('/tools')
def tools_page():
    """Page for utility and simple AI endpoints."""
    render_header()
    ui.label('Utility Endpoints').classes('text-h4 font-bold text-center my-4')

    # Health Check
    with ui.card().classes('w-full max-w-2xl mx-auto'):
        ui.label('Health Check').classes('text-h6 font-bold')
        ui.button('Run Health Check', on_click=handle_health_check)
        health_results_div = ui.html()

    # Simple Prompts
    with ui.card().classes('w-full max-w-2xl mx-auto mt-4'):
        ui.label('Simple AI Prompts').classes('text-h6 font-bold')
        prompt_input = ui.textarea('Prompt').props('outlined').classes('w-full')
        model_select = ui.select({
            '/google-ai/gemini': 'Google AI Gemini',
            '/openrouter/simple': 'OpenRouter Simple',
            '/openrouter/langchain': 'OpenRouter LangChain',
            '/openrouter/langgraph': 'OpenRouter LangGraph',
        }, label='Model').classes('w-full')
        ui.button('Send Prompt', on_click=lambda: handle_simple_prompt())
        simple_prompt_result_card = ui.card().classes('w-full mt-2').style('display: none;')

    async def handle_health_check():
        try:
            results = await run_health_check_api()
            html = "<ul>"
            for service, data in results.get('containers', {}).items():
                status = data.get('status', 'unknown')
                color = 'green' if status == 'healthy' else 'red'
                html += f"<li><strong>{service.title()}:</strong> <span style='color:{color};'>{status}</span></li>"
            html += "</ul>"
            health_results_div.set_content(html)
        except Exception as e:
            logger.error(f"Error during health check: {e}")
            ui.notify(f"An error occurred: {e}", type='negative')

    async def handle_simple_prompt():
        if not prompt_input.value or not model_select.value:
            ui.notify('Prompt and Model are required.', type='warning')
            return

        try:
            result = await run_simple_prompt_api(prompt_input.value, model_select.value)
            with simple_prompt_result_card:
                simple_prompt_result_card.clear()
                ui.label(f"Response from {result.get('service_type')}").classes('text-h6')
                ui.markdown(result.get('response'))
            simple_prompt_result_card.style('display: block;')
        except Exception as e:
            logger.error(f"Error during simple prompt: {e}")
            ui.notify(f"An error occurred: {e}", type='negative', multi_line=True)