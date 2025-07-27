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
    
    def _extract_users_from_response(self, users_response) -> list:
        """Extract users list from API response handling different response structures"""
        if not users_response:
            return []
            
        # Handle API response structure: response.users[]
        users_list = []
        if hasattr(users_response, 'response') and hasattr(users_response.response, 'users'):
            users_list = users_response.response.users
        elif hasattr(users_response, 'users'):
            users_list = users_response.users
        elif isinstance(users_response, dict):
            if 'response' in users_response and 'users' in users_response['response']:
                users_list = users_response['response']['users']
            elif 'users' in users_response:
                users_list = users_response['users']
        
        return users_list or []
    
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
            
            # Convert GB to bytes (ensure we don't set 0 which means unlimited)
            if traffic_limit_gb <= 0:
                traffic_limit_bytes = 1024 * 1024 * 1024  # 1GB minimum if 0 or negative
                logger.warning(f"Traffic limit was {traffic_limit_gb}GB, setting to 1GB minimum")
            else:
                traffic_limit_bytes = traffic_limit_gb * 1024 * 1024 * 1024
            
            logger.info(f"Setting traffic limit: {traffic_limit_gb}GB = {traffic_limit_bytes} bytes")
            
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
                    
                    # Based on SDK source code analysis: create_user expects a Pydantic body
                    # Method signature: create_user(body: CreateUserRequestDto) -> UserResponseDto
                    
                    from remnawave_api.models import CreateUserRequestDto
                    from remnawave_api.enums import UserStatus, TrafficLimitStrategy
                    
                    # Create the request DTO with proper structure
                    try:
                        # Create Pydantic model instance with all required fields based on actual model structure
                        create_request = CreateUserRequestDto(
                            username=username,
                            expire_at=expire_at_iso,  # Required field
                            traffic_limit_bytes=traffic_limit_bytes,  # Traffic limit in bytes (not 0 = unlimited)
                            traffic_limit_strategy=TrafficLimitStrategy.NO_RESET,  # Optional enum
                            activate_all_inbounds=True,  # Optional 
                            status=UserStatus.ACTIVE,  # Optional enum
                            tag=tag  # Tag for user categorization
                        )
                        
                        logger.info(f"Creating user {username} with tag='{tag}', traffic_limit={traffic_limit_bytes} bytes")
                        
                        response = await self.sdk.users.create_user(body=create_request)
                        logger.info(f"User creation succeeded with full parameters")
                        
                    except Exception as e1:
                        logger.warning(f"Full parameters failed: {e1}, trying minimal")
                        
                        try:
                            # Try with only required fields
                            create_request = CreateUserRequestDto(
                                username=username,
                                expire_at=expire_at_iso,  # Required field
                                tag=tag  # Always include tag
                            )
                            
                            logger.info(f"Fallback: Creating user {username} with minimal fields, tag='{tag}'")
                            
                            response = await self.sdk.users.create_user(body=create_request)
                            logger.info(f"User creation succeeded with minimal parameters")
                            
                        except Exception as e2:
                            logger.error(f"All creation attempts failed: {e1}, {e2}")
                            
                            # Log available methods for debugging
                            available_methods = [m for m in dir(self.sdk.users) if not m.startswith('_')]
                            logger.error(f"Available methods: {available_methods}")
                            
                            # Try to find the correct method signature
                            try:
                                import inspect
                                sig = inspect.signature(self.sdk.users.create_user)
                                logger.error(f"create_user signature: {sig}")
                            except:
                                pass
                                
                            raise e2
                    
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
                            
                            # Always get real subscription URL via separate API call using shortUuid
                            real_subscription_url = await self._get_real_subscription_url(username, user_id, response)
                            if real_subscription_url:
                                subscription_links.append(real_subscription_url)
                                created_users.append(username)
                                logger.info(f"Successfully created user: {username} with real subscription URL")
                            else:
                                logger.warning(f"User created but couldn't get real subscription URL: {username}")
                                # Still add as created since user was created
                                subscription_links.append(f"User created: {username} (no subscription URL)")
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
    
    async def _get_real_subscription_url(self, username: str, user_id: str = None, user_response = None) -> Optional[str]:
        """Get real subscription URL using subscription info API"""
        try:
            # Extract shortUuid from user response
            short_uuid = None
            
            if user_response:
                if hasattr(user_response, 'response'):
                    resp_data = user_response.response
                    if hasattr(resp_data, 'short_uuid'):
                        short_uuid = resp_data.short_uuid
                    elif hasattr(resp_data, 'shortUuid'):
                        short_uuid = resp_data.shortUuid
                elif hasattr(user_response, 'short_uuid'):
                    short_uuid = user_response.short_uuid
                elif hasattr(user_response, 'shortUuid'):
                    short_uuid = user_response.shortUuid
                elif isinstance(user_response, dict):
                    if 'response' in user_response:
                        resp_data = user_response['response']
                        short_uuid = resp_data.get('short_uuid') or resp_data.get('shortUuid')
                    else:
                        short_uuid = user_response.get('short_uuid') or user_response.get('shortUuid')
            
            if not short_uuid:
                logger.warning(f"Could not extract shortUuid for user {username}")
                return None
            
            # Get subscription info using user UUID (not shortUuid)
            # First try to get user by UUID to get full user data
            if user_id:
                try:
                    user_data = await self.sdk.users.get_user_by_uuid(user_id)
                    if user_data:
                        # Extract subscription URL from user data
                        subscription_url = None
                        
                        if hasattr(user_data, 'response'):
                            resp_data = user_data.response
                            if hasattr(resp_data, 'subscription_url'):
                                subscription_url = resp_data.subscription_url
                            elif hasattr(resp_data, 'subscriptionUrl'):
                                subscription_url = resp_data.subscriptionUrl
                        elif hasattr(user_data, 'subscription_url'):
                            subscription_url = user_data.subscription_url
                        elif hasattr(user_data, 'subscriptionUrl'):
                            subscription_url = user_data.subscriptionUrl
                        elif isinstance(user_data, dict):
                            if 'response' in user_data:
                                resp_data = user_data['response']
                                subscription_url = resp_data.get('subscription_url') or resp_data.get('subscriptionUrl')
                            else:
                                subscription_url = user_data.get('subscription_url') or user_data.get('subscriptionUrl')
                        
                        if subscription_url:
                            logger.info(f"Got subscription URL from API for {username}: {subscription_url}")
                            return subscription_url
                            
                except Exception as e:
                    logger.warning(f"Failed to get user data by UUID {user_id}: {e}")
            
            # Try by shortUuid if available
            if short_uuid:
                try:
                    user_data = await self.sdk.users.get_user_by_short_uuid(short_uuid)
                    if user_data:
                        # Extract subscription URL from user data
                        subscription_url = None
                        
                        if hasattr(user_data, 'response'):
                            resp_data = user_data.response
                            if hasattr(resp_data, 'subscription_url'):
                                subscription_url = resp_data.subscription_url
                            elif hasattr(resp_data, 'subscriptionUrl'):
                                subscription_url = resp_data.subscriptionUrl
                        elif hasattr(user_data, 'subscription_url'):
                            subscription_url = user_data.subscription_url
                        elif hasattr(user_data, 'subscriptionUrl'):
                            subscription_url = user_data.subscriptionUrl
                        elif isinstance(user_data, dict):
                            if 'response' in user_data:
                                resp_data = user_data['response']
                                subscription_url = resp_data.get('subscription_url') or resp_data.get('subscriptionUrl')
                            else:
                                subscription_url = user_data.get('subscription_url') or user_data.get('subscriptionUrl')
                        
                        if subscription_url:
                            logger.info(f"Got subscription URL from API by shortUuid for {username}: {subscription_url}")
                            return subscription_url
                            
                except Exception as e:
                    logger.warning(f"Failed to get user data by shortUuid {short_uuid}: {e}")
            
            logger.warning(f"Could not get subscription URL from API for user {username}")
            return None
            
        except Exception as e:
            logger.error(f"Failed to get real subscription URL for {username}: {str(e)}")
            return None
    
    async def _get_subscription_link(self, username: str, user_id: str = None) -> Optional[str]:
        """Get subscription link for user"""
        try:
            # Try to get user details by various methods
            user_info = None
            
            # Try by UUID first if available (GET /api/users/{uuid})
            if user_id:
                for method_name in ['get_user_by_uuid', 'get_user_by_id', 'get_user']:
                    if hasattr(self.sdk.users, method_name):
                        try:
                            method = getattr(self.sdk.users, method_name)
                            user_info = await method(user_id)
                            logger.debug(f"Got user info using {method_name} for UUID {user_id}")
                            break
                        except Exception as e:
                            logger.debug(f"Method {method_name} failed for UUID {user_id}: {e}")
            
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
            
            # Extract subscription URL from user info based on API documentation
            if user_info:
                # Handle nested response structure (response.response.subscriptionUrl)
                if hasattr(user_info, 'response'):
                    resp_data = user_info.response
                    if hasattr(resp_data, 'subscriptionUrl') and resp_data.subscriptionUrl:
                        logger.debug(f"Found subscriptionUrl in response.response")
                        return resp_data.subscriptionUrl
                
                # Handle direct subscriptionUrl field
                if hasattr(user_info, 'subscriptionUrl') and user_info.subscriptionUrl:
                    logger.debug(f"Found subscriptionUrl in direct response")
                    return user_info.subscriptionUrl
                
                # If user_info is a dict, handle nested structure
                if isinstance(user_info, dict):
                    # Check for nested response structure
                    if 'response' in user_info and isinstance(user_info['response'], dict):
                        subscription_url = user_info['response'].get('subscriptionUrl')
                        if subscription_url:
                            logger.debug(f"Found subscriptionUrl in dict response.response")
                            return subscription_url
                    
                    # Check for direct subscriptionUrl
                    subscription_url = user_info.get('subscriptionUrl')
                    if subscription_url:
                        logger.debug(f"Found subscriptionUrl in dict response")
                        return subscription_url
                    
                    # Fallback to other possible field names for backward compatibility
                    for field_name in ['subscription_url', 'sub_url', 'link', 'config_url']:
                        if field_name in user_info and user_info[field_name]:
                            logger.debug(f"Found subscription URL in fallback field {field_name}")
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
            
            # Extract users from API response
            users_list = self._extract_users_from_response(users_response)
            if not users_list:
                return []
            
            # Group users by tag
            tag_stats = {}
            
            for user in users_list:
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
                        
                        # Check if user is active based on API documentation fields
                        status = getattr(user, 'status', 'ACTIVE')
                        used_traffic = getattr(user, 'usedTrafficBytes', 0)
                        traffic_limit = getattr(user, 'trafficLimitBytes', 0)
                        
                        # User is active if status is ACTIVE and has remaining traffic
                        if status == 'ACTIVE':
                            if traffic_limit == 0 or used_traffic < traffic_limit:  # 0 means unlimited
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
            
            # Extract users from API response
            users_list = self._extract_users_from_response(users_response)
            if not users_list:
                return 0, 0
            
            tag_users = []
            deleted_count = 0
            
            # Find users with the specified tag
            for user in users_list:
                username = getattr(user, 'username', '')
                
                if username.startswith(Config.DEFAULT_UUID_PREFIX):
                    parts = username.split('-')
                    if len(parts) >= 3:
                        user_tag = '-'.join(parts[2:])
                        
                        if user_tag == tag:
                            tag_users.append(user)
                            
                            # Check if user is "used" based on API documentation fields
                            status = getattr(user, 'status', 'ACTIVE')
                            used_traffic = getattr(user, 'usedTrafficBytes', 0)
                            traffic_limit = getattr(user, 'trafficLimitBytes', 0)
                            user_uuid = getattr(user, 'uuid', None)
                            
                            # User is considered "used" if not ACTIVE or traffic limit exceeded
                            is_used = (status != 'ACTIVE' or 
                                     (traffic_limit > 0 and used_traffic >= traffic_limit))
                            
                            if is_used and user_uuid:
                                # Delete used subscription
                                try:
                                    await self.sdk.users.delete_user(user_uuid)
                                    deleted_count += 1
                                    logger.info(f"Deleted used subscription: {username} (UUID: {user_uuid})")
                                except Exception as e:
                                    logger.error(f"Failed to delete user {username} (UUID: {user_uuid}): {str(e)}")
                            elif is_used and not user_uuid:
                                logger.warning(f"Cannot delete user {username}: no UUID found")
            
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
            
            # Extract users from API response
            users_list = self._extract_users_from_response(users_response)
            if not users_list:
                return {'total': 0, 'active': 0, 'used': 0}
            
            stats = {'total': 0, 'active': 0, 'used': 0}
            
            for user in users_list:
                username = getattr(user, 'username', '')
                
                if username.startswith(Config.DEFAULT_UUID_PREFIX):
                    parts = username.split('-')
                    if len(parts) >= 3:
                        user_tag = '-'.join(parts[2:])
                        
                        if user_tag == tag:
                            stats['total'] += 1
                            
                            # Use correct API field names
                            status = getattr(user, 'status', 'ACTIVE')
                            used_traffic = getattr(user, 'usedTrafficBytes', 0)
                            traffic_limit = getattr(user, 'trafficLimitBytes', 0)
                            
                            # Check if user is "used" based on status and traffic
                            is_used = (status != 'ACTIVE' or 
                                     (traffic_limit > 0 and used_traffic >= traffic_limit))
                            
                            if is_used:
                                stats['used'] += 1
                            else:
                                stats['active'] += 1
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting tag preview stats: {str(e)}")
            return {'total': 0, 'active': 0, 'used': 0}