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
    if 'error' in response:
        return response['error']
    elif 'detail' in response:
        return response['detail'] 
    elif 'message' in response:
        return response['message']
    else:
        return "Unknown error occurred"


def is_success_response(response: Dict[str, Any]) -> bool:
    """Check if API response indicates success."""
    if 'error' in response:
        return False
    if 'status' in response:
        return response['status'] in ['success', 'healthy']
    # If no error and has expected response fields, consider it success
    return 'ai_result' in response or 'response' in response or 'containers' in response