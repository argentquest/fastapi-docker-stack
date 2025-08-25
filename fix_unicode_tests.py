#!/usr/bin/env python
"""
Script to fix Unicode encoding issues in test scripts for Windows compatibility.
Replaces Unicode emojis and symbols with ASCII equivalents.
"""

import os
import re
from pathlib import Path


def fix_unicode_in_file(file_path: Path):
    """Fix Unicode characters in a single file."""
    print(f"Fixing Unicode in {file_path}...")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        print(f"  Skipping {file_path} - unable to read with UTF-8")
        return
    
    original_content = content
    
    # Dictionary of Unicode characters to ASCII replacements
    unicode_replacements = {
        # Emojis
        '🚀': '[ROCKET]',
        '✅': '[OK]',
        '❌': '❌',
        '⚠️': '[WARN]',
        '📊': '[CHART]',
        '🎯': '[TARGET]',
        '🔍': '[SEARCH]',
        '💾': '[SAVE]',
        '🔄': '[REFRESH]',
        '⏱️': '[TIMER]',
        '📈': '[GRAPH]',
        '🧪': '[TEST]',
        '🏥': '[HEALTH]',
        '🗄️': '[DB]',
        '📦': '[PACKAGE]',
        '🔐': '[SECURE]',
        '🌐': '[WEB]',
        '⭐': '[STAR]',
        '🎉': '[CELEBRATE]',
        '🔧': '[TOOL]',
        '📝': '[NOTE]',
        '💡': '[IDEA]',
        '⚡': '[FAST]',
        '🚨': '[ALERT]',
        '📄': '[DOC]',
        '🔗': '[LINK]',
        '🎭': '[MASK]',
        '🏗️': '[BUILD]',
        '📚': '[BOOKS]',
        '🎪': '[TENT]',
        '🎨': '[ART]',
        '🔮': '[CRYSTAL]',
        '🎲': '[DICE]',
        '🏆': '[TROPHY]',
        '🎖️': '[MEDAL]',
        '🥇': '[GOLD]',
        '🥈': '[SILVER]',
        '🥉': '[BRONZE]',
        '🎊': '[CONFETTI]',
        '🎈': '[BALLOON]',
        '🎀': '[BOW]',
        '🔔': '[BELL]',
        '🔕': '[MUTE]',
        '🔊': '[SOUND]',
        '🔉': '[VOLUME]',
        '🔈': '[SPEAKER]',
        '📢': '[MEGAPHONE]',
        '📣': '[HORN]',
        '📯': '[TRUMPET]',
        '🎺': '[INSTRUMENT]',
        '🎵': '[MUSIC]',
        '🎶': '[NOTES]',
        '🎤': '[MIC]',
        '🎧': '[HEADPHONES]',
        '📻': '[RADIO]',
        '📺': '[TV]',
        '📷': '[CAMERA]',
        '📹': '[VIDEO]',
        '📼': '[TAPE]',
        '💿': '[CD]',
        '📀': '[DVD]',
        '💽': '[DISK]',
        '💾': '[FLOPPY]',
        '💻': '[LAPTOP]',
        '🖥️': '[DESKTOP]',
        '🖨️': '[PRINTER]',
        '⌨️': '[KEYBOARD]',
        '🖱️': '[MOUSE]',
        '🖲️': '[TRACKBALL]',
        '🕹️': '[JOYSTICK]',
        '🗜️': '[CLAMP]',
        '💡': '[BULB]',
        '🔦': '[FLASHLIGHT]',
        '🏮': '[LANTERN]',
        '📙': '[BOOK]',
        '📘': '[BLUE_BOOK]',
        '📗': '[GREEN_BOOK]',
        '📕': '[RED_BOOK]',
        '📓': '[NOTEBOOK]',
        '📔': '[JOURNAL]',
        '📒': '[LEDGER]',
        '📃': '[PAGE]',
        '📜': '[SCROLL]',
        '📄': '[DOCUMENT]',
        '📰': '[NEWSPAPER]',
        '🗞️': '[NEWS]',
        '📑': '[BOOKMARK]',
        '🔖': '[TAG]',
        '🏷️': '[LABEL]',
        '💰': '[MONEY]',
        '💴': '[YEN]',
        '💵': '[DOLLAR]',
        '💶': '[EURO]',
        '💷': '[POUND]',
        '💸': '[FLYING_MONEY]',
        '💳': '[CARD]',
        '💎': '[DIAMOND]',
        '⚖️': '[SCALE]',
        '🔧': '[WRENCH]',
        '🔨': '[HAMMER]',
        '⛏️': '[PICK]',
        '🛠️': '[TOOLS]',
        '⚙️': '[GEAR]',
        '🔩': '[BOLT]',
        '⚗️': '[FLASK]',
        '🧲': '[MAGNET]',
        '🧪': '[TEST_TUBE]',
        '🧫': '[PETRI]',
        '🧬': '[DNA]',
        '🔬': '[MICROSCOPE]',
        '🔭': '[TELESCOPE]',
        '📡': '[SATELLITE]',
        '💉': '[SYRINGE]',
        '💊': '[PILL]',
        '🩸': '[BLOOD]',
        '🧻': '[TISSUE]',
        '🚽': '[TOILET]',
        '🚿': '[SHOWER]',
        '🛁': '[BATH]',
        '🛀': '[BATHING]',
        '🧴': '[BOTTLE]',
        '🧵': '[THREAD]',
        '🪡': '[NEEDLE]',
        '🧶': '[YARN]',
        '🪢': '[KNOT]',
        
        # Check marks and X marks
        '✓': '[CHECK]',
        '✔️': '[CHECK]',
        '✗': '[X]',
        '✘': '[X]',
        '❌': '[X]',
        '⭕': '[O]',
        
        # Arrows
        '→': '->',
        '←': '<-',
        '↑': '^',
        '↓': 'v',
        '↗': '/',
        '↙': '\\',
        '↘': '/',
        '↖': '\\',
        '⇒': '=>',
        '⇐': '<=',
        '⇑': '^^',
        '⇓': 'vv',
        
        # Mathematical symbols
        '×': 'x',
        '÷': '/',
        '±': '+/-',
        '≠': '!=',
        '≤': '<=',
        '≥': '>=',
        '≈': '~=',
        '∞': 'inf',
        
        # Punctuation
        '"': '"',
        '"': '"',
        ''': "'",
        ''': "'",
        '—': '--',
        '–': '-',
        '…': '...',
        
        # Other symbols
        '°': 'deg',
        '™': '(TM)',
        '®': '(R)',
        '©': '(C)',
        '§': 'section',
        '¶': 'para',
        '†': '+',
        '‡': '++',
        '•': '*',
        '◦': 'o',
        '‣': '>',
        '⁃': '-',
    }
    
    # Apply replacements
    for unicode_char, ascii_replacement in unicode_replacements.items():
        content = content.replace(unicode_char, ascii_replacement)
    
    # Fix any remaining high Unicode characters with a generic replacement
    content = re.sub(r'[^\x00-\x7F]+', '[UNICODE]', content)
    
    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"  Fixed Unicode characters in {file_path}")
    else:
        print(f"  No Unicode fixes needed for {file_path}")


def fix_all_test_files():
    """Fix Unicode issues in all Python test files."""
    # Find all Python files in tests directory and root
    python_files = []
    
    # Tests directory
    tests_dir = Path("tests")
    if tests_dir.exists():
        python_files.extend(list(tests_dir.glob("*.py")))
    
    # Root directory test files
    root_files = [
        "run_all_tests.py",
    ]
    
    for file_name in root_files:
        file_path = Path(file_name)
        if file_path.exists():
            python_files.append(file_path)
    
    print(f"Found {len(python_files)} Python test files to fix:")
    
    for file_path in python_files:
        fix_unicode_in_file(file_path)
    
    print(f"\nUnicode fixes complete for {len(python_files)} files!")


if __name__ == "__main__":
    fix_all_test_files()