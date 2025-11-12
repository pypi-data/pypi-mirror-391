"""Utility functions for cross-platform support"""

import sys

def safe_print(*args, **kwargs):
    """Safe print that handles Unicode on all platforms"""
    emoji_map = {
        '✅': '[OK]',
        '❌': '[FAIL]',
        '⚠️': '[WARN]',
        '🔍': '[SEARCH]',
        '📚': '[DOCS]',
        '📝': '[WRITE]',
        '💾': '[SAVE]',
        '🚀': '[START]',
        '📊': '[STATS]',
        '🔬': '[RESEARCH]',
        '🎯': '[TARGET]',
        '💡': '[INFO]',
        '🔧': '[CONFIG]',
    }
    
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        safe_args = []
        for arg in args:
            if isinstance(arg, str):
                safe_arg = arg
                for emoji, ascii_text in emoji_map.items():
                    safe_arg = safe_arg.replace(emoji, ascii_text)
                safe_args.append(safe_arg)
            else:
                safe_args.append(arg)
        print(*safe_args, **kwargs)
