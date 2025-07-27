"""
Utility functions for Remnawave Telegram Bot
"""

import os
import aiofiles
import logging
from datetime import datetime
from typing import List, Optional
from config import Config

logger = logging.getLogger(__name__)

class FileManager:
    """File management utilities"""
    
    def __init__(self):
        # Use the same directory as shown in logs for consistency
        self.files_dir = "/app/temp_files"
        self._ensure_files_directory()
    
    def _ensure_files_directory(self):
        """Ensure the files directory exists with proper permissions"""
        try:
            if not os.path.exists(self.files_dir):
                os.makedirs(self.files_dir, mode=0o755)
                logger.info(f"Created directory: {self.files_dir}")
            else:
                # Try to set permissions on existing directory
                os.chmod(self.files_dir, 0o755)
        except (OSError, PermissionError) as e:
            logger.warning(f"Could not set permissions for {self.files_dir}: {e}")
            # Try alternative directories
            fallback_dirs = [
                "/app/temp_files",  # Docker app directory
                os.path.join(os.getcwd(), "temp_files"),
                "/tmp/promo_files",
                os.path.expanduser("~/promo_files"),
                "./subscription_files"  # Local fallback
            ]
            
            for fallback_dir in fallback_dirs:
                try:
                    os.makedirs(fallback_dir, mode=0o755, exist_ok=True)
                    self.files_dir = fallback_dir
                    logger.info(f"Using fallback directory: {fallback_dir}")
                    break
                except (OSError, PermissionError):
                    continue
            else:
                # Last resort: use current directory
                logger.warning("Using current directory for file storage")
                self.files_dir = os.getcwd()
    
    async def save_subscription_file(self, tag: str, subscription_links: List[str]) -> Optional[str]:
        """
        Save subscription links to a file and return the file path
        
        Args:
            tag: Campaign tag
            subscription_links: List of subscription URLs
            
        Returns:
            File path or None if failed
        """
        try:
            # Ensure directory exists and is writable
            self._ensure_files_directory()
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"promo_{tag}_{timestamp}.txt"
            filepath = os.path.join(self.files_dir, filename)
            
            # Create file content
            content_lines = [
                f"# Promo Campaign: {tag}",
                f"# Created: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                f"# Total subscriptions: {len(subscription_links)}",
                "",
                "# Subscription Links:",
                ""
            ]
            
            content_lines.extend(subscription_links)
            content = "\n".join(content_lines)
            
            # Try to save file with fallback options
            saved = False
            for attempt in range(3):
                try:
                    # Save file asynchronously
                    async with aiofiles.open(filepath, 'w', encoding='utf-8') as f:
                        await f.write(content)
                    
                    # Verify file was actually saved
                    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                        saved = True
                        break
                        
                except (OSError, PermissionError) as e:
                    logger.warning(f"Attempt {attempt + 1} failed to save {filepath}: {e}")
                    
                    # Try alternative filename and directory
                    if attempt == 1:
                        filename = f"promo_{tag}_{timestamp}_alt.txt"
                        filepath = os.path.join("/tmp", filename) if os.access("/tmp", os.W_OK) else os.path.join(os.getcwd(), filename)
                    elif attempt == 2:
                        filename = f"promo_{tag}_{timestamp}_final.txt"
                        filepath = os.path.join(os.getcwd(), filename)
            
            if not saved:
                logger.error(f"Failed to save subscription file after 3 attempts")
                return None
            
            # Return file path for Telegram bot to send as attachment
            logger.info(f"Saved subscription file: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Failed to save subscription file: {str(e)}")
            return None
    
    async def cleanup_old_files(self, days_old: int = 7):
        """Clean up files older than specified days"""
        try:
            cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
            cleaned_count = 0
            
            for filename in os.listdir(self.files_dir):
                filepath = os.path.join(self.files_dir, filename)
                
                if os.path.isfile(filepath):
                    file_time = os.path.getmtime(filepath)
                    
                    if file_time < cutoff_time:
                        os.remove(filepath)
                        cleaned_count += 1
                        logger.info(f"Cleaned up old file: {filename}")
            
            if cleaned_count > 0:
                logger.info(f"Cleaned up {cleaned_count} old files")
                
        except Exception as e:
            logger.error(f"Error during file cleanup: {str(e)}")

def format_bytes(bytes_value: int) -> str:
    """Format bytes to human readable format"""
    if bytes_value == 0:
        return "0 B"
    
    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    value = float(bytes_value)
    
    while value >= 1024 and unit_index < len(units) - 1:
        value /= 1024
        unit_index += 1
    
    if unit_index == 0:
        return f"{int(value)} {units[unit_index]}"
    else:
        return f"{value:.2f} {units[unit_index]}"

def validate_username_format(username: str) -> bool:
    """Validate username format for Remnawave"""
    if not username:
        return False
    
    # Basic validation - adjust based on Remnawave requirements
    if len(username) < 3 or len(username) > 50:
        return False
    
    # Allow alphanumeric, hyphens, underscores
    allowed_chars = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
    return all(c in allowed_chars for c in username)

def get_progress_bar(current: int, total: int, length: int = 10) -> str:
    """Generate a text progress bar"""
    if total == 0:
        return "█" * length
    
    filled_length = int(length * current / total)
    bar = "█" * filled_length + "░" * (length - filled_length)
    percentage = round(100 * current / total, 1)
    
    return f"{bar} {percentage}%"

class ProgressTracker:
    """Track progress for long-running operations"""
    
    def __init__(self, total: int, description: str = "Processing"):
        self.total = total
        self.current = 0
        self.description = description
        self.start_time = datetime.now()
    
    def update(self, increment: int = 1):
        """Update progress"""
        self.current += increment
        if self.current > self.total:
            self.current = self.total
    
    def get_status(self) -> str:
        """Get current status string"""
        progress_bar = get_progress_bar(self.current, self.total)
        elapsed = datetime.now() - self.start_time
        elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
        
        return (
            f"{self.description}\n"
            f"{progress_bar}\n"
            f"Progress: {self.current}/{self.total}\n"
            f"Elapsed: {elapsed_str}"
        )
    
    def is_complete(self) -> bool:
        """Check if progress is complete"""
        return self.current >= self.total