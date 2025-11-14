import time
from datetime import datetime
import json
import os

class FocusBlocker:
    """
    A simple focus blocker that manages distracting websites
    """
    
    def __init__(self, blocked_sites=None):
        self.blocked_sites = blocked_sites or [
            "facebook.com",
            "youtube.com", 
            "twitter.com",
            "instagram.com",
            "reddit.com",
            "netflix.com"
        ]
        self.focus_hours = {"start": 9, "end": 17}  # 9 AM to 5 PM
    
    def add_site(self, site):
        """Add a website to blocked list"""
        if site not in self.blocked_sites:
            self.blocked_sites.append(site)
            return f"Added {site} to blocked list"
        return f"{site} is already blocked"
    
    def remove_site(self, site):
        """Remove a website from blocked list"""
        if site in self.blocked_sites:
            self.blocked_sites.remove(site)
            return f"Removed {site} from blocked list"
        return f"{site} is not in blocked list"
    
    def is_blocked(self, url):
        """Check if a URL should be blocked"""
        if not self.is_focus_time():
            return False
        
        url_lower = url.lower()
        return any(site in url_lower for site in self.blocked_sites)
    
    def is_focus_time(self):
        """Check if current time is within focus hours"""
        now = datetime.now()
        current_hour = now.hour
        return self.focus_hours["start"] <= current_hour < self.focus_hours["end"]
    
    def set_focus_hours(self, start_hour, end_hour):
        """Set custom focus hours"""
        self.focus_hours = {"start": start_hour, "end": end_hour}
        return f"Focus hours set to {start_hour}:00 - {end_hour}:00"
    
    def get_status(self):
        """Get current blocker status"""
        return {
            "blocked_sites": self.blocked_sites,
            "focus_hours": self.focus_hours,
            "is_focus_time": self.is_focus_time(),
            "current_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }


def schedule_focus_hours(start_hour=9, end_hour=17, sites=None):
    """
    Convenience function to create a FocusBlocker with custom settings
    """
    blocker = FocusBlocker(sites)
    blocker.set_focus_hours(start_hour, end_hour)
    return blocker


# Demo function
def demo():
    """Run a demo of the focus blocker"""
    print("🚀 Demo Focus Blocker")
    print("=" * 40)
    
    blocker = FocusBlocker()
    
    # Show initial status
    status = blocker.get_status()
    print(f"Current time: {status['current_time']}")
    print(f"Focus time: {status['is_focus_time']}")
    print(f"Focus hours: {status['focus_hours']['start']}:00 - {status['focus_hours']['end']}:00")
    print(f"Blocked sites: {', '.join(status['blocked_sites'])}")
    print()
    
    # Test some URLs
    test_urls = [
        "https://www.youtube.com/watch?v=abc123",
        "https://github.com/python",
        "https://www.facebook.com/profile.php",
        "https://stackoverflow.com/questions",
        "https://www.netflix.com/watch/123"
    ]
    
    print("URL Blocking Test:")
    print("-" * 40)
    for url in test_urls:
        blocked = blocker.is_blocked(url)
        status = "🚫 BLOCKED" if blocked else "✅ ALLOWED"
        print(f"{status}: {url}")
    
    return blocker


if __name__ == "__main__":
    demo()
