"""
Configuration module for Remnawave Telegram Bot
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

def _parse_inbound_ids(env_value):
    """Parse inbound IDs as strings (UUIDs or numeric IDs converted to strings)"""
    if not env_value:
        return ["1"]  # Default as string
    
    ids = []
    for x in env_value.split(','):
        x = x.strip()
        if not x:
            continue
        
        # Always store as string (API expects List[str])
        # Both numeric IDs and UUIDs will be strings
        if len(x) > 0:  # Basic validation - not empty
            ids.append(x)
                
    return ids if ids else ["1"]  # Fallback as string

def _parse_admin_ids(env_value):
    """Parse admin user IDs from environment variable"""
    if not env_value:
        return []
    
    ids = []
    for x in env_value.split(','):
        x = x.strip()
        if not x:
            continue
        try:
            user_id = int(x)
            ids.append(user_id)
        except ValueError:
            print(f"Warning: Invalid admin user ID '{x}', skipping...")
            continue
                
    return ids

class Config:
    """Configuration class for the bot"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Remnawave Panel Configuration
    REMNAWAVE_BASE_URL = os.getenv('REMNAWAVE_BASE_URL')
    REMNAWAVE_TOKEN = os.getenv('REMNAWAVE_TOKEN')
    REMNAWAVE_CADDY_TOKEN = os.getenv('REMNAWAVE_CADDY_TOKEN')
    
    # User Creation Settings
    DEFAULT_INBOUND_IDS = _parse_inbound_ids(os.getenv('DEFAULT_INBOUND_IDS', '1'))
    DEFAULT_PROTOCOL = os.getenv('DEFAULT_PROTOCOL', 'vless')
    DEFAULT_UUID_PREFIX = os.getenv('DEFAULT_UUID_PREFIX', 'promo-')
    SUBSCRIPTION_FILE_BASE_URL = os.getenv('SUBSCRIPTION_FILE_BASE_URL', 'https://example.com/files/')
    
    # Limits and Settings
    MAX_SUBSCRIPTIONS_PER_REQUEST = int(os.getenv('MAX_SUBSCRIPTIONS_PER_REQUEST', '100'))
    
    # Security - Admin access control
    ADMIN_USER_IDS = _parse_admin_ids(os.getenv('ADMIN_USER_IDS', ''))
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration parameters"""
        required_fields = [
            'TELEGRAM_BOT_TOKEN',
            'REMNAWAVE_BASE_URL', 
            'REMNAWAVE_TOKEN'
        ]
        
        for field in required_fields:
            if not getattr(cls, field):
                raise ValueError(f"Required configuration field {field} is not set")
        
        if not cls.ADMIN_USER_IDS:
            raise ValueError("At least one admin user ID must be configured")
            
        return True