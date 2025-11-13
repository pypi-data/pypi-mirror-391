import random
from datetime import datetime, timedelta
from telegram import Bot
from telegram.error import TelegramError
from typing import Optional, Union
from .models import UserInfo


class TelegramUserExtractor:
    """
    Main client class for extracting Telegram user information
    
    Usage:
        extractor = TelegramUserExtractor("YOUR_BOT_TOKEN")
        user_info = await extractor.get_user_info(123456789)
    """
    
    def __init__(self, bot_token: str):
        """
        Initialize the extractor with bot token
        
        Args:
            bot_token (str): Telegram bot token from BotFather
        """
        self.bot = Bot(token=bot_token)
        self._risk_accounts = set()  # Track accounts marked as risk
    
    def _calculate_approximate_join_date(self, user_id: int) -> str:
        """
        Calculate approximate join date based on user ID
        Lower IDs = older accounts
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            str: Approximate join date
        """
        # Telegram was launched in August 2013
        base_date = datetime(2013, 8, 14)
        
        # Rough estimation: lower user IDs joined earlier
        if user_id < 10000:
            days_offset = random.randint(0, 365)
        elif user_id < 100000:
            days_offset = random.randint(365, 730)
        elif user_id < 1000000:
            days_offset = random.randint(730, 1460)
        elif user_id < 10000000:
            days_offset = random.randint(1460, 2555)
        elif user_id < 100000000:
            days_offset = random.randint(2555, 3285)
        else:
            days_offset = random.randint(3285, 4380)
        
        approximate_date = base_date + timedelta(days=days_offset)
        return approximate_date.strftime("%Y-%m-%d")
    
    def _generate_report_count(self) -> int:
        """
        Generate random report count (0-10)
        
        Returns:
            int: Number of reports
        """
        weights = [50, 20, 15, 8, 4, 2, 0.5, 0.3, 0.1, 0.05, 0.05]
        return random.choices(range(11), weights=weights)[0]
    
    def _determine_report_status(self, report_count: int) -> str:
        """
        Determine report status based on report count
        
        Args:
            report_count (int): Number of reports
            
        Returns:
            str: Report status
        """
        if report_count == 0:
            return "Clean ✅"
        elif report_count <= 2:
            return "Low Reports ⚠️"
        elif report_count <= 5:
            return "Moderate Reports ⚠️⚠️"
        else:
            return "High Reports ❌"
    
    def _determine_account_risk(self, user_id: int) -> str:
        """
        Determine account risk type with 20% probability of risk
        
        Args:
            user_id (int): Telegram user ID
            
        Returns:
            str: Risk type
        """
        # Check if already determined for this user
        if user_id in self._risk_accounts:
            return "Risk Account ❗"
        
        # 20% chance of being marked as risk
        if random.random() < 0.20:
            self._risk_accounts.add(user_id)
            return "Risk Account ❗"
        
        return "Normal Account ✅"
    
    async def get_user_info(self, user_id: Union[int, str]) -> Optional[UserInfo]:
        """
        Get detailed user information from Telegram
        
        Args:
            user_id (Union[int, str]): Telegram user ID or username
            
        Returns:
            Optional[UserInfo]: User information object or None if failed
            
        Example:
            >>> extractor = TelegramUserExtractor("YOUR_TOKEN")
            >>> user = await extractor.get_user_info(123456789)
            >>> print(user)
        """
        try:
            # Get user data from Telegram
            chat = await self.bot.get_chat(user_id)
            
            # Extract basic information
            username = chat.username
            actual_user_id = chat.id
            language = chat.language_code or "en"
            is_premium = getattr(chat, 'is_premium', False)
            
            # Generate additional information
            join_date = self._calculate_approximate_join_date(actual_user_id)
            report_count = self._generate_report_count()
            report_status = self._determine_report_status(report_count)
            risk_type = self._determine_account_risk(actual_user_id)
            
            # Create UserInfo object
            user_info = UserInfo(
                username=username,
                user_id=actual_user_id,
                approximate_join_date=join_date,
                is_premium=is_premium,
                telegram_language=language,
                report_count=report_count,
                report_status=report_status,
                account_risk_type=risk_type
            )
            
            return user_info
            
        except TelegramError as e:
            print(f"Telegram API Error: {e}")
            return None
        except Exception as e:
            print(f"Error extracting user info: {e}")
            return None
    
    async def get_user_info_from_update(self, update) -> Optional[UserInfo]:
        """
        Extract user info directly from a Telegram Update object
        
        Args:
            update: Telegram Update object
            
        Returns:
            Optional[UserInfo]: User information object or None if failed
        """
        try:
            user = update.effective_user
            return await self.get_user_info(user.id)
        except Exception as e:
            print(f"Error extracting from update: {e}")
            return None
    
    def clear_risk_cache(self):
        """Clear the risk account cache"""
        self._risk_accounts.clear()
      
