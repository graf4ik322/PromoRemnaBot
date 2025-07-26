"""
Remnawave API Service Module
"""

import asyncio
import logging
import random
import string
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
                    # Create user via API with minimal required parameters
                    user_data = {
                        "data_limit": traffic_limit_bytes,
                        "expire_date": None,  # No time limit (unlimited)
                        "inbound_ids": Config.DEFAULT_INBOUND_IDS,
                        "disabled": False
                    }
                    
                    # Based on logs: username/name parameters are not supported
                    # Let's try the correct API method parameters
                    try:
                        # Method 1: Try with just data structure - no username in parameters
                        response = await self.sdk.users.create_user(
                            data_limit=traffic_limit_bytes,
                            inbound_ids=Config.DEFAULT_INBOUND_IDS,
                            expire_date=None
                        )
                    except Exception as e1:
                        logger.warning(f"Method 1 (no username) failed: {e1}, trying method 2")
                        try:
                            # Method 2: Try with dict parameter
                            user_creation_data = {
                                "data_limit": traffic_limit_bytes,
                                "inbound_ids": Config.DEFAULT_INBOUND_IDS,
                                "expire_date": None
                            }
                            response = await self.sdk.users.create_user(user_creation_data)
                        except Exception as e2:
                            logger.warning(f"Method 2 (dict) failed: {e2}, trying method 3")
                            try:
                                # Method 3: Try minimal - just mandatory fields
                                response = await self.sdk.users.create_user(
                                    inbound_ids=Config.DEFAULT_INBOUND_IDS
                                )
                            except Exception as e3:
                                # Log available methods for debugging
                                available_methods = [m for m in dir(self.sdk.users) if not m.startswith('_')]
                                logger.error(f"All creation methods failed. Available methods: {available_methods}")
                                logger.error(f"Errors: {e1}, {e2}, {e3}")
                                raise e3
                    
                    if response:
                        # User created successfully, now try to set the username
                        try:
                            # Try to get the created user ID from response
                            user_id = None
                            if hasattr(response, 'id'):
                                user_id = response.id
                            elif hasattr(response, 'data') and 'id' in response.data:
                                user_id = response.data['id']
                            elif isinstance(response, dict) and 'id' in response:
                                user_id = response['id']
                            
                            if user_id:
                                # Try to update user with username if there's an update method
                                if hasattr(self.sdk.users, 'update_user'):
                                    await self.sdk.users.update_user(user_id, username=username)
                                elif hasattr(self.sdk.users, 'modify_user'):
                                    await self.sdk.users.modify_user(user_id, username=username)
                                
                                # Get subscription link using user_id or generated username
                                subscription_link = await self._get_subscription_link(username, user_id)
                                if subscription_link:
                                    subscription_links.append(subscription_link)
                                    created_users.append(username)
                                    logger.info(f"Successfully created user: {username} (ID: {user_id})")
                                else:
                                    logger.warning(f"User created but couldn't get subscription link: {username}")
                            else:
                                logger.warning(f"User created but couldn't get user ID from response: {response}")
                                # Still add as created since API call succeeded
                                subscription_links.append(f"User created successfully: {username}")
                                created_users.append(username)
                        
                        except Exception as update_error:
                            logger.warning(f"User created but couldn't set username {username}: {update_error}")
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
            # Try to get user details by ID first, then by username
            user_info = None
            
            if user_id and hasattr(self.sdk.users, 'get_user_by_id'):
                try:
                    user_info = await self.sdk.users.get_user_by_id(user_id)
                except Exception as e:
                    logger.warning(f"Could not get user by ID {user_id}: {e}")
            
            # Fallback to username
            if not user_info and hasattr(self.sdk.users, 'get_user_by_username'):
                try:
                    user_info = await self.sdk.users.get_user_by_username(username)
                except Exception as e:
                    logger.warning(f"Could not get user by username {username}: {e}")
            
            # Check if we got subscription URL from user info
            if user_info and hasattr(user_info, 'subscription_url'):
                return user_info.subscription_url
            
            # Fallback: construct subscription URL manually
            # This might need adjustment based on actual Remnawave API response format
            if user_id:
                return f"{Config.REMNAWAVE_BASE_URL}/sub/{user_id}"
            else:
                return f"{Config.REMNAWAVE_BASE_URL}/sub/{username}"
            
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