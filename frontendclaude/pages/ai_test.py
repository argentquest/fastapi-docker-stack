# AI Testing Page
"""
Interactive testing interface for all AI endpoints.
"""

from nicegui import ui
from ..components.navigation import Navigation
from ..utils.api_client import api_client
from ..utils.helpers import is_success_response, format_response_time, extract_error_message


def create_ai_test_page():
    """Create the AI testing page."""
    
    # Page header
    Navigation.create_page_header(
        "AI Testing", 
        "Test all AI endpoints and models"
    )
    
    # Tabs for different AI services
    with ui.tabs().classes('w-full') as tabs:
        comprehensive_tab = ui.tab('Comprehensive Test')
        google_tab = ui.tab('Google AI')
        google_adk_tab = ui.tab('Google ADK')
        openrouter_tab = ui.tab('OpenRouter')
    
    with ui.tab_panels(tabs, value=comprehensive_tab).classes('w-full'):
        
        # Comprehensive AI Test Tab
        with ui.tab_panel(comprehensive_tab):
            with Navigation.create_card("Comprehensive AI Test", "psychology"):
                ui.label("Tests the complete workflow: AI generation + embedding + storage + database + caching").classes('text-body2 text-grey-7 q-mb-md')
                
                with ui.row().classes('w-full'):
                    with ui.column().classes('col-6'):
                        system_prompt = ui.textarea(
                            label="System Prompt",
                            placeholder="You are a helpful assistant...",
                            value="You are a helpful AI assistant. Provide clear and informative responses."
                        ).classes('w-full')
                        
                        user_context = ui.textarea(
                            label="User Context", 
                            placeholder="Enter your question or prompt here...",
                            value="Explain the benefits of microservices architecture."
                        ).classes('w-full')
                        
                        test_btn = ui.button("Run Comprehensive Test", 
                                           on_click=lambda: run_comprehensive_test(),
                                           icon="rocket_launch").classes('w-full')
                    
                    with ui.column().classes('col-6'):
                        result_area = ui.markdown().classes('w-full')
                        metrics_area = ui.column().classes('w-full')
            
            async def run_comprehensive_test():
                """Run the comprehensive AI test."""
                test_btn.props('loading')
                result_area.content = "🔄 Running comprehensive test..."
                
                try:
                    response = await api_client.ai_test(
                        system_prompt.value,
                        user_context.value
                    )
                    
                    if is_success_response(response):
                        # Show results
                        result_area.content = f"""
## ✅ Test Successful!

**AI Response:**
{response.get('ai_result', 'No response')}

**File URL:** {response.get('file_url', 'N/A')}
**Response Time:** {format_response_time(response.get('response_time_ms', 0))}
**Created:** {response.get('created_at', 'N/A')}
                        """
                        
                        # Show service statuses
                        metrics_area.clear()
                        with metrics_area:
                            ui.label("Services Tested:").classes('text-h6')
                            containers = response.get('containers_tested', {})
                            for service, status in containers.items():
                                color = 'positive' if status == 'success' else 'negative'
                                ui.chip(f"{service.title()}: {status}", 
                                       color=color).classes('q-mr-xs')
                    
                    else:
                        error_msg = extract_error_message(response)
                        result_area.content = f"## ❌ Test Failed\n\n{error_msg}"
                        
                except Exception as e:
                    result_area.content = f"## ❌ Connection Error\n\n{str(e)}"
                
                finally:
                    test_btn.props('loading=false')
        
        # Google AI Tab
        with ui.tab_panel(google_tab):
            with Navigation.create_card("Google AI (Gemini)", "smart_toy"):
                ui.label("Test Google Gemini 2.5 Flash Image Preview model").classes('text-body2 text-grey-7 q-mb-md')
                
                with ui.row().classes('w-full'):
                    with ui.column().classes('col-6'):
                        ui.button("Test Connection", 
                                 on_click=lambda: test_google_connection(),
                                 icon="link").classes('w-full q-mb-md')
                        
                        google_prompt = ui.textarea(
                            label="Prompt",
                            placeholder="Enter your prompt for Google AI...",
                            value="Write a haiku about artificial intelligence."
                        ).classes('w-full')
                        
                        google_btn = ui.button("Send to Google AI", 
                                             on_click=lambda: test_google_ai(),
                                             icon="send").classes('w-full')
                    
                    with ui.column().classes('col-6'):
                        google_result = ui.markdown().classes('w-full')
            
            async def test_google_connection():
                """Test Google AI connection."""
                try:
                    response = await api_client.google_ai_test()
                    if response.get('status') == 'success':
                        google_result.content = f"""
## ✅ Google AI Connected!

**Model:** {response.get('model', 'Unknown')}
**Test Response:** {response.get('test_response', 'No response')}
                        """
                    else:
                        google_result.content = f"""
## ❌ Connection Failed

{response.get('message', 'Unknown error')}
                        """
                except Exception as e:
                    google_result.content = f"## ❌ Error\n\n{str(e)}"
            
            async def test_google_ai():
                """Send prompt to Google AI."""
                google_btn.props('loading')
                google_result.content = "🔄 Generating response..."
                
                try:
                    response = await api_client.google_ai_prompt(google_prompt.value)
                    
                    if is_success_response(response):
                        google_result.content = f"""
## 🤖 Google AI Response

{response.get('response', 'No response')}

**Service:** {response.get('service_type', 'Unknown')}
**Model:** {response.get('model', 'Unknown')}  
**Response Time:** {format_response_time(response.get('response_time_ms', 0))}
                        """
                    else:
                        error_msg = extract_error_message(response)
                        google_result.content = f"## ❌ Error\n\n{error_msg}"
                        
                except Exception as e:
                    google_result.content = f"## ❌ Connection Error\n\n{str(e)}"
                
                finally:
                    google_btn.props('loading=false')
        
        # Google ADK Tab
        with ui.tab_panel(google_adk_tab):
            with Navigation.create_card("Google ADK Agent", "psychology_alt"):
                ui.label("Test Google Agent Development Kit - Enhanced agent framework with tool support").classes('text-body2 text-grey-7 q-mb-md')
                
                with ui.row().classes('w-full'):
                    with ui.column().classes('col-6'):
                        ui.button("Test ADK Connection", 
                                 on_click=lambda: test_adk_connection(),
                                 icon="link").classes('w-full q-mb-md')
                        
                        adk_prompt = ui.textarea(
                            label="Prompt",
                            placeholder="Enter your prompt for Google ADK Agent...",
                            value="Explain how AI agents differ from traditional chatbots."
                        ).classes('w-full')
                        
                        adk_btn = ui.button("Send to ADK Agent", 
                                          on_click=lambda: test_google_adk(),
                                          icon="smart_toy").classes('w-full')
                    
                    with ui.column().classes('col-6'):
                        adk_result = ui.markdown().classes('w-full')
            
            async def test_adk_connection():
                """Test Google ADK connection."""
                try:
                    response = await api_client.google_adk_test()
                    if response.get('status') == 'success':
                        agent_info = response.get('agent_info', {})
                        adk_result.content = f"""
## ✅ Google ADK Agent Connected!

**Agent Name:** {agent_info.get('name', 'Unknown')}
**Framework:** {agent_info.get('framework', 'Google ADK')}
**Model:** {agent_info.get('model', 'Unknown')}
**Tools Count:** {agent_info.get('tools_count', 0)}
**Test Response:** {response.get('test_response', 'No response')}
                        """
                    else:
                        adk_result.content = f"""
## ❌ Connection Failed

{response.get('message', 'Unknown error')}
                        """
                except Exception as e:
                    adk_result.content = f"## ❌ Error\n\n{str(e)}"
            
            async def test_google_adk():
                """Send prompt to Google ADK Agent."""
                adk_btn.props('loading')
                adk_result.content = "🔄 ADK Agent processing..."
                
                try:
                    response = await api_client.google_adk_prompt(adk_prompt.value)
                    
                    if is_success_response(response):
                        adk_result.content = f"""
## 🤖 Google ADK Agent Response

{response.get('response', 'No response')}

**Service:** {response.get('service_type', 'Unknown')}
**Model:** {response.get('model', 'Unknown')}  
**Response Time:** {format_response_time(response.get('response_time_ms', 0))}

*This response was generated using Google's Agent Development Kit framework*
                        """
                    else:
                        error_msg = extract_error_message(response)
                        adk_result.content = f"## ❌ Error\n\n{error_msg}"
                        
                except Exception as e:
                    adk_result.content = f"## ❌ Connection Error\n\n{str(e)}"
                
                finally:
                    adk_btn.props('loading=false')
        
        # OpenRouter Tab
        with ui.tab_panel(openrouter_tab):
            with Navigation.create_card("OpenRouter Services", "hub"):
                ui.label("Test different OpenRouter implementations").classes('text-body2 text-grey-7 q-mb-md')
                
                with ui.row().classes('w-full'):
                    with ui.column().classes('col-6'):
                        openrouter_prompt = ui.textarea(
                            label="Prompt",
                            placeholder="Enter your prompt for OpenRouter...",
                            value="Explain the difference between microservices and monolithic architecture."
                        ).classes('w-full')
                        
                        with ui.row().classes('w-full'):
                            ui.button("Simple", on_click=lambda: test_openrouter('simple'), 
                                     icon="bolt").classes('col')
                            ui.button("LangChain", on_click=lambda: test_openrouter('langchain'), 
                                     icon="link").classes('col')
                            ui.button("LangGraph", on_click=lambda: test_openrouter('langgraph'), 
                                     icon="account_tree").classes('col')
                    
                    with ui.column().classes('col-6'):
                        openrouter_result = ui.markdown().classes('w-full')
            
            async def test_openrouter(service_type: str):
                """Test OpenRouter service."""
                openrouter_result.content = f"🔄 Testing OpenRouter {service_type.title()}..."
                
                try:
                    if service_type == 'simple':
                        response = await api_client.openrouter_simple(openrouter_prompt.value)
                    elif service_type == 'langchain':
                        response = await api_client.openrouter_langchain(openrouter_prompt.value)
                    elif service_type == 'langgraph':
                        response = await api_client.openrouter_langgraph(openrouter_prompt.value)
                    
                    if is_success_response(response):
                        openrouter_result.content = f"""
## 🚀 OpenRouter {service_type.title()} Response

{response.get('response', 'No response')}

**Service:** {response.get('service_type', 'Unknown')}
**Model:** {response.get('model', 'Unknown')}
**Response Time:** {format_response_time(response.get('response_time_ms', 0))}
                        """
                    else:
                        error_msg = extract_error_message(response)
                        openrouter_result.content = f"## ❌ Error\n\n{error_msg}"
                        
                except Exception as e:
                    openrouter_result.content = f"## ❌ Connection Error\n\n{str(e)}"