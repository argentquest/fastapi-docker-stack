# Helper Functions
"""
Utility functions for the NiceGUI frontend.
"""

from datetime import datetime
from typing import Dict, Any


def format_timestamp(timestamp: str) -> str:
    """Format ISO timestamp for display."""
    try:
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp


def format_response_time(ms: int) -> str:
    """Format response time in milliseconds."""
    if ms < 1000:
        return f"{ms}ms"
    else:
        return f"{ms/1000:.2f}s"


def get_status_color(status: str) -> str:
    """Get color class for status."""
    status_colors = {
        'healthy': 'positive',
        'success': 'positive', 
        'degraded': 'warning',
        'error': 'negative',
        'unavailable': 'negative'
    }
    return status_colors.get(status.lower(), 'grey')


def get_status_icon(status: str) -> str:
    """Get icon for status."""
    status_icons = {
        'healthy': 'check_circle',
        'success': 'check_circle',
        'degraded': 'warning', 
        'error': 'error',
        'unavailable': 'cancel'
    }
    return status_icons.get(status.lower(), 'help')


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def format_json(data: Dict[str, Any]) -> str:
    """Format JSON data for display."""
    try:
        import json
        return json.dumps(data, indent=2)
    except:
        return str(data)


def extract_error_message(response: Dict[str, Any]) -> str:
    """Extract user-friendly error message from API response."""
    # Handle HTTP error responses
    if isinstance(response, dict):
        # Check for standard error fields
        if 'error' in response:
            error = response['error']
            # Handle nested error structures
            if isinstance(error, dict):
                if 'message' in error:
                    return error['message']
                elif 'detail' in error:
                    return error['detail']
                else:
                    return str(error)
            return str(error)
        elif 'detail' in response:
            detail = response['detail']
            # Handle FastAPI HTTPException details
            if isinstance(detail, list) and len(detail) > 0:
                return " | ".join([d.get('msg', str(d)) for d in detail])
            return str(detail)
        elif 'message' in response:
            return response['message']
        elif 'msg' in response:
            return response['msg']
        
        # Try to extract from nested structures
        if 'data' in response and isinstance(response['data'], dict):
            if 'error' in response['data']:
                return response['data']['error']
        
        # If response has status code
        if 'status_code' in response:
            return f"HTTP {response['status_code']}: {response.get('reason', 'Request failed')}"
    
    # Handle string responses
    elif isinstance(response, str):
        return response
    
    # Default fallback
    return "Unknown error occurred. Check server logs for details."


def format_error_details(response: Dict[str, Any], include_debug: bool = True) -> str:
    """Format detailed error information for display."""
    error_msg = extract_error_message(response)
    
    # Build detailed error display
    details = []
    details.append(f"**Error:** {error_msg}")
    
    if include_debug and isinstance(response, dict):
        # Add status code if available
        if 'status_code' in response:
            details.append(f"**Status Code:** {response['status_code']}")
        
        # Add timestamp if available
        if 'timestamp' in response:
            details.append(f"**Timestamp:** {format_timestamp(response['timestamp'])}")
        
        # Add request ID if available
        if 'request_id' in response:
            details.append(f"**Request ID:** {response['request_id']}")
        
        # Add service information if available
        if 'service' in response:
            details.append(f"**Service:** {response['service']}")
        
        # Add traceback if available (truncated)
        if 'traceback' in response:
            tb = response['traceback']
            if isinstance(tb, str):
                # Show only last few lines of traceback
                tb_lines = tb.split('\n')
                if len(tb_lines) > 5:
                    tb = '\n'.join(tb_lines[-5:])
                details.append(f"**Debug Info:**\n```\n{tb}\n```")
    
    return '\n\n'.join(details)


def is_success_response(response: Dict[str, Any]) -> bool:
    """Check if API response indicates success."""
    if 'error' in response:
        return False
    if 'status' in response:
        return response['status'] in ['success', 'healthy']
    # If no error and has expected response fields, consider it success
    return 'ai_result' in response or 'response' in response or 'containers' in response