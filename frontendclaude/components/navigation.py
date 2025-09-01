# Navigation Component
"""
Reusable navigation menu for all pages.
"""

from nicegui import ui
from typing import Callable, Optional


class Navigation:
    """Navigation menu component."""
    
    def __init__(self, current_page: str = "dashboard"):
        self.current_page = current_page
        self.create_navigation()
    
    def create_navigation(self):
        """Create the navigation header."""
        with ui.header().classes('items-center justify-between'):
            with ui.row().classes('items-center'):
                ui.label('V2 POC - Frontend Claude').classes('text-h6 font-weight-bold')
                
            with ui.row().classes('q-gutter-md'):
                self.nav_button('Dashboard', '/claude/', 'dashboard', 'dashboard')
                self.nav_button('AI Test', '/claude/ai-test', 'smart_toy', 'ai-test')  
                self.nav_button('Health', '/claude/health', 'health_and_safety', 'health')
                self.nav_button('API Explorer', '/claude/api-explorer', 'code', 'api-explorer')
    
    def nav_button(self, label: str, url: str, icon: str, page_id: str):
        """Create a navigation button."""
        is_current = self.current_page == page_id
        
        button = ui.button(label, icon=icon).classes('q-mr-sm')
        if is_current:
            button.classes('bg-primary text-white')
        
        button.on('click', lambda: ui.navigate.to(url))
    
    @staticmethod
    def create_page_header(title: str, subtitle: str = ""):
        """Create a consistent page header."""
        with ui.row().classes('w-full items-center q-pa-md'):
            ui.label(title).classes('text-h4 font-weight-bold')
            if subtitle:
                ui.separator().classes('q-mx-md')
                ui.label(subtitle).classes('text-subtitle1 text-grey-7')
    
    @staticmethod 
    def create_card(title: str, icon: str = "", classes: str = ""):
        """Create a consistent card layout."""
        card_classes = f'q-pa-md q-ma-sm {classes}'
        card = ui.card().classes(card_classes)
        
        with card:
            if title or icon:
                with ui.card_section().classes('pb-xs'):
                    with ui.row().classes('items-center'):
                        if icon:
                            ui.icon(icon).classes('q-mr-sm text-h5')
                        if title:
                            ui.label(title).classes('text-h6 font-weight-bold')
        
        return card