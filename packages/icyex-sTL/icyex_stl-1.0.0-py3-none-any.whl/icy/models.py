from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class UserInfo:
    """
    Data model for Telegram user information
    """
    username: Optional[str]
    user_id: int
    approximate_join_date: str
    is_premium: bool
    telegram_language: str
    report_count: int
    report_status: str
    account_risk_type: str
    
    def to_dict(self):
        """Convert UserInfo to dictionary"""
        return {
            "username": self.username,
            "user_id": self.user_id,
            "approximate_join_date": self.approximate_join_date,
            "is_premium": self.is_premium,
            "telegram_language": self.telegram_language,
            "report_count": self.report_count,
            "report_status": self.report_status,
            "account_risk_type": self.account_risk_type
        }
    
    def __str__(self):
        """String representation of user info"""
        return f"""
╔══════════════════════════════════════╗
║     TELEGRAM USER INFORMATION        ║
╠══════════════════════════════════════╣
║ Username: {self.username or 'N/A'}
║ User ID: {self.user_id}
║ Join Date: {self.approximate_join_date}
║ Premium: {self.is_premium}
║ Language: {self.telegram_language}
║ Report Count: {self.report_count}
║ Report Status: {self.report_status}
║ Risk Type: {self.account_risk_type}
╚══════════════════════════════════════╝
        """

