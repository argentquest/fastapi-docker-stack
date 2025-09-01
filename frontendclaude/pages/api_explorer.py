# API Explorer Page
"""
Generic API endpoint testing interface.
"""

from nicegui import ui
from ..components.navigation import Navigation
from ..utils.helpers import format_json
import httpx
import json


def create_api_explorer_page():
    """Create the API explorer page."""
    
    # Page header
    Navigation.create_page_header(
        "API Explorer", 
        "Test any API endpoint"
    )
    
    # Quick endpoint shortcuts
    with Navigation.create_card("Quick Endpoints", "bolt"):
        ui.label("Common API endpoints").classes('text-body2 text-grey-7 q-mb-md')
        
        with ui.row().classes('w-full'):
            ui.button("Health Check", 
                     on_click=lambda: set_endpoint('GET', '/health'),
                     icon="health_and_safety").classes('q-mr-xs')
            ui.button("Google AI Test", 
                     on_click=lambda: set_endpoint('GET', '/google-ai/test'),
                     icon="smart_toy").classes('q-mr-xs')
            ui.button("AI Test", 
                     on_click=lambda: set_endpoint('POST', '/ai-test'),
                     icon="psychology").classes('q-mr-xs')
            ui.button("API Docs", 
                     on_click=lambda: ui.open("/docs"),
                     icon="description").classes('q-mr-xs')
    
    # Main testing interface
    with ui.row().classes('w-full'):
        # Left side - Request configuration
        with ui.column().classes('col-6'):
            with Navigation.create_card("Request Configuration", "settings"):
                # HTTP method and endpoint
                with ui.row().classes('w-full'):
                    method_select = ui.select(['GET', 'POST', 'PUT', 'DELETE'], 
                                            value='GET',
                                            label="Method").classes('col-3')
                    
                    endpoint_input = ui.input(label="Endpoint", 
                                            placeholder="/health",
                                            value="/health").classes('col-9')
                
                # Request body (for POST/PUT)
                body_input = ui.textarea(label="Request Body (JSON)", 
                                       placeholder='{"key": "value"}',
                                       value="").classes('w-full').style('height: 200px')
                
                # Headers
                headers_input = ui.textarea(label="Custom Headers (JSON)", 
                                          placeholder='{"Content-Type": "application/json"}',
                                          value="").classes('w-full').style('height: 100px')
                
                # Send button
                send_btn = ui.button("Send Request", 
                                   on_click=lambda: send_request(),
                                   icon="send").classes('w-full')
        
        # Right side - Response display
        with ui.column().classes('col-6'):
            with Navigation.create_card("Response", "code"):
                # Response status
                response_status = ui.label("Ready to send request").classes('text-body2')
                
                # Response body
                response_body = ui.textarea(label="Response Body", 
                                          value="").classes('w-full').style('height: 400px')
                response_body.props('readonly')
                
                # Response headers
                response_headers = ui.textarea(label="Response Headers", 
                                             value="").classes('w-full').style('height: 150px')
                response_headers.props('readonly')
    
    def set_endpoint(method: str, endpoint: str):
        """Set endpoint for quick testing."""
        method_select.value = method
        endpoint_input.value = endpoint
        
        # Set default body for POST endpoints
        if method == 'POST' and endpoint == '/ai-test':
            body_input.value = json.dumps({
                "system_prompt": "You are a helpful assistant.",
                "user_context": "Hello, this is a test message."
            }, indent=2)
        elif method == 'POST' and 'prompt' in endpoint:
            body_input.value = json.dumps({
                "prompt": "Hello, this is a test prompt."
            }, indent=2)
        else:
            body_input.value = ""
    
    async def send_request():
        """Send the configured API request."""
        send_btn.props('loading')
        response_status.text = "🔄 Sending request..."
        
        try:
            # Parse configuration
            method = method_select.value
            endpoint = endpoint_input.value
            
            # Build full URL
            base_url = "http://localhost:8001"  # Same port as FastAPI
            full_url = f"{base_url}{endpoint}"
            
            # Parse headers
            headers = {"Content-Type": "application/json"}
            if headers_input.value.strip():
                try:
                    custom_headers = json.loads(headers_input.value)
                    headers.update(custom_headers)
                except json.JSONDecodeError:
                    response_status.text = "❌ Invalid headers JSON"
                    return
            
            # Parse request body
            body_data = None
            if method in ['POST', 'PUT'] and body_input.value.strip():
                try:
                    body_data = json.loads(body_input.value)
                except json.JSONDecodeError:
                    response_status.text = "❌ Invalid request body JSON"
                    return
            
            # Send request
            async with httpx.AsyncClient(timeout=60.0) as client:
                if method == 'GET':
                    response = await client.get(full_url, headers=headers)
                elif method == 'POST':
                    response = await client.post(full_url, json=body_data, headers=headers)
                elif method == 'PUT':
                    response = await client.put(full_url, json=body_data, headers=headers)
                elif method == 'DELETE':
                    response = await client.delete(full_url, headers=headers)
            
            # Display response
            status_code = response.status_code
            status_color = 'positive' if 200 <= status_code < 300 else 'warning' if 300 <= status_code < 400 else 'negative'
            
            response_status.text = f"Status: {status_code} {response.reason_phrase}"
            response_status.classes(f'text-{status_color}')
            
            # Response body
            try:
                response_json = response.json()
                response_body.value = format_json(response_json)
            except:
                response_body.value = response.text
            
            # Response headers
            headers_dict = dict(response.headers)
            response_headers.value = format_json(headers_dict)
            
        except httpx.TimeoutException:
            response_status.text = "❌ Request timeout"
            response_status.classes('text-negative')
            response_body.value = "Request timed out after 60 seconds"
            
        except httpx.ConnectError:
            response_status.text = "❌ Connection failed"
            response_status.classes('text-negative')
            response_body.value = "Could not connect to the server. Make sure the FastAPI server is running."
            
        except Exception as e:
            response_status.text = f"❌ Error: {str(e)}"
            response_status.classes('text-negative')
            response_body.value = f"Request failed: {str(e)}"
            
        finally:
            send_btn.props('loading=false')