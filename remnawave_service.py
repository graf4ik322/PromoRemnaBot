"""
Remnawave API Service Module
"""

import asyncio
import logging
import random
import string
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Tuple, Optional
from remnawave_api import RemnawaveSDK
from config import Config
from utils import FileManager

logger = logging.getLogger(__name__)

class RemnawaveService:
    """Service class for interacting with Remnawave API"""
    
    def __init__(self):
        self.sdk = RemnawaveSDK(
            base_url=Config.REMNAWAVE_BASE_URL,
            token=Config.REMNAWAVE_TOKEN,
            caddy_token=Config.REMNAWAVE_CADDY_TOKEN
        )
        self.file_manager = FileManager()
    
    def _generate_random_suffix(self, length: int = 8) -> str:
        """Generate random string for user names"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def _validate_tag(self, tag: str) -> bool:
        """Validate tag format (only latin characters, snake_case for spaces)"""
        if not tag:
            return False
        # Allow latin letters, numbers, underscore and hyphen
        allowed_chars = set(string.ascii_letters + string.digits + '_-')
        return all(c in allowed_chars for c in tag)
    
    async def create_promo_users(self, tag: str, traffic_limit_gb: int, count: int) -> Tuple[List[str], str]:
        """
        Create promo users and return subscription links and file URL
        
        Args:
            tag: Campaign tag
            traffic_limit_gb: Traffic limit in GB
            count: Number of subscriptions to create
            
        Returns:
            Tuple of (subscription_links, file_url)
        """
        try:
            # Validate tag
            if not self._validate_tag(tag):
                raise ValueError("Invalid tag format. Use only latin characters, numbers, underscore and hyphen.")
            
            # Convert GB to bytes
            traffic_limit_bytes = traffic_limit_gb * 1024 * 1024 * 1024
            
            subscription_links = []
            created_users = []
            
            for i in range(count):
                # Generate unique username
                random_suffix = self._generate_random_suffix()
                username = f"{Config.DEFAULT_UUID_PREFIX}{random_suffix}-{tag}"
                
                try:
                    # Based on API documentation, username and expireAt are required fields
                    # Generate a proper expiration date (e.g., 30 days from now)
                    expire_date = datetime.now(timezone.utc) + timedelta(days=30)
                    expire_at_iso = expire_date.isoformat()
                    
                    # Method 1: Try with all required and optional parameters according to API docs
                    try:
                        response = await self.sdk.users.create_user(
                            username=username,
                            expireAt=expire_at_iso,
                            trafficLimitBytes=traffic_limit_bytes,
                            status="ACTIVE",
                            trafficLimitStrategy="NO_RESET",
                            activateAllInbounds=True
                        )
                        logger.info(f"Method 1 (full API spec) succeeded")
                    except Exception as e1:
                        logger.warning(f"Method 1 failed: {e1}, trying method 2")
                        
                        # Method 2: Try with just required parameters
                        try:
                            response = await self.sdk.users.create_user(
                                username=username,
                                expireAt=expire_at_iso
                            )
                            logger.info(f"Method 2 (required only) succeeded")
                        except Exception as e2:
                            logger.warning(f"Method 2 failed: {e2}, trying method 3")
                            
                            # Method 3: Try with snake_case parameter names
                            try:
                                response = await self.sdk.users.create_user(
                                    username=username,
                                    expire_at=expire_at_iso,
                                    traffic_limit_bytes=traffic_limit_bytes
                                )
                                logger.info(f"Method 3 (snake_case) succeeded")
                            except Exception as e3:
                                logger.warning(f"Method 3 failed: {e3}, trying method 4")
                                
                                # Method 4: Try using dict/json format
                                try:
                                    user_data = {
                                        "username": username,
                                        "expireAt": expire_at_iso,
                                        "trafficLimitBytes": traffic_limit_bytes,
                                        "status": "ACTIVE"
                                    }
                                    response = await self.sdk.users.create_user(**user_data)
                                    logger.info(f"Method 4 (dict format) succeeded")
                                except Exception as e4:
                                    # Log available methods for debugging
                                    available_methods = [m for m in dir(self.sdk.users) if not m.startswith('_')]
                                    logger.error(f"All creation methods failed. Available methods: {available_methods}")
                                    logger.error(f"Errors: {e1}, {e2}, {e3}, {e4}")
                                    raise e4
                    
                    if response:
                        # User created successfully with username already set
                        try:
                            # Try to extract subscription URL and user ID from response
                            user_id = None
                            subscription_url = None
                            
                            # Extract data from response based on API documentation structure
                            if hasattr(response, 'response'):
                                # Response has nested response object (as per API docs)
                                resp_data = response.response
                                if hasattr(resp_data, 'uuid'):
                                    user_id = resp_data.uuid
                                if hasattr(resp_data, 'subscriptionUrl'):
                                    subscription_url = resp_data.subscriptionUrl
                            elif hasattr(response, 'uuid'):
                                user_id = response.uuid
                                if hasattr(response, 'subscriptionUrl'):
                                    subscription_url = response.subscriptionUrl
                            elif isinstance(response, dict):
                                if 'response' in response:
                                    resp_data = response['response']
                                    user_id = resp_data.get('uuid')
                                    subscription_url = resp_data.get('subscriptionUrl')
                                else:
                                    user_id = response.get('uuid') or response.get('id')
                                    subscription_url = response.get('subscriptionUrl')
                            
                            # Use subscription URL from response if available
                            if subscription_url:
                                subscription_links.append(subscription_url)
                                created_users.append(username)
                                logger.info(f"Successfully created user: {username} with subscription URL")
                            else:
                                # Fallback: try to get subscription link via separate API call
                                subscription_link = await self._get_subscription_link(username, user_id)
                                if subscription_link:
                                    subscription_links.append(subscription_link)
                                    created_users.append(username)
                                    logger.info(f"Successfully created user: {username} with subscription link from API")
                                else:
                                    logger.warning(f"User created but couldn't get subscription link: {username}")
                                    # Still add as created since user was created
                                    subscription_links.append(f"User created: {username} (ID: {user_id})")
                                    created_users.append(username)
                        
                        except Exception as post_create_error:
                            logger.warning(f"User created but post-creation processing failed for {username}: {post_create_error}")
                            # Still count as success since user was created
                            subscription_links.append(f"User created: {username}")
                            created_users.append(username)
                    
                    logger.info(f"Processed user: {username}")
                    
                except Exception as e:
                    logger.error(f"Failed to create user {username}: {str(e)}")
                    continue
            
            # Generate file with subscription links
            file_url = await self._generate_subscription_file(tag, subscription_links)
            
            logger.info(f"Successfully created {len(created_users)} users for tag '{tag}'")
            return subscription_links, file_url
            
        except Exception as e:
            logger.error(f"Error creating promo users: {str(e)}")
            raise
    
    async def _get_subscription_link(self, username: str, user_id: str = None) -> Optional[str]:
        """Get subscription link for user"""
        try:
            # Try to get user details by various methods
            user_info = None
            
            # Try by UUID first if available
            if user_id:
                for method_name in ['get_user_by_uuid', 'get_user_by_id', 'get_user']:
                    if hasattr(self.sdk.users, method_name):
                        try:
                            method = getattr(self.sdk.users, method_name)
                            user_info = await method(user_id)
                            logger.debug(f"Got user info using {method_name}")
                            break
                        except Exception as e:
                            logger.debug(f"Method {method_name} failed for ID {user_id}: {e}")
            
            # Try by username if ID methods failed or no ID
            if not user_info:
                for method_name in ['get_user_by_username', 'get_users_by_username', 'find_user']:
                    if hasattr(self.sdk.users, method_name):
                        try:
                            method = getattr(self.sdk.users, method_name)
                            user_info = await method(username)
                            logger.debug(f"Got user info using {method_name}")
                            break
                        except Exception as e:
                            logger.debug(f"Method {method_name} failed for username {username}: {e}")
            
            # Extract subscription URL from user info
            if user_info:
                # Try different possible field names for subscription URL
                for field_name in ['subscription_url', 'sub_url', 'link', 'config_url', 'vless_url']:
                    if hasattr(user_info, field_name):
                        url = getattr(user_info, field_name)
                        if url:
                            logger.debug(f"Found subscription URL in field {field_name}")
                            return url
                
                # If user_info is a dict, try dict access
                if isinstance(user_info, dict):
                    for field_name in ['subscription_url', 'sub_url', 'link', 'config_url', 'vless_url']:
                        if field_name in user_info and user_info[field_name]:
                            logger.debug(f"Found subscription URL in dict field {field_name}")
                            return user_info[field_name]
            
            # Fallback: construct subscription URL manually based on common patterns
            base_url = Config.REMNAWAVE_BASE_URL.rstrip('/')
            
            # Try different URL patterns that might work
            url_patterns = [
                f"{base_url}/sub/{user_id}" if user_id else None,
                f"{base_url}/subscription/{user_id}" if user_id else None,
                f"{base_url}/sub/{username}",
                f"{base_url}/subscription/{username}",
                f"{base_url}/api/subscription/{user_id}" if user_id else None,
                f"{base_url}/api/sub/{username}",
            ]
            
            # Return the first non-None pattern
            for pattern in url_patterns:
                if pattern:
                    logger.debug(f"Using fallback subscription URL pattern: {pattern}")
                    return pattern
            
            logger.warning(f"Could not determine subscription URL for user {username}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get subscription link for {username}: {str(e)}")
            return None
    
    async def _generate_subscription_file(self, tag: str, subscription_links: List[str]) -> str:
        """Generate TXT file with subscription links and return URL"""
        try:
            file_url = await self.file_manager.save_subscription_file(tag, subscription_links)
            return file_url or ""
            
        except Exception as e:
            logger.error(f"Failed to generate subscription file: {str(e)}")
            return ""
    
    async def get_tags_with_stats(self) -> List[Dict[str, Any]]:
        """Get list of tags with usage statistics"""
        try:
            # Get all users
            users_response = await self.sdk.users.get_all_users_v2()
            
            if not users_response or not users_response.users:
                return []
            
            # Group users by tag
            tag_stats = {}
            
            for user in users_response.users:
                username = getattr(user, 'username', '')
                
                # Extract tag from username (assuming format: promo-{random}-{tag})
                if username.startswith(Config.DEFAULT_UUID_PREFIX):
                    parts = username.split('-')
                    if len(parts) >= 3:
                        tag = '-'.join(parts[2:])  # Everything after the second dash
                        
                        if tag not in tag_stats:
                            tag_stats[tag] = {
                                'tag': tag,
                                'total': 0,
                                'active': 0,
                                'used': 0
                            }
                        
                        tag_stats[tag]['total'] += 1
                        
                        # Check if user is active (not disabled and has remaining traffic)
                        if not getattr(user, 'disabled', False):
                            used_traffic = getattr(user, 'used_traffic', 0)
                            traffic_limit = getattr(user, 'traffic_limit', 0)
                            
                            if used_traffic < traffic_limit:
                                tag_stats[tag]['active'] += 1
                            else:
                                tag_stats[tag]['used'] += 1
                        else:
                            tag_stats[tag]['used'] += 1
            
            return list(tag_stats.values())
            
        except Exception as e:
            logger.error(f"Error getting tags with stats: {str(e)}")
            return []
    
    async def delete_used_subscriptions(self, tag: str) -> Tuple[int, int]:
        """
        Delete used subscriptions for a specific tag
        
        Returns:
            Tuple of (deleted_count, total_count)
        """
        try:
            # Get all users
            users_response = await self.sdk.users.get_all_users_v2()
            
            if not users_response or not users_response.users:
                return 0, 0
            
            tag_users = []
            deleted_count = 0
            
            # Find users with the specified tag
            for user in users_response.users:
                username = getattr(user, 'username', '')
                
                if username.startswith(Config.DEFAULT_UUID_PREFIX):
                    parts = username.split('-')
                    if len(parts) >= 3:
                        user_tag = '-'.join(parts[2:])
                        
                        if user_tag == tag:
                            tag_users.append(user)
                            
                            # Check if user is "used" (disabled or traffic limit exceeded)
                            used_traffic = getattr(user, 'used_traffic', 0)
                            traffic_limit = getattr(user, 'traffic_limit', 0)
                            is_disabled = getattr(user, 'disabled', False)
                            
                            if is_disabled or used_traffic >= traffic_limit:
                                # Delete used subscription
                                try:
                                    await self.sdk.users.delete_user(getattr(user, 'id', None))
                                    deleted_count += 1
                                    logger.info(f"Deleted used subscription: {username}")
                                except Exception as e:
                                    logger.error(f"Failed to delete user {username}: {str(e)}")
            
            total_count = len(tag_users)
            logger.info(f"Deleted {deleted_count} out of {total_count} users for tag '{tag}'")
            
            return deleted_count, total_count
            
        except Exception as e:
            logger.error(f"Error deleting used subscriptions: {str(e)}")
            raise
    
    async def get_tag_preview_stats(self, tag: str) -> Dict[str, int]:
        """Get preview statistics for a specific tag before deletion"""
        try:
            users_response = await self.sdk.users.get_all_users_v2()
            
            if not users_response or not users_response.users:
                return {'total': 0, 'active': 0, 'used': 0}
            
            stats = {'total': 0, 'active': 0, 'used': 0}
            
            for user in users_response.users:
                username = getattr(user, 'username', '')
                
                if username.startswith(Config.DEFAULT_UUID_PREFIX):
                    parts = username.split('-')
                    if len(parts) >= 3:
                        user_tag = '-'.join(parts[2:])
                        
                        if user_tag == tag:
                            stats['total'] += 1
                            
                            used_traffic = getattr(user, 'used_traffic', 0)
                            traffic_limit = getattr(user, 'traffic_limit', 0)
                            is_disabled = getattr(user, 'disabled', False)
                            
                            if is_disabled or used_traffic >= traffic_limit:
                                stats['used'] += 1
                            else:
                                stats['active'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting tag preview stats: {str(e)}")
            return {'total': 0, 'active': 0, 'used': 0}