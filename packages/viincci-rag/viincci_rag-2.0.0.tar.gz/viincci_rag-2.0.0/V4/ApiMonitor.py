"""
ApiMonitor.py - Research V4
Monitor SerpAPI usage and credits with alerts
"""

import requests
import logging
from typing import Dict, Optional
from datetime import datetime

try:
    from .ConfigManager import ConfigManager
except ImportError:
    from FlaskApp.services.v4.ConfigManager import ConfigManager

logger = logging.getLogger(__name__)


class SerpAPIMonitor:
    """Monitor SerpAPI account usage and credits"""
    
    def __init__(self, config: ConfigManager = None):
        """Initialize API monitor with configuration."""
        if config is None:
            config = ConfigManager()
        
        self.config = config
        self.api_key = config.get_api_key()
        self.account_url = "https://serpapi.com/account"
        self.timeout = config.get_request_timeout()
        
        # Alert thresholds from config
        self.warning_threshold = config.get_api_warning_threshold()
        self.critical_threshold = config.get_api_critical_threshold()
        
    def get_account_info(self) -> Optional[Dict]:
        """
        Fetch account information from SerpAPI.
        
        Returns:
            Dictionary with account info or None if error
        """
        try:
            params = {"api_key": self.api_key}
            response = requests.get(
                self.account_url, 
                params=params, 
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            logger.info("Successfully retrieved SerpAPI account info")
            return data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching SerpAPI account info: {e}")
            return None
    
    def check_credits(self, verbose: bool = True) -> Dict:
        """
        Check current credit status with threshold alerts.
        
        Args:
            verbose: Print status to console
            
        Returns:
            Dictionary with credit status and alerts
        """
        account_info = self.get_account_info()
        
        if not account_info:
            return {
                "status": "error",
                "message": "Failed to retrieve account information",
                "can_proceed": False,
                "searches_remaining": 0,
                "searches_used": 0,
                "plan_searches": 0,
                "usage_percent": 0,
                "account_email": "Unknown",
                "plan_name": "Unknown",
                "checked_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        
        # Extract credit information
        searches_remaining = account_info.get("total_searches_left", 0)
        plan_searches = account_info.get("plan_searches_per_month", 0)
        searches_used = plan_searches - searches_remaining
        
        usage_percent = (searches_used / plan_searches * 100) if plan_searches > 0 else 0
        
        # Determine status
        if searches_remaining <= self.critical_threshold:
            status = "critical"
            alert_level = "🔴 CRITICAL"
            can_proceed = False
            message = f"Only {searches_remaining} searches remaining! Research halted."
        elif searches_remaining <= self.warning_threshold:
            status = "warning"
            alert_level = "🟡 WARNING"
            can_proceed = True
            message = f"Low on searches: {searches_remaining} remaining"
        else:
            status = "ok"
            alert_level = "🟢 OK"
            can_proceed = True
            message = f"Sufficient searches available: {searches_remaining} remaining"
        
        result = {
            "status": status,
            "alert_level": alert_level,
            "can_proceed": can_proceed,
            "message": message,
            "searches_remaining": searches_remaining,
            "searches_used": searches_used,
            "plan_searches": plan_searches,
            "usage_percent": usage_percent,
            "account_email": account_info.get("account_email", "Unknown"),
            "plan_name": account_info.get("plan_name", "Unknown"),
            "checked_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if verbose:
            self.print_status(result)
        
        return result
    
    def print_status(self, status: Dict):
        """Print formatted credit status."""
        print("\n" + "="*70)
        print(f"📊 SerpAPI Account Status - {status['checked_at']}")
        print("="*70)
        print(f"Account: {status.get('account_email', 'Unknown')}")
        print(f"Plan: {status.get('plan_name', 'Unknown')}")
        print()
        print(f"Status: {status['alert_level']}")
        print(f"Message: {status['message']}")
        print()
        print(f"📊 Usage Statistics:")
        print(f"  • Searches Used: {status['searches_used']:,}")
        print(f"  • Searches Remaining: {status['searches_remaining']:,}")
        print(f"  • Plan Limit: {status['plan_searches']:,}")
        print(f"  • Usage: {status['usage_percent']:.1f}%")
        print()
        
        if not status['can_proceed']:
            print("⚠️  RESEARCH OPERATIONS BLOCKED - INSUFFICIENT CREDITS")
            print("   Please upgrade your plan or wait for monthly reset")
        elif status['status'] == 'warning':
            print("⚠️  Consider upgrading your plan soon")
        
        print("="*70 + "\n")
    
    def can_perform_search(self, required_searches: int = 1) -> tuple[bool, str]:
        """
        Check if enough searches are available for operation.
        
        Args:
            required_searches: Number of searches needed
            
        Returns:
            Tuple of (can_proceed: bool, message: str)
        """
        status = self.check_credits(verbose=False)
        
        if not status['can_proceed']:
            return False, f"Insufficient credits: {status['message']}"
        
        if status['searches_remaining'] < required_searches:
            return False, f"Need {required_searches} searches but only {status['searches_remaining']} remaining"
        
        return True, f"Can proceed: {status['searches_remaining']} searches available"
    
    def estimate_research_cost(self, plant_name: str = None, questions: int = 4) -> Dict:
        """
        Estimate search cost for a research operation.
        
        Args:
            plant_name: Plant name for research (optional)
            questions: Number of AI questions to ask
            
        Returns:
            Dictionary with cost estimate
        """
        # Each research typically uses:
        # - 3 SerpAPI searches (SA academic, SA general, international)
        # - N questions to Google AI Mode (each is 1 search)
        
        web_searches = 3
        ai_searches = questions
        total_searches = web_searches + ai_searches
        
        status = self.check_credits(verbose=False)
        
        # Safely access searches_remaining with default value
        searches_remaining = status.get('searches_remaining', 0)
        
        can_afford = searches_remaining >= total_searches
        remaining_after = searches_remaining - total_searches if can_afford else 0
        
        estimate = {
            "plant_name": plant_name or "Unknown",
            "web_searches": web_searches,
            "ai_questions": ai_searches,
            "total_searches_needed": total_searches,
            "searches_available": searches_remaining,
            "can_afford": can_afford,
            "remaining_after_operation": remaining_after,
            "estimated_operations_remaining": searches_remaining // total_searches if total_searches > 0 else 0
        }
        
        return estimate
    
    def print_estimate(self, estimate: Dict):
        """Print research cost estimate."""
        print("\n" + "="*70)
        print(f"💰 Research Cost Estimate: {estimate['plant_name']}")
        print("="*70)
        print(f"Web Searches: {estimate['web_searches']}")
        print(f"AI Questions: {estimate['ai_questions']}")
        print(f"Total Searches Needed: {estimate['total_searches_needed']}")
        print()
        print(f"Searches Available: {estimate['searches_available']:,}")
        print(f"Remaining After: {estimate['remaining_after_operation']:,}")
        print(f"Estimated Operations Remaining: {estimate['estimated_operations_remaining']}")
        print()
        
        if estimate['can_afford']:
            print("✅ Sufficient credits to proceed")
        else:
            print("❌ Insufficient credits for this operation")
        
        print("="*70 + "\n")


# Convenience functions
def check_api_credits(config: ConfigManager = None) -> Dict:
    """Quick function to check API credits."""
    monitor = SerpAPIMonitor(config)
    return monitor.check_credits()


def can_start_research(plant_name: str = None, config: ConfigManager = None) -> bool:
    """Check if research can start with current credits."""
    monitor = SerpAPIMonitor(config)
    estimate = monitor.estimate_research_cost(plant_name)
    monitor.print_estimate(estimate)
    return estimate['can_afford']


if __name__ == "__main__":
    # Example usage
    print("\n📊 SerpAPI Credit Monitor Demo\n")
    
    config = ConfigManager(verbose=False)
    monitor = SerpAPIMonitor(config)
    
    # Check current status
    status = monitor.check_credits()
    
    # Estimate cost for research
    estimate = monitor.estimate_research_cost("Rosa rubiginosa", questions=4)
    monitor.print_estimate(estimate)
    
    # Check if we can proceed
    can_proceed, message = monitor.can_perform_search(required_searches=7)
    print(f"Can proceed with research: {can_proceed}")
    print(f"Message: {message}")