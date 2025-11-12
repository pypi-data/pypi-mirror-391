import os
import json
from typing import Dict, Any, Optional

HOME = os.path.expanduser('~')
CONFIG_DIR = os.path.join(HOME, '.omga_cli')
os.makedirs(CONFIG_DIR, exist_ok=True)

HISTORY_FILE = os.path.join(CONFIG_DIR, 'history.txt')
CACHE_DB = os.path.join(CONFIG_DIR, 'cache.sqlite')
LOG_FILE = os.path.join(CONFIG_DIR, 'log.txt')
CONFIG_FILE = os.path.join(CONFIG_DIR, 'config.json')

# Default configuration
DEFAULT_CONFIG = {
    "api": {
        "provider": "metis",
        "model": "kwaipilot/kat-coder-pro:free",
        "timeout": 30,
        "max_tokens": 2048,
        "temperature": 0.7
    },
    "ui": {
        "theme": "monokai",
        "show_line_numbers": True,
        "word_wrap": True,
        "show_icons": True,
        "show_progress": True
    },
    "features": {
        "auto_fix": True,
        "smart_completion": True,
        "cache_responses": True,
        "show_diffs": True
    },
    "security": {
        "confirm_destructive": True,
        "safe_mode": True
    }
}

def load_config() -> Dict[str, Any]:
    """Load configuration from file or create default"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults for any missing keys
                merged_config = _merge_config(DEFAULT_CONFIG, config)
                
                # Migration: Update old model names to new OpenRouter model
                old_models = ['gemini-2.0-flash', 'gemini-pro', 'gemini-1.5-pro', 'gemini-1.5-flash']
                if merged_config.get('api', {}).get('model') in old_models:
                    merged_config['api']['model'] = DEFAULT_CONFIG['api']['model']
                    save_config(merged_config)
                    # Lazy import to avoid circular dependency
                    try:
                        from core.logger import logger
                        logger.info(f"Migrated model to {DEFAULT_CONFIG['api']['model']}")
                    except:
                        pass  # Logger not available yet, that's okay
                
                return merged_config
        except (json.JSONDecodeError, IOError) as e:
            print(f"Warning: Error loading config: {e}. Using defaults.")
            return DEFAULT_CONFIG.copy()
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file"""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError as e:
        print(f"Error saving config: {e}")
        return False

def _merge_config(default: Dict[str, Any], user: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively merge user config with defaults"""
    result = default.copy()
    for key, value in user.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _merge_config(result[key], value)
        else:
            result[key] = value
    return result

def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get configuration value using dot notation (e.g., 'api.model')"""
    config = load_config()
    keys = key_path.split('.')
    value = config
    
    try:
        for key in keys:
            value = value[key]
        return value
    except (KeyError, TypeError):
        return default

def set_config_value(key_path: str, value: Any) -> bool:
    """Set configuration value using dot notation"""
    config = load_config()
    keys = key_path.split('.')
    
    # Navigate to the parent of the target key
    current = config
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    
    # Set the value
    current[keys[-1]] = value
    
    return save_config(config)

# API key is now built-in, no configuration needed

# Load configuration on import
CONFIG = load_config()