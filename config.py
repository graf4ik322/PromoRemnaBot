"""
Configuration module for Remnawave Telegram Bot
"""

import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuration class for the bot"""
    
    # Telegram Bot Configuration
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Remnawave Panel Configuration
    REMNAWAVE_BASE_URL = os.getenv('REMNAWAVE_BASE_URL')
    REMNAWAVE_TOKEN = os.getenv('REMNAWAVE_TOKEN')
    REMNAWAVE_CADDY_TOKEN = os.getenv('REMNAWAVE_CADDY_TOKEN')
    
    # User Creation Settings
    DEFAULT_INBOUND_IDS = [int(x.strip()) for x in os.getenv('DEFAULT_INBOUND_IDS', '1').split(',')]
    DEFAULT_PROTOCOL = os.getenv('DEFAULT_PROTOCOL', 'vless')
    DEFAULT_UUID_PREFIX = os.getenv('DEFAULT_UUID_PREFIX', 'promo-')
    SUBSCRIPTION_FILE_BASE_URL = os.getenv('SUBSCRIPTION_FILE_BASE_URL', 'https://example.com/files/')
    
    # Limits and Settings
    MAX_SUBSCRIPTIONS_PER_REQUEST = int(os.getenv('MAX_SUBSCRIPTIONS_PER_REQUEST', '100'))
    ADMIN_USER_IDS = [int(x.strip()) for x in os.getenv('ADMIN_USER_IDS', '').split(',') if x.strip()]
    
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